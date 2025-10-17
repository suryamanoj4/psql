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

### 1. Fix Current Issues

#### A. File Adapter Registration
Current issue: File adapters not properly registering or being found.

**Solution**:
```python
# In adapters.py - ensure proper registration
def register_builtin_adapters():
    """Register all built-in adapters."""
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

#### B. Path Handling in File Adapters
Issue: File paths not being handled correctly.

**Solution**:
```python
class CSVFileAdapter(DataAdapter):
    def can_handle(self, data: Any) -> bool:
        # More robust path checking
        if not isinstance(data, str):
            return False
        
        path = Path(data)
        return path.exists() and path.suffix.lower() == '.csv'
    
    def adapt(self, data: Any) -> DataSource:
        return CSVFileDataSource(str(Path(data).resolve()))
```

### 2. Core Query Operations Enhancement

#### A. Advanced Where Conditions
Extend the `where` method to support complex expressions:

```python
def where(self, field, condition=None, value=None) -> 'Queryable':
    """Extended where with complex condition support."""
    
    # Support for complex expressions like "age > 25 AND salary < 100000"
    if isinstance(field, str) and condition is None and value is None:
        # Parse complex expression
        if " AND " in field or " OR " in field:
            return self._parse_complex_expression(field)
    
    # Existing logic for simple conditions
    # ...

def _parse_complex_expression(self, expression: str) -> 'Queryable':
    """Parse and execute complex boolean expressions."""
    # Tokenize expression
    # Build AST
    # Convert to predicate function
    # Return filtered Queryable
    pass
```

#### B. Calculated Fields in Select
Enhance `select` to support calculated fields:

```python
def select(self, fields: Union[str, List, Dict], as_: Union[str, List[str]] = None) -> 'Queryable':
    """Extended select with calculated field support."""
    
    def operation(data):
        if isinstance(fields, dict):
            # Handle calculated fields
            def calculate_fields(item):
                result = {}
                for alias, expr in fields.items():
                    if callable(expr):
                        # Lambda function
                        result[alias] = expr(item)
                    elif isinstance(expr, str):
                        # Expression string (e.g., "salary * 12")
                        result[alias] = self._evaluate_expression(expr, item)
                    else:
                        result[alias] = expr
                return result
            return (calculate_fields(item) for item in data)
        
        # Existing logic for simple field selection
        # ...
    
    # ...
```

### 3. Aggregation Functions Implementation

#### A. Aggregate Method
```python
def aggregate(self, aggregations: Dict[str, str]) -> 'Queryable':
    """Perform aggregations on the data."""
    
    def operation(data):
        items = list(data)
        if not items:
            return [{}]
        
        result = {}
        for alias, agg_expr in aggregations.items():
            result[alias] = self._execute_aggregation(agg_expr, items)
        
        return [result]
    
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
        return sum(float(item.get(field, 0)) for item in items if item.get(field) is not None)
    
    elif agg_expr.startswith('AVG('):
        field = agg_expr[4:-1]
        values = [float(item[field]) for item in items if item.get(field) is not None]
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
```

#### B. Grouped Aggregations
```python
def group_by(self, key: Union[str, Callable], aggregations: Dict[str, str] = None) -> 'Queryable':
    """Group by key with optional aggregations."""
    
    def operation(data):
        if aggregations:
            # Group and aggregate in one step
            groups = defaultdict(list)
            for item in data:
                try:
                    if callable(key):
                        group_key = key(item)
                    else:
                        group_key = item[key] if isinstance(item, dict) else getattr(item, key)
                    groups[group_key].append(item)
                except (KeyError, AttributeError, TypeError):
                    groups[None].append(item)
            
            # Apply aggregations to each group
            result = []
            for group_key, group_items in groups.items():
                agg_result = {"_group_key": group_key}
                for alias, agg_expr in aggregations.items():
                    agg_result[alias] = self._execute_aggregation(agg_expr, group_items)
                result.append(agg_result)
            
            return result
        else:
            # Just grouping without aggregation (existing behavior)
            groups = defaultdict(list)
            for item in data:
                try:
                    if callable(key):
                        group_key = key(item)
                    else:
                        group_key = item[key] if isinstance(item, dict) else getattr(item, key)
                    groups[group_key].append(item)
                except (KeyError, AttributeError, TypeError):
                    groups[None].append(item)
            
            return list(groups.items())
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations + [operation]
    return new_queryable
```

### 4. Join Operations Implementation

#### A. Basic Join Method
```python
def join(self, other: Any, on: Union[str, Callable], how: str = 'inner') -> 'Queryable':
    """Join with another dataset."""
    
    def operation(left_data):
        # Adapt the right dataset
        right_queryable = Queryable(other)
        right_data = right_queryable.to_list()
        
        # Parse join condition
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
        
        # Build right index for performance
        right_index = defaultdict(list)
        for item in right_data:
            if right_field:
                key = item.get(right_field)
                right_index[key].append(item)
            else:
                # For callable conditions, we can't pre-index
                right_index[None].extend(right_data)
                break
        
        # Perform join
        result = []
        for left_item in left_data:
            if left_field and right_field:
                # Hash join using indexes
                left_key = left_item.get(left_field)
                matching_rights = right_index.get(left_key, [])
                
                if how == 'inner' and matching_rights:
                    # INNER JOIN
                    for right_item in matching_rights:
                        result.append({**left_item, **right_item})
                elif how == 'left':
                    # LEFT JOIN
                    if matching_rights:
                        for right_item in matching_rights:
                            result.append({**left_item, **right_item})
                    else:
                        result.append({**left_item, **{k: None for k in right_data[0].keys()}})
                # Add RIGHT JOIN and FULL OUTER JOIN logic
            else:
                # Nested loop join for complex conditions
                for right_item in right_data:
                    if condition(left_item, right_item):
                        result.append({**left_item, **right_item})
        
        return result
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations + [operation]
    return new_queryable
```

### 5. Performance Optimizations

#### A. Query Planning
```python
def optimize(self) -> 'Queryable':
    """Optimize the query execution plan."""
    
    # Analyze operations for optimization opportunities
    optimized_ops = []
    
    # Merge consecutive filters
    # Reorder operations for better performance (filters before maps)
    # Push down projections
    # Eliminate redundant operations
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = optimized_ops
    return new_queryable
```

#### B. Streaming Processing
```python
def stream(self, chunk_size: int = 1000) -> 'Queryable':
    """Enable streaming processing for large datasets."""
    
    # Modify data source to yield chunks
    # Apply operations to chunks rather than entire dataset
    # Reduce memory footprint
    
    def streaming_operation(data):
        # Process data in chunks
        chunk = []
        for item in data:
            chunk.append(item)
            if len(chunk) >= chunk_size:
                # Apply operations to this chunk
                yield from self._apply_operations_to_chunk(chunk)
                chunk = []
        
        # Process remaining items
        if chunk:
            yield from self._apply_operations_to_chunk(chunk)
    
    new_queryable = Queryable([])
    new_queryable._data_source = self._data_source
    new_queryable._operations = self._operations + [streaming_operation]
    return new_queryable
```

## Integration Points

### 1. Pandas Integration
```python
def to_df(self) -> 'pd.DataFrame':
    """Convert to pandas DataFrame with optimizations."""
    try:
        import pandas as pd
        
        # For simple datasets, use direct conversion
        if not self._operations:
            return pd.DataFrame(self._data_source)
        
        # For complex queries, execute and convert
        return pd.DataFrame(self.to_list())
    except ImportError:
        raise ImportError("pandas is required for to_df(). Install with: pip install pandas")
```

### 2. Database Integration
```python
# Future extension point for SQL databases
def sql(self, query: str) -> 'Queryable':
    """Execute SQL query directly on database sources."""
    # Check if data source is a database connection
    # If so, execute SQL and return results as Queryable
    # Otherwise, raise appropriate error
    pass
```

## Testing Strategy

### 1. Unit Tests
- Individual adapter functionality
- Core query operations
- Edge cases and error conditions

### 2. Integration Tests
- End-to-end query scenarios
- Multi-source joins
- Complex data transformations

### 3. Performance Tests
- Large dataset processing
- Memory usage monitoring
- Speed comparisons with alternatives

### 4. Compatibility Tests
- Different Python versions
- Various data formats
- Third-party library integrations

## Deployment Considerations

### 1. Packaging
- PyPI distribution
- Conda package
- Docker container

### 2. Documentation
- API reference
- Usage examples
- Migration guides

### 3. Community
- Issue tracking
- Contribution guidelines
- Release management