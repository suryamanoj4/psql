"""
pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

from typing import Any, Callable, List, Union, Iterator, Dict
from functools import reduce
from collections import defaultdict
import copy
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
        self._condition_groups = []
    
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
    
    def where(self, field, condition=None, value=None, or_: bool = False) -> 'Queryable':
        """Simple filter for common use cases with intuitive syntax.
        
        Supports SQL-like AND/OR chaining:
        
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
        
        OR Support:
        - where("field", "gt", value, or_=True) - OR with previous conditions
        - where([("field1", "op", val1), ("field2", "op", val2)]) - Batch AND
        - where([("f1", "op", v1, or_=True), ("f2", "op", v2)]) - Batch OR
        
        Examples:
        # SQL: age > 18 OR salary > 20000
        .where("age", "gt", 18).where("salary", "gt", 20000, or_=True)
        
        # SQL: age > 18 AND (salary > 20000 OR dept == 'executive')
        .where("age", "gt", 18).where([
            ("salary", "gt", 20000, or_=True),
            ("dept", "eq", "executive", or_=True)
        ])
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
        
        # Handle batch conditions (list of tuples)
        if isinstance(field, list):
            if len(field) == 0:
                raise ValueError("Batch conditions cannot be empty")
            
            # Determine operator for this batch (AND by default, OR if or_=True)
            batch_operator = 'or' if or_ else 'and'
            
            conditions = []
            for cond in field:
                if len(cond) == 3:
                    f, c, v = cond
                    conditions.append((f, c, v))
                elif len(cond) == 4:
                    f, c, v, o = cond
                    conditions.append((f, c, v))
                    if o:
                        batch_operator = 'or'
                else:
                    raise ValueError(f"Invalid condition format: {cond}")
            
            # Create new condition group
            new_group = {
                'operator': batch_operator,
                'conditions': conditions
            }
            
            # Add to condition groups and apply filter
            new_queryable = Queryable([])
            new_queryable._data_source = self._data_source
            new_queryable._operations = self._operations + []
            new_queryable._condition_groups = self._condition_groups + [new_group]
            new_queryable._apply_conditions_filter()
            return new_queryable
        
        # Handle single condition
        # If or_=True and there's a previous group, extend it as OR
        if or_ and self._condition_groups:
            # Extend previous group with new condition as OR
            # If previous group was AND, now it becomes mixed
            # Create a deep copy of all groups and modify the last one
            new_condition_groups = copy.deepcopy(self._condition_groups)
            new_condition_groups[-1]['operator'] = 'or'
            new_condition_groups[-1]['conditions'].append((field, condition, value))
            
            # Replace the last filter operation with new combined filter
            # Don't add a new filter, rebuild operations without the last filter
            new_operations = self._operations[:-1]
            
            # Create new queryable with modified condition groups
            new_queryable = Queryable([])
            new_queryable._data_source = self._data_source
            new_queryable._operations = new_operations + []
            new_queryable._condition_groups = new_condition_groups
            new_queryable._apply_conditions_filter()
            return new_queryable
        
        # Create new group for AND condition (first condition or without or_=True)
        new_group = {
            'operator': 'and',
            'conditions': [(field, condition, value)]
        }
        
        # Add to condition groups and apply filter
        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + []
        new_queryable._condition_groups = self._condition_groups + [new_group]
        new_queryable._apply_conditions_filter()
        return new_queryable
        
        # Create new group for AND condition (first condition or without or_=True)
        new_group = {
            'operator': 'and',
            'conditions': [(field, condition, value)]
        }
        
        # Add to condition groups and apply filter
        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + []
        new_queryable._condition_groups = self._condition_groups + [new_group]
        new_queryable._apply_conditions_filter()
        return new_queryable
    
    def _apply_conditions_filter(self) -> None:
        """Add a filter operation that evaluates all stored condition groups."""
        if not self._condition_groups:
            return
        
        def predicate(item):
            """Evaluate all condition groups using SQL-like AND/OR logic."""
            group_results = []
            
            for group in self._condition_groups:
                if group['operator'] == 'and':
                    # All conditions in this group must be true
                    result = all(
                        self._evaluate_single_condition(item, cond)
                        for cond in group['conditions']
                    )
                else:  # 'or'
                    # At least one condition in this group must be true
                    result = any(
                        self._evaluate_single_condition(item, cond)
                        for cond in group['conditions']
                    )
                
                group_results.append(result)
            
            # All groups are ANDed together
            final_result = all(group_results)
            return final_result
        
        # Add filter operation
        self._operations.append(lambda data: (item for item in data if predicate(item)))
    
    def _evaluate_single_condition(self, item: Any, condition: tuple) -> bool:
        """Evaluate a single condition tuple (field, operator, value)."""
        field_name, operator, value = condition
        
        # Get field value
        if isinstance(item, dict):
            field_value = item.get(field_name)
        elif hasattr(item, field_name):
            field_value = getattr(item, field_name)
        else:
            return False
        
        # Apply operator
        try:
            if operator == "gt":
                return field_value > value
            elif operator == "lt":
                return field_value < value
            elif operator == "eq":
                return field_value == value
            elif operator == "ne":
                return field_value != value
            elif operator == "ge":
                return field_value >= value
            elif operator == "le":
                return field_value <= value
            elif operator == "in":
                return field_value in value
            elif operator == "not_in":
                return field_value not in value
            elif operator == "contains":
                return isinstance(field_value, str) and value in field_value
            elif operator == "starts_with":
                return isinstance(field_value, str) and field_value.startswith(value)
            elif operator == "ends_with":
                return isinstance(field_value, str) and field_value.endswith(value)
            else:
                return False
        except Exception:
            return False
    
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
        :param how: Type of join ('inner', 'left', 'right', 'outer')
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
            right_keys_set = set()  # Track keys that appear in right data for outer joins
            for item in right_data_list:
                # Extract key value
                if isinstance(item, dict):
                    k = item.get(right_key)
                else:
                    k = getattr(item, right_key, None)

                # Track keys for outer joins
                if k is not None:
                    right_keys_set.add(k)
                
                # Only index if key exists (skip None keys for join purposes usually,
                # or strictly follow SQL behavior where NULL != NULL)
                if k is not None:
                    right_map[k].append(item)

            # Track left keys for full outer joins and collect schema
            left_keys_set = set()
            left_schema = set()  # Track all possible keys in left data
            
            # First pass: collect keys and schema
            left_items = []
            for left_item in left_data:
                left_items.append(left_item)
                
                # Extract left key
                if isinstance(left_item, dict):
                    l_k = left_item.get(left_key)
                    # Collect schema
                    left_schema.update(left_item.keys())
                else:
                    l_k = getattr(left_item, left_key, None)

                # Track left keys for outer joins
                if l_k is not None:
                    left_keys_set.add(l_k)

            # 2. Process the LEFT side based on join type
            for left_item in left_items:
                # Extract left key
                if isinstance(left_item, dict):
                    l_k = left_item.get(left_key)
                else:
                    l_k = getattr(left_item, left_key, None)

                matches = right_map.get(l_k, [])

                if not matches:
                    if how == "left":
                        # For left join, yield left item without right fields
                        yield left_item
                    elif how == "outer":
                        # For outer join, yield left item with None values for right fields
                        merged = {}
                        # Add Left items
                        if isinstance(left_item, dict):
                            for k, v in left_item.items():
                                merged[k] = v
                        else:
                            # If primitive, this is tricky.
                            # Assume we wrap it or it has attributes.
                            pass
                        
                        # Add None values for right fields
                        if right_data_list and isinstance(right_data_list[0], dict):
                            for right_key_name in right_data_list[0].keys():
                                if right_key_name not in merged:
                                    merged[right_key_name] = None
                                elif right_key_name == right_key:  # Handle key name collision
                                    merged[f"{right_key_name}_joined"] = None
                        
                        yield merged
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
            
            # Handle RIGHT and OUTER joins - add unmatched right items
            if how in ["right", "outer"]:
                # Find right items that were not matched
                for right_item in right_data_list:
                    if isinstance(right_item, dict):
                        r_k = right_item.get(right_key)
                    else:
                        r_k = getattr(right_item, right_key, None)
                    
                    # If this right key wasn't matched in left data, yield it with None left values
                    if r_k is not None and r_k not in left_keys_set:
                        merged = {}
                        
                        # Add None values for left fields based on collected schema
                        for left_key_name in left_schema:
                            merged[left_key_name] = None
                            # Special handling for join key to avoid confusion
                            if left_key_name == left_key and right_key in right_item:
                                merged[f"{left_key_name}_left"] = None
                        
                        # Add Right items
                        if isinstance(right_item, dict):
                            for k, v in right_item.items():
                                # Avoid overwriting left fields
                                if k not in merged:
                                    merged[k] = v
                                else:
                                    # Handle collision
                                    merged[f"{k}_joined"] = v
                        
                        yield merged

        new_queryable = Queryable([])
        new_queryable._data_source = self._data_source
        new_queryable._operations = self._operations + [operation]
        return new_queryable

    def left_join(self, target: Any, on: str = None, left_on: str = None, right_on: str = None) -> 'Queryable':
        """
        Left join the current data with another data source.
        
        :param target: The data to join with (List, CSV, JSON, etc.)
        :param on: Key to join on (if same in both)
        :param left_on: Key in the current data
        :param right_on: Key in the target data
        """
        return self.join(target, on=on, left_on=left_on, right_on=right_on, how="left")

    def right_join(self, target: Any, on: str = None, left_on: str = None, right_on: str = None) -> 'Queryable':
        """
        Right join the current data with another data source.
        
        :param target: The data to join with (List, CSV, JSON, etc.)
        :param on: Key to join on (if same in both)
        :param left_on: Key in the current data
        :param right_on: Key in the target data
        """
        return self.join(target, on=on, left_on=left_on, right_on=right_on, how="right")

    def outer_join(self, target: Any, on: str = None, left_on: str = None, right_on: str = None) -> 'Queryable':
        """
        Full outer join the current data with another data source.
        
        :param target: The data to join with (List, CSV, JSON, etc.)
        :param on: Key to join on (if same in both)
        :param left_on: Key in the current data
        :param right_on: Key in the target data
        """
        return self.join(target, on=on, left_on=left_on, right_on=right_on, how="outer")

    def cross_join(self, target: Any) -> 'Queryable':
        """
        Cross join the current data with another data source (Cartesian product).
        
        :param target: The data to join with (List, CSV, JSON, etc.)
        """
        def operation(left_data):
            # Materialize the right side
            right_queryable = Queryable(target)
            right_data_list = right_queryable.to_list()
            
            # Create Cartesian product
            for left_item in left_data:
                for right_item in right_data_list:
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