"""
pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

from typing import Any, Callable, List, Union, Iterator, Dict
from functools import reduce
from collections import defaultdict
import csv
import json
import io
from .core import DataSource
from .registry import registry


class Queryable:
    """A lazy, chainable interface for querying data."""
    
    def __init__(self, data: Any):
        """Initialize with data to query. Uses adapters to normalize data to DataSource."""
        # Find appropriate adapter and convert data to DataSource
        adapter = registry.get_data_adapter(data)
        if adapter is None:
            # If no adapter found, treat as a list of primitives
            # If no adapter found, treat as a list of primitives
            if isinstance(data, list) and len(data) > 0 and all(not isinstance(item, (dict, list)) for item in data):
                from .adapters import ListOfPrimitivesDataSource
                self._data_source = ListOfPrimitivesDataSource(data)
            elif isinstance(data, list) and len(data) > 0 and all(isinstance(item, dict) for item in data):
                from .adapters import ListOfDictsDataSource
                self._data_source = ListOfDictsDataSource(data)
            else:
                # Default to single value
                from .adapters import SingleValueDataSource
                self._data_source = SingleValueDataSource(data)
        else:
            self._data_source = adapter.adapt(data)
        
        self._operations = []
    
    def filter(self, predicate: Callable) -> 'Queryable':
        """Filter elements based on a predicate function."""
        def operation(data):
            def safe_predicate(item):
                try:
                    return predicate(item)
                except Exception:
                    return False
            
            return (item for item in data if safe_predicate(item))
        
        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def where(self, field, condition=None, value=None) -> 'Queryable':
        """Simple filter for common use cases with intuitive syntax.
        
        Usage:
        - where(lambda x: condition) - Custom condition (same as filter)
        - where("field", "gt", value) - Field greater than value
        - where("field", "lt", value) - Field less than value
        - where("field", "eq", value) - Field equals value
        - where("field", "ne", value) - Field not equals value
        - where("field", "ge", value) - Field greater than or equal to value
        - where("field", "le", value) - Field less than or equal to value
        - where("field", "in", [list]) - Field value is in list
        - where("field", "not_in", [list]) - Field value is not in list
        - where("field", "contains", substring) - String field contains substring
        - where("field", "starts_with", prefix) - String field starts with prefix
        - where("field", "ends_with", suffix) - String field ends with suffix
        """
        # If first argument is callable, delegate to filter
        if callable(field):
            return self.filter(field)
        
        # If only field is provided, check for truthiness
        if condition is None and value is None:
            def predicate(item):
                if isinstance(item, dict):
                    return item.get(field)
                elif hasattr(item, field):
                    return getattr(item, field)
                else:
                    return False
            return self.filter(predicate)
        
        # Create predicate based on condition
        def predicate(item):
            # Get field value
            if isinstance(item, dict):
                field_value = item.get(field)
            elif hasattr(item, field):
                field_value = getattr(item, field)
            else:
                return False
            
            # Apply condition
            try:
                if condition == "gt":
                    return field_value > value
                elif condition == "lt":
                    return field_value < value
                elif condition == "eq":
                    return field_value == value
                elif condition == "ne":
                    return field_value != value
                elif condition == "ge":
                    return field_value >= value
                elif condition == "le":
                    return field_value <= value
                elif condition == "in":
                    return field_value in value
                elif condition == "not_in":
                    return field_value not in value
                elif condition == "contains":
                    return isinstance(field_value, str) and value in field_value
                elif condition == "starts_with":
                    return isinstance(field_value, str) and field_value.startswith(value)
                elif condition == "ends_with":
                    return isinstance(field_value, str) and field_value.endswith(value)
                else:
                    # Unknown condition, return False
                    return False
            except Exception:
                # If comparison fails, return False
                return False
        
        return self.filter(predicate)
    
    def select(self, field: Union[str, Callable, List[str]], as_: Union[str, List[str]] = None) -> 'Queryable':
        """Select specific fields from each element.
        
        Usage:
        - select("field") - Select a single field
        - select("field", as_="alias") - Select a field and rename it
        - select(["field1", "field2"]) - Select multiple fields
        - select(["field1", "field2"], as_=["alias1", "alias2"]) - Select multiple fields with renaming
        - select(lambda x: transform(x)) - Transform each element with a function
        """
        def operation(data):
            # Handle callable
            if callable(field):
                return (field(item) for item in data)
            
            # Handle list of fields with aliasing
            if isinstance(field, list):
                def select_fields(item):
                    result = {}
                    for i, f in enumerate(field):
                        # Get alias if provided
                        alias = as_[i] if isinstance(as_, list) and i < len(as_) else f
                        if isinstance(item, dict):
                            result[alias] = item.get(f)
                        else:
                            try:
                                result[alias] = getattr(item, f)
                            except AttributeError:
                                result[alias] = None
                    return result
                
                return (select_fields(item) for item in data)
            
            # Handle single field (string) with aliasing
            if isinstance(field, str):
                alias = as_ if isinstance(as_, str) else field
                
                def get_field(item):
                    if isinstance(item, dict):
                        return item.get(field)
                    else:
                        try:
                            return getattr(item, field)
                        except AttributeError:
                            return None
                
                # For single field selection with alias, return a dict
                if as_ is not None:
                    return ({alias: get_field(item)} for item in data)
                else:
                    # Just return the field value directly
                    return (get_field(item) for item in data)
        
        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def map(self, func: Union[Callable, dict, type], field: str = None) -> 'Queryable':
        """Transform each element using a function or type cast.
        
        Usage:
        - map(lambda x: transform(x)) - Transform each element with a function
        - map({"field1": lambda x: transform(x), "field2": int}) - Transform specific fields
        - map(int, field="age") - Type cast a specific field to integer
        - map(str, field="id") - Type cast a specific field to string
        - map(float) - Type cast each element to float
        """
        def operation(data):
            # Handle dict of field-specific functions/types
            if isinstance(func, dict):
                def transform_fields(item):
                    if isinstance(item, dict):
                        result = item.copy()
                        for field_name, field_func in func.items():
                            try:
                                # Handle type casting
                                if isinstance(field_func, type):
                                    result[field_name] = field_func(item.get(field_name))
                                else:
                                    # Handle transformation function
                                    result[field_name] = field_func(item.get(field_name))
                            except Exception:
                                # If transformation fails, keep original value
                                pass
                        return result
                    else:
                        # For non-dict items, we can't apply field-specific transformations
                        return item
                
                return (transform_fields(item) for item in data)
            
            # Handle field-specific mapping/type casting
            if field is not None:
                def transform_field(item):
                    if isinstance(item, dict):
                        result = item.copy()
                        try:
                            # Handle type casting
                            if isinstance(func, type):
                                result[field] = func(item.get(field))
                            else:
                                # Handle transformation function
                                result[field] = func(item.get(field))
                        except Exception:
                            # If transformation fails, keep original value
                            pass
                        return result
                    else:
                        # For non-dict items, try to get and set attribute
                        try:
                            value = getattr(item, field)
                            # Handle type casting
                            if isinstance(func, type):
                                new_item = item.copy() if hasattr(item, 'copy') else item
                                setattr(new_item, field, func(value))
                            else:
                                # Handle transformation function
                                new_item = item.copy() if hasattr(item, 'copy') else item
                                setattr(new_item, field, func(value))
                        except Exception:
                            # If transformation fails, keep original value
                            new_item = item
                        return new_item
                
                return (transform_field(item) for item in data)
            
            # Handle general mapping function/type casting
            def safe_func(item):
                try:
                    # Handle type casting
                    if isinstance(func, type):
                        # Apply to the whole item
                        return func(item) if not isinstance(item, dict) else item
                    else:
                        # Handle transformation function
                        return func(item)
                except Exception:
                    # If transformation fails, return item as is
                    return item
            return (safe_func(item) for item in data)
        
        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def limit(self, n: int) -> 'Queryable':
        """Limit the number of results."""
        def operation(data):
            count = 0
            for item in data:
                if count >= n:
                    break
                yield item
                count += 1
        
        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def skip(self, n: int) -> 'Queryable':
        """Skip the first n results."""
        def operation(data):
            count = 0
            for item in data:
                if count >= n:
                    yield item
                count += 1
        
        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def order_by(self, key: Union[str, Callable]) -> 'Queryable':
        """Sort results by a key."""
        def operation(data):
            items = list(data)
            if callable(key):
                try:
                    return sorted(items, key=key)
                except Exception:
                    # If key function fails, return items as is
                    return items
            else:
                try:
                    return sorted(items, key=lambda x: x[key] if isinstance(x, dict) and key in x else None)
                except Exception:
                    # If sorting fails, return items as is
                    return items
        
        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def group_by(self, key: Union[str, Callable]) -> 'Queryable':
        """Group elements by a key."""
        def operation(data):
            groups = defaultdict(list)
            for item in data:
                try:
                    if callable(key):
                        group_key = key(item)
                    else:
                        group_key = item[key] if isinstance(item, dict) else getattr(item, key)
                    groups[group_key].append(item)
                except (KeyError, AttributeError, TypeError):
                    # If the key doesn't exist, group under None
                    groups[None].append(item)
            
            # Return list of (key, items) tuples
            return list(groups.items())
        
        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def join(self, target: Any, on: str = None, left_on: str = None, right_on: str = None, how: str = "inner") -> 'Queryable':
        """
        Join the current data with another data source.
        
        :param target: The data to join with (List, CSV, JSON, etc.)
        :param on: Key to join on (if same in both)
        :param left_on: Key in the current data
        :param right_on: Key in the target data
        :param how: Type of join ('inner', 'left')
        """
        # specific import to avoid circular dependency if any
        from .registry import registry
        
        # Normalize join keys
        if on:
            left_key = on
            right_key = on
        elif left_on and right_on:
            left_key = left_on
            right_key = right_on
        else:
            raise ValueError("Must provide either 'on' or both 'left_on' and 'right_on'")

        def operation(left_data):
            # 1. Materialize the RIGHT side (target) into a Hash Map
            # We use a temporary Queryable to leverage the adapter system for the target
            right_queryable = Queryable(target)
            right_data_list = right_queryable.to_list()
            
            # Build Hash Map: Key -> List[Row] (to handle one-to-many)
            right_map = defaultdict(list)
            for item in right_data_list:
                # Extract key value
                if isinstance(item, dict):
                    k = item.get(right_key)
                else:
                    k = getattr(item, right_key, None)
                
                # Only index if key exists (skip None keys for join purposes usually, 
                # or strictly follow SQL behavior where NULL != NULL)
                if k is not None:
                    right_map[k].append(item)

            # 2. Stream the LEFT side and probe
            for left_item in left_data:
                # Extract left key
                if isinstance(left_item, dict):
                    l_k = left_item.get(left_key)
                else:
                    l_k = getattr(left_item, left_key, None)
                
                matches = right_map.get(l_k, [])
                
                if not matches:
                    if how == "left":
                        # Yield left item with empty right fields (merged is just left item here effectively)
                        # But to be proper, we should probably ensure it's a dict and maybe add nulls?
                        # For simplicity in NoSQL/Dict world, we just return the left item 
                        # optionally with suffix keys if we did collision detection, but here no collision.
                        yield left_item
                else:
                    # Yield one result per match (Cross Product for this key)
                    for right_item in matches:
                        # Merge Logic
                        merged = {}
                        
                        # Add Left items
                        if isinstance(left_item, dict):
                            for k, v in left_item.items():
                                merged[k] = v
                        else:
                             # If primitive, this is tricky. 
                             # Assume we wrap it or it has attributes.
                             pass 

                        # Add Right items (handle collisions)
                        if isinstance(right_item, dict):
                            for k, v in right_item.items():
                                if k in merged:
                                    # Collision!
                                    merged[f"{k}_joined"] = v
                                else:
                                    merged[k] = v
                        
                        yield merged

        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + [operation]
        return new_queryable

    def to_list(self) -> List:
        """Execute the query and return a list."""
        # Start with data source
        result_iter = iter(self._data_source)
        
        # Apply all operations
        for operation in self._operations:
            result_iter = operation(result_iter)
        
        # Convert to list
        return list(result_iter)
    
    def to_dict(self) -> dict:
        """Execute the query and return a dictionary."""
        result = self.to_list()
        if isinstance(result, dict):
            return result
        elif isinstance(result, list) and len(result) > 0:
            # If it's a list of key-value pairs, convert to dict
            if isinstance(result[0], (list, tuple)) and len(result[0]) == 2:
                return dict(result)
            # If it's a list of dicts with 'key' and 'value' fields, convert to dict
            elif isinstance(result[0], dict) and 'key' in result[0] and 'value' in result[0]:
                return {item['key']: item['value'] for item in result}
            # If it's a list of (key, value) tuples from group_by, convert to dict
            elif isinstance(result[0], (list, tuple)) and len(result[0]) == 2 and isinstance(result[0][1], list):
                return dict(result)
        # Default case - return dict with index as key
        return {i: item for i, item in enumerate(result)}
    
    def to_json(self) -> str:
        """Execute the query and return a JSON string."""
        return json.dumps(self.to_list(), indent=2)
    
    def to_csv(self) -> str:
        """Execute the query and return a CSV string."""
        data = self.to_list()
        if not data:
            return ""
        
        # Get all unique field names
        fieldnames = set()
        for item in data:
            if isinstance(item, dict):
                fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames)) if fieldnames else []
        
        if not fieldnames:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
    
    def to_df(self):
        """Execute the query and return a pandas DataFrame (if pandas is available)."""
        try:
            import pandas as pd
            return pd.DataFrame(self.to_list())
        except ImportError:
            raise ImportError("pandas is required for to_df(). Install with: pip install pandas")


def Q(data: Any) -> Queryable:
    """Create a queryable object from data."""
    return Queryable(data)