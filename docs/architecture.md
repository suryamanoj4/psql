# pyql Architecture Documentation

## Overview

pyql implements a universal querying toolkit that can handle diverse data sources by normalizing them to a common internal representation: `Iterator[Dict[str, Any]]`. This enables a consistent, chainable, lazy API regardless of the input data format.

## Core Architecture

### 1. Common Internal Representation

All data is normalized to `Iterator[Dict[str, Any]]`, which provides:

- **Natural for Python developers**: Dictionaries are Python's native way of representing structured data
- **Flexible**: Handles sparse data, heterogeneous data, and nested structures
- **Memory efficient**: Iterators ensure lazy evaluation
- **Consistent**: One query engine regardless of source

### 2. Adapter Pattern

The system uses adapters to convert different data formats to the common representation:

#### Built-in Adapters

1. **ListOfPrimitivesAdapter**
   - Handles: `[1, 2, 3, "hello"]` 
   - Converts to: `[{"value": 1}, {"value": 2}, {"value": 3}, {"value": "hello"}]`

2. **ListOfDictsAdapter** 
   - Handles: `[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]`
   - Converts to: `[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]` (unchanged)

3. **ListOfListsAdapter**
   - Handles: `[["name", "age"], ["Alice", 25], ["Bob", 30]]`
   - Converts to: `[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]`

4. **DictAdapter**
   - Handles: `{"name": "Charlie", "age": 35}`
   - Converts to: `[{"name": "Charlie", "age": 35}]`

5. **SingleValueAdapter**
   - Handles: `"hello"`, `42`, etc.
   - Converts to: `[{"_value": "hello"}]`, `[{"_value": 42}]`

6. **CSVFileAdapter**
   - Handles: CSV files
   - Converts to: Iterator of dictionaries with column headers as keys

7. **JSONFileAdapter**
   - Handles: JSON files
   - Converts to: Iterator of dictionaries

### 3. Adapter Registry

Central component that automatically selects the appropriate adapter for any input data:

```python
# Registry automatically finds the right adapter
adapter = registry.get_data_adapter(data)
data_source = adapter.adapt(data)
```

### 4. Lazy Evaluation

All operations are lazy and only executed when materialized:

```python
# Chain operations without execution
query = Q(data).filter(...).select(...).order_by(...)

# Operations execute only when materialized
result = query.to_list()  # or .to_json(), .to_csv(), etc.
```

## Key Features

### Enhanced Querying Methods

1. **Enhanced `where` Method**
   - SQL-like condition operators: `gt`, `lt`, `eq`, `ne`, `ge`, `le`, `in`, `not_in`, `contains`, `starts_with`, `ends_with`
   - Backward compatible with lambda functions

2. **Enhanced `select` Method**
   - Field aliasing with `as_` parameter
   - Multiple field selection with renaming

3. **Enhanced `map` Method**
   - Type casting: `Q(data).map(int, field="age")`
   - Field-specific transformations: `Q(data).map({"age": int, "name": str.upper})`
   - General transformations with lambda functions

### Materialization Options

1. **`to_list()`** - Returns Python list
2. **`to_dict()`** - Returns Python dict  
3. **`to_json()`** - Returns JSON string
4. **`to_csv()`** - Returns CSV string
5. **`to_df()`** - Returns pandas DataFrame (when pandas is available)

### Error Handling

- Graceful handling of malformed data
- Safe type casting with fallbacks
- Robust error recovery in transformation functions

## Real-World Usage Patterns

### 1. E-commerce Data Processing

```python
products = Q("products.csv").where("price", "lt", 1000).where("rating", "gt", 4.0).to_list()
```

### 2. Employee Management  

```python
senior_engineers = (Q(employees)
                   .map({"age": int, "salary": int})
                   .where("department", "eq", "engineering")
                   .where("age", "gt", 30)
                   .where("salary", "gt", 100000)
                   .select(["name", "age", "salary"])
                   .to_list())
```

### 3. Financial Data Analysis

```python
monthly_summary = (Q(transactions)
                  .map({"amount": float})
                  .where("type", "eq", "debit")
                  .group_by("month")
                  .map(lambda group: {
                      "month": group[0],
                      "total": sum(t["amount"] for t in group[1]),
                      "count": len(group[1])
                  })
                  .to_list())
```

## Extensibility

### Adding New Adapters

```python
class MyCustomAdapter(DataAdapter):
    def can_handle(self, data):
        return isinstance(data, MyCustomType)
    
    def adapt(self, data):
        return MyCustomDataSource(data)

# Register the adapter
registry.register_data_adapter(MyCustomAdapter)
```

### Adding New Output Formats

```python
class MyOutputSerializer(OutputSerializer):
    def can_serialize(self, format_name):
        return format_name == "custom_format"
    
    def serialize(self, data, format_name):
        # Custom serialization logic
        return custom_output

# Register the serializer
registry.register_output_serializer(MyOutputSerializer)
```

## Performance Characteristics

1. **Lazy Evaluation**: Operations are only executed when needed
2. **Memory Efficient**: Uses iterators to avoid loading entire datasets into memory
3. **Short-Circuiting**: Operations like `.limit(10)` stop processing after enough results
4. **Streaming**: Can process files larger than available memory

## Design Principles

1. **Universal**: Query anything, anywhere with one consistent API
2. **Lazy**: Operations only execute when needed
3. **Chainable**: jQuery-style method chaining for readable queries
4. **Familiar**: SQL-like syntax that feels natural in Python
5. **Extensible**: Easy to add new data sources and operations
6. **Robust**: Graceful error handling and type safety