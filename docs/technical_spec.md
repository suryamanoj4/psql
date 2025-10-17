# pyql Technical Specification

## Core Architecture Overview

### 1. Common Internal Representation
All data in pyql is normalized to `Iterator[Dict[str, Any]]`, which provides:
- **Flexibility**: Handles sparse, heterogeneous, and nested data
- **Memory Efficiency**: Lazy evaluation through iterators
- **Consistency**: Uniform interface regardless of source format
- **Python Native**: Uses familiar dictionary structures

### 2. Component Architecture

#### A. DataSource Interface
```python
class DataSource(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Return an iterator over records as dictionaries."""
        pass
```

#### B. DataAdapter Interface
```python
class DataAdapter(ABC):
    @abstractmethod
    def can_handle(self, data: Any) -> bool:
        """Check if this adapter can handle the given data."""
        pass
    
    @abstractmethod
    def adapt(self, data: Any) -> DataSource:
        """Convert the input data to a DataSource."""
        pass
```

#### C. Queryable Class
Main entry point for query operations with methods like:
- `filter()`, `where()` - Row filtering
- `select()` - Column selection/projection
- `map()` - Row transformation
- `order_by()` - Sorting
- `group_by()` - Grouping
- `join()` - Data joining (future)
- `aggregate()` - Statistical operations (future)

#### D. Output Serialization
```python
class OutputSerializer(ABC):
    @abstractmethod
    def can_serialize(self, format_name: str) -> bool:
        """Check if this serializer can handle the given format."""
        pass
    
    @abstractmethod
    def serialize(self, data: Iterator[Dict[str, Any]], format_name: str) -> Any:
        """Serialize the data to the requested format."""
        pass
```

## Next Phase Implementation Plan

### 1. Fix Current Issues - Zero Dependency Approach

#### A. File Adapter Registration
Current issue: File adapters not properly registering or being found.

**Solution - Use only standard library**:
```python
# In adapters.py - ensure proper registration using only stdlib
import os
import pathlib

def register_builtin_adapters():
    """Register all built-in adapters using only standard library."""
    registry.register_data_adapter(ListOfDictsAdapter)
    registry.register_data_adapter(ListOfPrimitivesAdapter)
    registry.register_data_adapter(ListOfListsAdapter)
    registry.register_data_adapter(DictAdapter)
    registry.register_data_adapter(SingleValueAdapter)
    registry.register_data_adapter(CSVFileAdapter)
    registry.register_data_adapter(JSONFileAdapter)

# Call during module initialization
register_builtin_adapters()
```

#### B. Path Handling in File Adapters - Zero Dependency
Issue: File paths not being handled correctly.

**Solution - Use only pathlib and os from stdlib**:
```python
import os
import pathlib

class CSVFileAdapter(DataAdapter):
    def can_handle(self, data: Any) -> bool:
        """Check if this adapter can handle CSV files using only stdlib."""
        if not isinstance(data, str):
            return False
        
        try:
            path = pathlib.Path(data)
            return path.exists() and path.suffix.lower() == '.csv'
        except (OSError, ValueError):
            return False
    
    def adapt(self, data: Any) -> DataSource:
        """Convert CSV file to DataSource using only stdlib."""
        try:
            path = pathlib.Path(data).resolve()
            return CSVFileDataSource(str(path))
        except (OSError, ValueError) as e:
            raise ValueError(f"Cannot access CSV file {data}: {e}")
```

#### C. CSV File DataSource - Zero Dependency
```python
import csv
import io

class CSVFileDataSource(DataSource):
    """DataSource for CSV files using only stdlib csv module."""
    
    def __init__(self, file_path: str):
        self._file_path = file_path
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over CSV file rows as dictionaries."""
        try:
            with open(self._file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Detect dialect
                sample = csvfile.read(1024)
                csvfile.seek(0)
                
                try:
                    # Try to detect delimiter
                    dialect = csv.Sniffer().sniff(sample)
                except csv.Error:
                    # Fall back to default comma delimiter
                    dialect = csv.excel
                
                reader = csv.reader(csvfile, dialect)
                headers = next(reader, None)
                
                if headers is None:
                    return
                
                # Convert to field names (handle duplicates)
                field_names = []
                for i, header in enumerate(headers):
                    if not header:
                        field_names.append(f"_col_{i}")
                    else:
                        # Sanitize field names
                        sanitized = str(header).strip()
                        if not sanitized.replace('_', '').isalnum():
                            sanitized = f"field_{i}"
                        field_names.append(sanitized)
                
                # Yield rows as dictionaries
                for row in reader:
                    # Pad short rows with None
                    while len(row) < len(field_names):
                        row.append(None)
                    
                    # Create dictionary for this row
                    row_dict = {}
                    for i, field_name in enumerate(field_names):
                        value = row[i] if i < len(row) else None
                        # Convert empty strings to None for consistency
                        if value == "":
                            value = None
                        row_dict[field_name] = value
                    
                    yield row_dict
        except IOError as e:
            raise IOError(f"Error reading CSV file {self._file_path}: {e}")
```

#### D. JSON File DataSource - Zero Dependency
```python
import json

class JSONFileDataSource(DataSource):
    """DataSource for JSON files using only stdlib json module."""
    
    def __init__(self, file_path: str):
        self._file_path = file_path
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over JSON file records as dictionaries."""
        try:
            with open(self._file_path, 'r', encoding='utf-8') as jsonfile:
                try:
                    data = json.load(jsonfile)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in file {self._file_path}: {e}")
                
                # Handle different JSON structures
                if isinstance(data, list):
                    # Array of objects
                    for item in data:
                        if isinstance(item, dict):
                            yield item
                        else:
                            # Wrap non-dict items
                            yield {"_value": item}
                elif isinstance(data, dict):
                    # Single object
                    yield data
                else:
                    # Primitive value
                    yield {"_value": data}
        except IOError as e:
            raise IOError(f"Error reading JSON file {self._file_path}: {e}")
```

### 2. Core Query Operations Enhancement - Maximum Laziness

#### A. Advanced Where Conditions with Lazy Evaluation
Extend the `where` method to support complex expressions while maintaining laziness:

```python
def where(self, field, condition=None, value=None) -> 'Queryable':
    """Extended where with complex condition support - fully lazy."""
    
    def operation(data):
        # Support for complex expressions like "age > 25 AND salary < 100000"
        if isinstance(field, str) and condition is None and value is None:
            # Parse complex expression lazily
            if " AND " in field or " OR " in field:
                return self._parse_complex_expression_lazy(field, data)
        
        # Existing logic for simple conditions with lazy evaluation
        def safe_predicate(item):
            try:
                if isinstance(field, str):
                    if isinstance(item, dict):
                        field_value = item.get(field)
                    else:
                        field_value = getattr(item, field, None)
                    
                    # Apply condition
                    if condition == "gt":
                        return field_value is not None and field_value > value
                    elif condition == "lt":
                        return field_value is not None and field_value < value
                    elif condition == "eq":
                        return field_value == value
                    elif condition == "ne":
                        return field_value != value
                    elif condition == "ge":
                        return field_value is not None and field_value >= value
                    elif condition == "le":
                        return field_value is not None and field_value <= value
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
                        return False
                else:
                    # Callable predicate
                    return field(item)
            except (TypeError, ValueError):
                return False
        
        return (item for item in data if safe_predicate(item))
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations + [operation]
    return new_queryable

def _parse_complex_expression_lazy(self, expression: str, data) -> Iterator[Dict[str, Any]]:
    """Parse and execute complex boolean expressions lazily."""
    # Tokenize expression lazily
    # Build AST lazily
    # Convert to predicate function lazily
    # Return filtered iterator lazily
    tokens = self._tokenize_expression(expression)
    ast = self._build_ast(tokens)
    
    def lazy_filter(data):
        predicate = self._compile_ast_to_function(ast)
        for item in data:
            try:
                if predicate(item):
                    yield item
            except (TypeError, ValueError, KeyError):
                # Skip items that cause evaluation errors
                continue
    
    return lazy_filter(data)
```

#### B. Calculated Fields in Select with Lazy Evaluation
Enhance `select` to support calculated fields while maintaining maximum laziness:

```python
def select(self, fields: Union[str, List, Dict], as_: Union[str, List[str]] = None) -> 'Queryable':
    """Extended select with calculated field support - fully lazy."""
    
    def operation(data):
        # Handle calculated fields lazily
        if isinstance(fields, dict):
            # Handle calculated fields lazily
            def calculate_fields_lazily(item):
                result = {}
                for alias, expr in fields.items():
                    try:
                        if callable(expr):
                            # Lambda function - evaluate lazily
                            result[alias] = expr(item)
                        elif isinstance(expr, str):
                            # Expression string (e.g., "salary * 12") - parse and evaluate lazily
                            result[alias] = self._evaluate_expression_lazily(expr, item)
                        else:
                            result[alias] = expr
                    except (TypeError, ValueError, KeyError):
                        # Handle evaluation errors gracefully
                        result[alias] = None
                return result
            
            return (calculate_fields_lazily(item) for item in data)
        
        # Existing logic for simple field selection with lazy evaluation
        # ...
        
        def select_fields_lazily(item):
            result = {}
            # ... select logic ...
            return result
        
        return (select_fields_lazily(item) for item in data)
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations + [operation]
    return new_queryable
```

### 3. Aggregation Functions Implementation - Lazy and Efficient

#### A. Aggregate Method with Lazy Evaluation
```python
def aggregate(self, aggregations: Dict[str, str]) -> 'Queryable':
    """Perform aggregations on the data - lazy until materialization."""
    
    def operation(data):
        # Aggregations are eager by nature, but we defer execution
        def lazy_aggregate():
            items = list(data)  # Only consume data when materialized
            if not items:
                return [{}]
            
            result = {}
            for alias, agg_expr in aggregations.items():
                result[alias] = self._execute_aggregation(agg_expr, items)
            
            return [result]
        
        # Return a generator that will compute when iterated
        def yield_once():
            yield from lazy_aggregate()
        
        return yield_once()
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations + [operation]
    return new_queryable

def _execute_aggregation(self, agg_expr: str, items: List[Dict]) -> Any:
    """Execute a single aggregation expression."""
    agg_expr = agg_expr.upper().strip()
    
    if agg_expr.startswith('COUNT('):
        if agg_expr == 'COUNT(*)' or agg_expr == 'COUNT(1)':
            return len(items)
        else:
            # Count specific field (non-null values)
            field = agg_expr[6:-1]  # Extract field name
            return sum(1 for item in items if item.get(field) is not None)
    
    elif agg_expr.startswith('SUM('):
        field = agg_expr[4:-1]
        return sum(self._safe_float(item.get(field, 0)) for item in items if item.get(field) is not None)
    
    elif agg_expr.startswith('AVG('):
        field = agg_expr[4:-1]
        values = [self._safe_float(item[field]) for item in items if item.get(field) is not None]
        return sum(values) / len(values) if values else 0
    
    elif agg_expr.startswith('MIN('):
        field = agg_expr[4:-1]
        values = [item[field] for item in items if item.get(field) is not None]
        return min(values) if values else None
    
    elif agg_expr.startswith('MAX('):
        field = agg_expr[4:-1]
        values = [item[field] for item in items if item.get(field) is not None]
        return max(values) if values else None
    
    # Add more aggregation functions (STDDEV, VARIANCE, etc.)
    return None

def _safe_float(self, value) -> float:
    """Safely convert value to float."""
    try:
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            return float(value)
        else:
            return 0.0
    except (TypeError, ValueError):
        return 0.0
```

#### B. Grouped Aggregations with Lazy Evaluation
```python
def group_by(self, key: Union[str, Callable], aggregations: Dict[str, str] = None) -> 'Queryable':
    """Group by key with optional aggregations - lazy grouping."""
    
    def operation(data):
        # Grouping is also eager by nature, but we defer execution
        def lazy_group_and_aggregate():
            if aggregations:
                # Group and aggregate in one step lazily
                groups = {}
                for item in data:
                    try:
                        if callable(key):
                            group_key = key(item)
                        else:
                            group_key = item[key] if isinstance(item, dict) else getattr(item, key)
                        
                        if group_key not in groups:
                            groups[group_key] = []
                        groups[group_key].append(item)
                    except (KeyError, AttributeError, TypeError):
                        # Handle missing keys gracefully
                        if None not in groups:
                            groups[None] = []
                        groups[None].append(item)
                
                # Apply aggregations to each group lazily
                result = []
                for group_key, group_items in groups.items():
                    agg_result = {"_group_key": group_key}
                    for alias, agg_expr in aggregations.items():
                        agg_result[alias] = self._execute_aggregation(agg_expr, group_items)
                    result.append(agg_result)
                
                return result
            else:
                # Just grouping without aggregation (existing behavior) - lazy
                groups = {}
                for item in data:
                    try:
                        if callable(key):
                            group_key = key(item)
                        else:
                            group_key = item[key] if isinstance(item, dict) else getattr(item, key)
                        
                        if group_key not in groups:
                            groups[group_key] = []
                        groups[group_key].append(item)
                    except (KeyError, AttributeError, TypeError):
                        # Handle missing keys gracefully
                        if None not in groups:
                            groups[None] = []
                        groups[None].append(item)
                
                # Return grouped items lazily
                return [{"_group_key": k, "_items": v} for k, v in groups.items()]
        
        # Return a generator that will compute when iterated
        def yield_groups():
            yield from lazy_group_and_aggregate()
        
        return yield_groups()
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations + [operation]
    return new_queryable
```

### 4. Join Operations Implementation - Lazy and Memory Efficient

#### A. Basic Join Method with Lazy Evaluation
```python
def join(self, other: Any, on: Union[str, Callable], how: str = 'inner') -> 'Queryable':
    """Join with another dataset - lazy join."""
    
    def operation(left_data):
        # Join operations are typically eager, but we make them as lazy as possible
        def lazy_join():
            # Adapt the right dataset lazily
            right_queryable = Queryable(other)
            
            # Parse join condition lazily
            if isinstance(on, str):
                # Format: "left_field=right_field" or "left_field" (implies same field name)
                if '=' in on:
                    left_field, right_field = on.split('=', 1)
                    left_field = left_field.strip()
                    right_field = right_field.strip()
                else:
                    left_field = right_field = on.strip()
            else:
                # Callable condition
                condition = on
                left_field = right_field = None
            
            # For INNER and LEFT joins, we need to materialize the right side
            # to build an index for performance
            right_data = list(right_queryable.to_list())
            
            # Build right index for performance (if possible)
            right_index = {}
            if left_field and right_field:
                right_index = {}
                for item in right_data:
                    if right_field in item:
                        key = item[right_field]
                        if key not in right_index:
                            right_index[key] = []
                        right_index[key].append(item)
            
            # Perform join lazily
            for left_item in left_data:
                if left_field and right_field and right_index:
                    # Hash join using indexes - as lazy as possible
                    left_key = left_item.get(left_field)
                    matching_rights = right_index.get(left_key, [])
                    
                    if how == 'inner' and matching_rights:
                        # INNER JOIN - yield matches lazily
                        for right_item in matching_rights:
                            yield {**left_item, **right_item}
                    elif how == 'left':
                        # LEFT JOIN - yield matches or fill with None lazily
                        if matching_rights:
                            for right_item in matching_rights:
                                yield {**left_item, **right_item}
                        else:
                            # No matches, fill right side with None
                            right_placeholder = {k: None for k in right_data[0].keys()} if right_data else {}
                            yield {**left_item, **right_placeholder}
                    # Add RIGHT JOIN and FULL OUTER JOIN logic
                else:
                    # Nested loop join for complex conditions - as lazy as possible
                    matched = False
                    for right_item in right_data:
                        if callable(on):
                            if on(left_item, right_item):
                                yield {**left_item, **right_item}
                                matched = True
                        else:
                            # Simple field matching
                            if left_item.get(on) == right_item.get(on):
                                yield {**left_item, **right_item}
                                matched = True
                    
                    # Handle LEFT JOIN for unmatched items
                    if how == 'left' and not matched:
                        right_placeholder = {k: None for k in right_data[0].keys()} if right_data else {}
                        yield {**left_item, **right_placeholder}
        
        return lazy_join()
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations + [operation]
    return new_queryable
```

### 5. Performance Optimizations - Zero Dependencies, Maximum Laziness

#### A. Query Planning with Lazy Optimization
```python
def optimize(self) -> 'Queryable':
    """Optimize the query execution plan - lazy optimization."""
    
    # Analyze operations for optimization opportunities without executing
    optimized_ops = []
    
    # Merge consecutive filters lazily
    # Reorder operations for better performance lazily (filters before maps)
    # Push down projections lazily
    # Eliminate redundant operations lazily
    
    # For now, just return self since we don't have complex optimizations yet
    # Future implementation will analyze the operation pipeline
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations  # Keep operations as-is for now
    return new_queryable
```

#### B. Streaming Processing with Lazy Evaluation
```python
def stream(self, chunk_size: int = 1000) -> 'Queryable':
    """Enable streaming processing for large datasets - fully lazy."""
    
    # This modifies data source to yield chunks lazily
    # Apply operations to chunks rather than entire dataset
    # Reduce memory footprint significantly
    
    def streaming_operation(data):
        # Process data lazily in chunks
        def lazy_chunk_processor():
            chunk = []
            for item in data:
                chunk.append(item)
                if len(chunk) >= chunk_size:
                    # Apply operations to this chunk lazily
                    yield from self._apply_operations_to_chunk_lazily(chunk)
                    chunk = []
            
            # Process remaining items lazily
            if chunk:
                yield from self._apply_operations_to_chunk_lazily(chunk)
        
        return lazy_chunk_processor()
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations + [streaming_operation]
    return new_queryable

def _apply_operations_to_chunk_lazily(self, chunk):
    """Apply operations to a chunk lazily."""
    # Create a temporary queryable for this chunk
    temp_queryable = Queryable([])
    temp_queryable._data_source = iter(chunk)
    temp_queryable._operations = self._operations
    
    # Yield results lazily
    yield from temp_queryable.to_list()
```

## Integration Points - Future Ready Without Dependencies

### 1. Pandas Integration (Optional - No Hard Dependency)
```python
def to_df(self):
    """Convert to pandas DataFrame with optimizations - optional."""
    try:
        import pandas as pd
        
        # For simple datasets, use direct conversion
        if not self._operations:
            return pd.DataFrame(list(self._data_source))
        
        # For complex queries, execute and convert
        return pd.DataFrame(self.to_list())
    except ImportError:
        raise ImportError("pandas is required for to_df(). Install with: pip install pandas")
```

### 2. Database Integration Interface (Future Extension Point)
```python
# Future extension point for SQL databases - no implementation yet
# Design interfaces now for future compatibility

class DatabaseDataSource(DataSource):
    """Interface for database data sources - future implementation."""
    
    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        # Will use sqlite3, psycopg2, mysql.connector, etc. when implemented
    
    def sql(self, query: str) -> 'Queryable':
        """Execute SQL query directly on database sources."""
        # Future implementation will connect to database and execute query
        # Return results as Queryable
        raise NotImplementedError("Database support coming soon")

# Design clean interfaces for future SQLAlchemy integration
class SQLAlchemyDataSource(DataSource):
    """Interface for SQLAlchemy data sources - future implementation."""
    
    def __init__(self, queryable_object):
        self._queryable_object = queryable_object
        # Will use sqlalchemy when implemented
    
    def where(self, *args, **kwargs) -> 'Queryable':
        """SQLAlchemy-style querying."""
        # Future implementation will translate to SQLAlchemy queries
        raise NotImplementedError("SQLAlchemy support coming soon")
```

## Testing Strategy - Comprehensive Without External Tools

### 1. Unit Tests Using Only Standard Library
```python
# tests/test_core.py
import unittest
import tempfile
import json
import csv
import os

class TestCoreFunctionality(unittest.TestCase):
    """Test core pyql functionality using only standard library."""
    
    def test_list_of_primitives(self):
        """Test handling of list of primitives."""
        from pyql import Q
        data = [1, 2, 3, 4, 5]
        result = Q(data).filter(lambda x: x['value'] > 3).to_list()
        expected = [{"value": 4}, {"value": 5}]
        self.assertEqual(result, expected)
    
    def test_csv_file_handling(self):
        """Test CSV file handling using only stdlib."""
        from pyql import Q
        
        # Create temporary CSV file using stdlib
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'age'])
            writer.writerow(['Alice', '25'])
            writer.writerow(['Bob', '30'])
            temp_csv = f.name
        
        try:
            result = Q(temp_csv).where('age', 'gt', '25').to_list()
            expected = [{'name': 'Bob', 'age': '30'}]
            self.assertEqual(result, expected)
        finally:
            os.unlink(temp_csv)
    
    # More tests...
```

### 2. Integration Tests for Real-World Scenarios
```python
# tests/test_real_world_scenarios.py
import unittest
import tempfile
import json
import os

class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios."""
    
    def test_e_commerce_analytics(self):
        """Test e-commerce analytics workflow."""
        from pyql import Q
        
        # Simulate e-commerce data
        products = [
            {"id": 1, "name": "Laptop", "category": "Electronics", "price": "1200.00", "rating": "4.5"},
            {"id": 2, "name": "Phone", "category": "Electronics", "price": "800.00", "rating": "4.7"},
            {"id": 3, "name": "Book", "category": "Education", "price": "20.00", "rating": "4.8"},
        ]
        
        # Complex query: High-rated affordable electronics
        result = (Q(products)
                  .map({"price": float, "rating": float})
                  .where("category", "eq", "Electronics")
                  .where("rating", "gt", 4.4)
                  .where("price", "lt", 1000.0)
                  .select(["name", "price"], as_=["product", "cost"])
                  .order_by("rating")
                  .to_list())
        
        expected = [
            {"product": "Phone", "cost": 800.0},
            {"product": "Laptop", "cost": 1200.0}
        ]
        # Adjust expectation based on actual filtering
        self.assertEqual(len(result), 1)  # Only phone meets criteria
        self.assertEqual(result[0]["product"], "Phone")
    
    # More real-world tests...
```

### 3. Performance Tests Using Standard Library Only
```python
# tests/test_performance.py
import unittest
import time
import sys

class TestPerformance(unittest.TestCase):
    """Test performance characteristics."""
    
    def test_large_dataset_filtering(self):
        """Test filtering performance on large datasets."""
        from pyql import Q
        
        # Create large dataset
        large_data = [{"id": i, "value": i * 2} for i in range(100000)]
        
        # Measure filtering time
        start_time = time.time()
        result = Q(large_data).where("value", "gt", 150000).limit(10).to_list()
        end_time = time.time()
        
        # Assert performance (should be fast due to lazy evaluation and limit)
        self.assertLess(end_time - start_time, 1.0)  # Should complete in under 1 second
        self.assertEqual(len(result), 10)
        self.assertTrue(all(item["value"] > 150000 for item in result))
    
    def test_memory_efficiency(self):
        """Test memory efficiency with streaming."""
        from pyql import Q
        import gc
        
        # Create large dataset
        large_data = ({"id": i, "value": i * 2} for i in range(1000000))  # Generator
        
        # Force garbage collection
        gc.collect()
        initial_memory = self._get_memory_usage()
        
        # Process with streaming
        result = Q(large_data).where("value", "gt", 1500000).limit(100).to_list()
        
        # Check memory usage
        final_memory = self._get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory usage should be reasonable (not increase by GBs)
        self.assertLess(memory_increase, 50 * 1024 * 1024)  # Less than 50MB increase
        self.assertEqual(len(result), 100)
    
    def _get_memory_usage(self):
        """Get current memory usage."""
        try:
            import psutil
            return psutil.Process().memory_info().rss
        except ImportError:
            # Fallback to approximate measurement
            return len(gc.get_objects()) * sys.getsizeof(object())
```

## Deployment Considerations - Zero Dependencies

### 1. Packaging with Standard Tools Only
```bash
# Use only standard Python packaging tools
python -m build  # Instead of external tools like poetry or flit
twine upload dist/*  # Standard deployment tool
```

### 2. Documentation Generation
```bash
# Use standard docstring formats
# Generate documentation with standard tools or manual process
# No external documentation generators required
```

### 3. Community Support
```markdown
# Community Guidelines

## Contributing

1. **Zero External Dependencies**: All contributions must use only Python standard library
2. **Maximum Laziness**: All operations should be lazy-evaluated
3. **Universal Compatibility**: Must work with DFS, CSVs, JSONs, lists, and other popular data formats
4. **Extreme Simplicity**: User experience should be as simple as possible
5. **Future-Proof Design**: Easy to extend for DB connectivity and SQLAlchemy integration

## Issue Reporting

Please include:
1. Version of Python
2. Operating system
3. Exact code that reproduces the issue
4. Expected vs actual behavior
5. Any error messages

## Pull Requests

1. All new features must include comprehensive tests
2. Follow the existing code style and patterns
3. Include documentation updates
4. Ensure zero external dependencies
5. Maintain backward compatibility
```

## Success Criteria

### 1. Technical Excellence
- **Zero External Dependencies**: Only standard library used
- **Maximum Laziness**: All operations lazy until materialization
- **Universal Compatibility**: Works with DFS, CSVs, JSONs, lists, and other popular data formats
- **Extreme Simplicity**: Intuitive API for both SQL and Python developers
- **Future-Ready**: Clean interfaces for DB connectivity and SQLAlchemy integration

### 2. Performance Benchmarks
- Query execution time < 100ms for datasets < 10K records
- Memory usage < 2x original dataset size  
- Scalability to 1M+ records with streaming
- Efficient lazy evaluation with minimal overhead

### 3. Usability Goals
- 90% of common use cases covered by intuitive APIs
- Comprehensive documentation with examples
- Minimal learning curve for SQL/Python developers
- Clear error messages and helpful debugging information

### 4. Reliability Standards
- 99.9% uptime for stable data sources
- Graceful degradation for unstable sources
- Comprehensive error reporting and recovery
- Thorough testing with edge cases covered

### 5. Community Adoption
- Easy installation with pip
- Clear migration path from existing tools
- Active community contributions and support
- Regular releases with improvements and bug fixes