"""
Output serializers for pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

from typing import Any, Iterator, Dict, List
import json
import csv
import io
from .core import OutputSerializer


class ListSerializer(OutputSerializer):
    """Serializer for list output."""
    
    def can_serialize(self, format_name: str) -> bool:
        return format_name.lower() in ['list', 'array']
    
    def serialize(self, data: Iterator[Dict[str, Any]], format_name: str) -> List[Dict[str, Any]]:
        return list(data)


class JSONSerializer(OutputSerializer):
    """Serializer for JSON output."""
    
    def can_serialize(self, format_name: str) -> bool:
        return format_name.lower() in ['json']
    
    def serialize(self, data: Iterator[Dict[str, Any]], format_name: str) -> str:
        items = list(data)
        return json.dumps(items, indent=2)


class CSVSerializer(OutputSerializer):
    """Serializer for CSV output."""
    
    def can_serialize(self, format_name: str) -> bool:
        return format_name.lower() in ['csv']
    
    def serialize(self, data: Iterator[Dict[str, Any]], format_name: str) -> str:
        items = list(data)
        if not items:
            return ""
        
        # Get all unique field names
        fieldnames = set()
        for item in items:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
        return output.getvalue()


# Register output serializers
from .registry import registry

registry.register_output_serializer(ListSerializer)
registry.register_output_serializer(JSONSerializer)
registry.register_output_serializer(CSVSerializer)