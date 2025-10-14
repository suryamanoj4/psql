"""
pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

from typing import Any, Callable, List, Union, Iterator
from functools import reduce
from collections import defaultdict


class Queryable:
    """A lazy, chainable interface for querying data."""
    
    def __init__(self, data: Any):
        """Initialize with data to query."""
        self._data = data
        self._operations = []
    
    def filter(self, predicate: Callable) -> 'Queryable':
        """Filter elements based on a predicate function."""
        def operation(data):
            # Handle None data
            if data is None:
                return []
            
            # Handle non-iterable data
            if not hasattr(data, '__iter__') or isinstance(data, (str, bytes)):
                try:
                    return [data] if predicate(data) else []
                except Exception:
                    # If predicate fails on non-iterable data, return empty list
                    return []
            
            # Handle iterable data
            try:
                return (item for item in data if predicate(item))
            except Exception:
                # If predicate fails on any item, filter it out
                def safe_predicate(item):
                    try:
                        return predicate(item)
                    except Exception:
                        return False
                return (item for item in data if safe_predicate(item))
        
        new_queryable = Queryable(self._data)
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
        
        For custom conditions, use filter() method instead.
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
                if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                    return (field(item) for item in data)
                else:
                    return field(data)
            
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
                
                if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                    return (select_fields(item) for item in data)
                else:
                    return select_fields(data)
            
            # Handle single field (string) with aliasing
            if isinstance(field, str):
                alias = as_ if isinstance(as_, str) else field
                
                if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                    def get_field(item):
                        if isinstance(item, dict):
                            return item.get(field)
                        else:
                            try:
                                return getattr(item, field)
                            except AttributeError:
                                return None
                    
                    # For single field selection, we return the value directly, not a dict
                    if as_ is None:
                        return (get_field(item) for item in data)
                    else:
                        # If aliasing, return a dict
                        return ({alias: get_field(item)} for item in data)
                else:
                    if isinstance(data, dict):
                        value = data.get(field)
                    else:
                        try:
                            value = getattr(data, field)
                        except AttributeError:
                            value = None
                    
                    # For single field selection, we return the value directly, not a dict
                    if as_ is None:
                        return value
                    else:
                        # If aliasing, return a dict
                        return {alias: value}
        
        new_queryable = Queryable(self._data)
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
                
                if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                    return (transform_fields(item) for item in data)
                else:
                    return transform_fields(data)
            
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
                                setattr(item, field, func(value))
                            else:
                                # Handle transformation function
                                setattr(item, field, func(value))
                        except Exception:
                            # If transformation fails, keep original value
                            pass
                        return item
                
                if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                    return (transform_field(item) for item in data)
                else:
                    return transform_field(data)
            
            # Handle general mapping function/type casting
            if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                def safe_func(item):
                    try:
                        # Handle type casting
                        if isinstance(func, type):
                            return func(item)
                        else:
                            # Handle transformation function
                            return func(item)
                    except Exception:
                        # If transformation fails, return item as is
                        return item
                return (safe_func(item) for item in data)
            else:
                try:
                    # Handle type casting
                    if isinstance(func, type):
                        return func(data)
                    else:
                        # Handle transformation function
                        return func(data)
                except Exception:
                    # If transformation fails, return data as is
                    return data
        
        new_queryable = Queryable(self._data)
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def limit(self, n: int) -> 'Queryable':
        """Limit the number of results."""
        def operation(data):
            if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                # Generator that yields at most n items
                count = 0
                for item in data:
                    if count >= n:
                        break
                    yield item
                    count += 1
            else:
                # If data is not iterable, return it as is (single item)
                return data
        
        new_queryable = Queryable(self._data)
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def skip(self, n: int) -> 'Queryable':
        """Skip the first n results."""
        def operation(data):
            if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                # Skip first n items
                count = 0
                for item in data:
                    if count >= n:
                        yield item
                    count += 1
            else:
                # If data is not iterable, return None if we're supposed to skip it
                return None if n > 0 else data
        
        new_queryable = Queryable(self._data)
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def order_by(self, key: Union[str, Callable]) -> 'Queryable':
        """Sort results by a key."""
        def operation(data):
            # For lazy sorting, we need to collect all items first
            # This is one of the limitations of lazy evaluation with sorting
            if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
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
            else:
                # If data is not iterable, return it as is
                return data
        
        new_queryable = Queryable(self._data)
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def group_by(self, key: Union[str, Callable]) -> 'Queryable':
        """Group elements by a key."""
        def operation(data):
            if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                groups = defaultdict(list)
                if callable(key):
                    for item in data:
                        try:
                            groups[key(item)].append(item)
                        except Exception:
                            # If the key function fails, group under None
                            groups[None].append(item)
                else:
                    for item in data:
                        try:
                            groups[item[key]].append(item)
                        except (KeyError, TypeError):
                            # If the key doesn't exist or item is not a dict, group under None
                            groups[None].append(item)
                # Return list of (key, items) tuples
                return list(groups.items())
            else:
                # If data is not iterable, return it as a single group
                return [(None, [data])] if data is not None else []
        
        new_queryable = Queryable(self._data)
        new_queryable._operations = self._operations + [operation]
        return new_queryable
    
    def to_list(self) -> List:
        """Execute the query and return a list."""
        result = self._data
        for operation in self._operations:
            result = operation(result)
        
        # Convert final result to list
        if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
            return list(result)
        elif result is not None:
            return [result]
        else:
            return []
    
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


def Q(data: Any) -> Queryable:
    """Create a queryable object from data."""
    return Queryable(data)