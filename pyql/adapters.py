"""
Built-in adapters for pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

from typing import Any, Iterator, Dict, List, Union
from pathlib import Path
import json
import csv
import os
from .core import DataSource, DataAdapter
from .registry import registry


class ListOfDictsDataSource(DataSource):
    """DataSource for a list of dictionaries."""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self._data = data
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        yield from self._data


class ListOfDictsAdapter(DataAdapter):
    """Adapter for lists of dictionaries."""
    
    def can_handle(self, data: Any) -> bool:
        return (isinstance(data, list) and 
                len(data) > 0 and 
                all(isinstance(item, dict) for item in data))
    
    def adapt(self, data: Any) -> DataSource:
        return ListOfDictsDataSource(data)


class ListOfPrimitivesDataSource(DataSource):
    """DataSource for a list of primitive values."""
    
    def __init__(self, data: List[Any]):
        self._data = data
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        for item in self._data:
            yield {"value": item}


class ListOfPrimitivesAdapter(DataAdapter):
    """Adapter for lists of primitive values."""
    
    def can_handle(self, data: Any) -> bool:
        return (isinstance(data, list) and 
                len(data) > 0 and 
                all(not isinstance(item, (dict, list, tuple)) for item in data))
    
    def adapt(self, data: Any) -> DataSource:
        return ListOfPrimitivesDataSource(data)


class ListOfListsDataSource(DataSource):
    """DataSource for a list of lists (with or without headers)."""
    
    def __init__(self, data: List[List[Any]]):
        self._data = data
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        if not self._data:
            return
        
        first_row = self._data[0]
        # Check if first row looks like headers (all strings and unique)
        likely_headers = (all(isinstance(item, str) for item in first_row) and 
                         len(set(first_row)) == len(first_row))
        
        if likely_headers:
            # Use first row as headers
            headers = [str(item).strip() for item in first_row]
            for row in self._data[1:]:
                yield {headers[i] if i < len(headers) else f"_{i}": 
                       row[i] if i < len(row) else None 
                       for i in range(max(len(headers), len(row)))}
        else:
            # No headers, use synthetic keys
            headers = [f"_{i}" for i in range(len(first_row))]
            for row in self._data:
                yield {headers[i] if i < len(headers) else f"_{i}": 
                       row[i] if i < len(row) else None 
                       for i in range(len(headers))}


class ListOfListsAdapter(DataAdapter):
    """Adapter for lists of lists."""
    
    def can_handle(self, data: Any) -> bool:
        return (isinstance(data, list) and 
                len(data) > 0 and 
                all(isinstance(item, (list, tuple)) for item in data))
    
    def adapt(self, data: Any) -> DataSource:
        return ListOfListsDataSource(data)


class DictDataSource(DataSource):
    """DataSource for a single dictionary."""
    
    def __init__(self, data: Dict[str, Any]):
        self._data = [data]
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        yield from self._data


class DictAdapter(DataAdapter):
    """Adapter for a single dictionary."""
    
    def can_handle(self, data: Any) -> bool:
        return isinstance(data, dict)
    
    def adapt(self, data: Any) -> DataSource:
        return DictDataSource(data)


class SingleValueDataSource(DataSource):
    """DataSource for a single non-structured value."""
    
    def __init__(self, data: Any):
        self._data = [{"_value": data}]
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        yield from self._data


class SingleValueAdapter(DataAdapter):
    """Adapter for single values."""
    
    def can_handle(self, data: Any) -> bool:
        return not isinstance(data, (list, dict))
    
    def adapt(self, data: Any) -> DataSource:
        return SingleValueDataSource(data)


class CSVFileDataSource(DataSource):
    """DataSource for CSV files."""
    
    def __init__(self, file_path: str):
        self._file_path = file_path
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        with open(self._file_path, 'r', newline='') as csvfile:
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.reader(csvfile, delimiter=delimiter)
            first_row = next(reader, None)
            
            if first_row is None:
                return
            
            # Check if first row looks like headers
            likely_headers = all(isinstance(cell, str) and cell.strip() != '' for cell in first_row)
            
            if likely_headers:
                # Use first row as headers
                headers = [str(cell).strip() for cell in first_row]
                for row in reader:
                    yield {headers[i] if i < len(headers) else f"_{i}": 
                           row[i] if i < len(row) else None 
                           for i in range(max(len(headers), len(row)))}
            else:
                # No headers, use synthetic keys
                headers = [f"_{i}" for i in range(len(first_row))]
                # Process the first row we already read
                yield {headers[i]: first_row[i] if i < len(first_row) else None 
                       for i in range(len(headers))}
                # Process remaining rows
                for row in reader:
                    yield {headers[i]: row[i] if i < len(row) else None 
                           for i in range(len(headers))}


class CSVFileAdapter(DataAdapter):
    """Adapter for CSV files."""
    
    def can_handle(self, data: Any) -> bool:
        return (isinstance(data, str) and 
                os.path.exists(data) and 
                Path(data).suffix.lower() == '.csv')
    
    def adapt(self, data: Any) -> DataSource:
        return CSVFileDataSource(data)


class JSONFileDataSource(DataSource):
    """DataSource for JSON files."""
    
    def __init__(self, file_path: str):
        self._file_path = file_path
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        with open(self._file_path, 'r') as f:
            content = f.read().strip()
            
            # Check if it's a JSON array
            if content.startswith('['):
                data = json.loads(content)
                for item in data:
                    if isinstance(item, dict):
                        yield item
                    else:
                        yield {"_value": item}
            else:
                # JSON lines or single JSON object
                f.seek(0)
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            item = json.loads(line)
                            if isinstance(item, dict):
                                yield item
                            else:
                                yield {"_value": item}
                        except json.JSONDecodeError:
                            continue


class JSONFileAdapter(DataAdapter):
    """Adapter for JSON files."""
    
    def can_handle(self, data: Any) -> bool:
        return (isinstance(data, str) and 
                os.path.exists(data) and 
                Path(data).suffix.lower() in ['.json', '.jsonl'])
    
    def adapt(self, data: Any) -> DataSource:
        return JSONFileDataSource(data)


# Register built-in adapters
registry.register_data_adapter(ListOfDictsAdapter)
registry.register_data_adapter(ListOfPrimitivesAdapter)
registry.register_data_adapter(ListOfListsAdapter)
registry.register_data_adapter(DictAdapter)
# Register file adapters BEFORE SingleValueAdapter
registry.register_data_adapter(CSVFileAdapter)
registry.register_data_adapter(JSONFileAdapter)
registry.register_data_adapter(SingleValueAdapter)