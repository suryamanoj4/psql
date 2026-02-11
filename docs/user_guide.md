# PyQL - The Universal, Lazy, Super-Friendly Querying Toolkit for Python

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Concepts](#core-concepts)
5. [API Reference](#api-reference)
6. [Advanced Features](#advanced-features)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Introduction

PyQL is a universal, lazy, super-friendly querying toolkit for Python that allows you to query lists, JSON, CSVs, Excel files, Pandas DataFrames, APIs, databases, and streams using one simple, chainable, jQuery-meets-SQL syntax.

### Key Features
- **Universal**: Query lists, JSON, CSVs, Excel files, Pandas DataFrames, APIs, databases, and streams
- **Lazy**: Operations are only executed when needed
- **Chainable**: jQuery-style method chaining for readable queries
- **Familiar**: SQL-like syntax that feels natural in Python
- **Extensible**: Easy to add new data sources and operations
- **Type-safe**: Built-in type casting and error handling

## Installation

```bash
pip install pyql
```

## Quick Start

```python
from pyql import Q

# Query a list
data = [1, 2, 3, 4, 5]
result = Q(data).filter(lambda x: x > 3).to_list()
# [4, 5]

# Query JSON data
json_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
result = Q(json_data).where(lambda x: x["age"] > 25).select("name").to_list()
# ["Bob"]
```

## Core Concepts

### Data Sources
PyQL supports multiple data sources through its adapter system:
- Lists of dictionaries
- Lists of primitives
- Lists of lists (with/without headers)
- CSV files
- JSON files
- Single dictionaries
- Any other data type (converted to single value)

### Lazy Evaluation
All operations in PyQL are lazy until materialized with `.to_*()` methods. This means:
- Operations are not executed until `.to_list()`, `.to_dict()`, etc. is called
- Memory efficient for large datasets
- Chain operations without performance penalty

### Common Internal Representation
All data is normalized to `Iterator[Dict[str, Any]]` internally, providing:
- Consistent interface regardless of source format
- Flexibility to handle sparse, heterogeneous, and nested data
- Memory efficiency through iterators

## API Reference

### Core Methods

- `Q(data)`: Create a queryable object from data
- `.filter(predicate)`: Filter elements based on a predicate function
- `.where(field, condition, value)`: Simple filter with intuitive syntax
- `.select(field, as_=alias)`: Select specific fields with optional aliasing
- `.map(func, field=name)`: Transform elements or type cast fields
- `.limit(n)`: Limit the number of results
- `.skip(n)`: Skip the first n results
- `.order_by(key)`: Sort results by a key
- `.group_by(key)`: Group elements by a key
- `.join(target, on|left_on/right_on, how)`: Join with another data source
- `.left_join(target, on|left_on/right_on)`: Left join with another data source
- `.right_join(target, on|left_on/right_on)`: Right join with another data source
- `.outer_join(target, on|left_on/right_on)`: Full outer join with another data source
- `.cross_join(target)`: Cross join (Cartesian product) with another data source
- `.to_list()`: Execute the query and return a list
- `.to_dict()`: Execute the query and return a dictionary
- `.to_json()`: Execute the query and return a JSON string
- `.to_csv()`: Execute the query and return a CSV string
- `.to_df()`: Execute the query and return a pandas DataFrame (if pandas is available)

### Enhanced `where` Method

The `where` method supports intuitive syntax for common filtering operations:

```python
# Using lambda (same as filter)
Q(data).where(lambda x: x["age"] > 25)

# Using condition operators
Q(data).where("age", "gt", 25)        # Greater than
Q(data).where("age", "lt", 30)        # Less than
Q(data).where("name", "eq", "Alice")  # Equals
Q(data).where("name", "ne", "Bob")    # Not equals
Q(data).where("age", "ge", 25)        # Greater than or equal
Q(data).where("age", "le", 30)        # Less than or equal
Q(data).where("name", "in", ["Alice", "Bob"])      # In list
Q(data).where("name", "not_in", ["Alice", "Bob"])  # Not in list
Q(data).where("name", "contains", "Al")            # Contains substring
Q(data).where("name", "starts_with", "A")          # Starts with
Q(data).where("name", "ends_with", "e")            # Ends with
```

### Enhanced `select` Method

The `select` method supports field aliasing:

```python
# Select single field
Q(data).select("name")

# Select single field with alias
Q(data).select("name", as_="full_name")

# Select multiple fields
Q(data).select(["name", "age"])

# Select multiple fields with aliases
Q(data).select(["name", "age"], as_=["full_name", "years"])
```

### Enhanced `map` Method

The `map` method supports type casting and field-specific transformations:

```python
# Transform each element
Q(data).map(lambda x: x * 2)

# Type cast each element
Q(string_numbers).map(int)

# Type cast specific field
Q(data).map(int, field="age")

# Transform multiple fields
Q(data).map({
    "name": lambda x: x.upper(),
    "age": int,
    "salary": float
})
```

### Enhanced `join` Method

The `join` method supports various types of joins between datasets:

```python
# Inner join (default)
result = Q(users).join(departments, left_on="dept_id", right_on="id").to_list()

# Left join
result = Q(users).left_join(departments, left_on="dept_id", right_on="id").to_list()

# Right join
result = Q(users).right_join(departments, left_on="dept_id", right_on="id").to_list()

# Full outer join
result = Q(users).outer_join(departments, left_on="dept_id", right_on="id").to_list()

# Cross join (Cartesian product)
colors = [{"color": "red"}, {"color": "blue"}]
sizes = [{"size": "small"}, {"size": "large"}]
result = Q(colors).cross_join(sizes).to_list()
# [{"color": "red", "size": "small"}, {"color": "red", "size": "large"}, ...]

# Join with different syntax options
result = Q(users).join(departments, on="dept_id=id").to_list()  # When field names are the same
```

## Advanced Features

### Complex Chaining
Operations can be chained together for complex queries:

```python
products = [
    {"name": "Laptop", "price": "1200.00", "rating": "4.5", "category": "electronics"},
    # ... more products
]

# Clean and filter products
result = (Q(products)
          .map({"price": float, "rating": float})  # Type cast
          .where("category", "eq", "electronics")   # Filter by category
          .where("rating", "gt", 4.0)              # Filter by rating
          .where("price", "lt", 1000.0)            # Filter by price
          .select(["name", "price"], as_=["product", "cost"])  # Select with alias
          .order_by("price")                       # Sort by price
          .to_list())
```

### Multiple Condition Groups
The `where` method supports SQL-like AND/OR chaining:

```python
# SQL: age > 18 OR salary > 20000
Q(data).where("age", "gt", 18).where("salary", "gt", 20000, or_=True)

# SQL: age > 18 AND (salary > 20000 OR dept == 'executive')
Q(data).where("age", "gt", 18).where([
    ("salary", "gt", 20000, or_=True),
    ("dept", "eq", "executive", or_=True)
])
```

### File-Based Queries
Query CSV and JSON files directly:

```python
# Query CSV file
result = (Q("data.csv")
          .map({"price": float, "rating": float})
          .where("category", "eq", "Electronics")
          .select(["product", "price"], as_=["item", "cost"])
          .to_list())

# Query JSON file
result = (Q("data.json")
          .where("status", "eq", "active")
          .select("name")
          .to_list())
```

## Best Practices

### 1. Leverage Lazy Evaluation
Take advantage of lazy evaluation by chaining operations before materializing:

```python
# Good: Chain operations before materializing
result = (Q(data)
          .filter(lambda x: x["age"] > 25)
          .select("name")
          .order_by("name")
          .to_list())

# Avoid: Materializing early
filtered = Q(data).filter(lambda x: x["age"] > 25).to_list()
selected = Q(filtered).select("name").to_list()
result = Q(selected).order_by("name").to_list()
```

### 2. Use Type Casting Early
Cast data types early in your chain to avoid runtime errors:

```python
# Good: Cast types early
result = (Q(data)
          .map({"age": int, "salary": float})  # Cast early
          .where("age", "gt", 25)
          .where("salary", "gt", 50000)
          .to_list())
```

### 3. Use Appropriate Filters
Filter data as early as possible to reduce the amount of data processed:

```python
# Good: Filter early
result = (Q(large_dataset)
          .where("status", "eq", "active")  # Filter first
          .select("name", "email")          # Then select
          .to_list())

# Less efficient: Select first
result = (Q(large_dataset)
          .select("name", "email")          # Select all records first
          .where("status", "eq", "active")  # Then filter
          .to_list())
```

### 4. Handle Errors Gracefully
PyQL handles most errors internally, but you should still validate inputs when possible:

```python
# Validate data before querying when possible
if isinstance(data, list) and len(data) > 0:
    result = Q(data).where("age", "gt", 25).to_list()
else:
    result = []
```

## Examples

### E-commerce Product Filtering
```python
products = [
    {"name": "Laptop", "price": "1200.00", "rating": "4.5", "category": "electronics"},
    # ... more products
]

# Clean and filter products
result = (Q(products)
          .map({"price": float, "rating": float})  # Type cast
          .where("category", "eq", "electronics")   # Filter by category
          .where("rating", "gt", 4.0)              # Filter by rating
          .where("price", "lt", 1000.0)            # Filter by price
          .select(["name", "price"], as_=["product", "cost"])  # Select with alias
          .order_by("price")                       # Sort by price
          .to_list())
```

### Employee Data Analysis
```python
employees = [
    {"name": "alice johnson", "salary": "90000", "department": "engineering"},
    # ... more employees
]

# Analyze employee data
high_earners = (Q(employees)
                .map({
                    "salary": int,
                    "name": lambda x: x.title()  # Format name
                })
                .where("salary", "gt", 100000)
                .where("department", "eq", "engineering")
                .select(["name", "salary"], as_=["engineer", "compensation"])
                .to_list())
```

### Join Operations Example
```python
users = [
    {"id": 1, "name": "Alice", "dept_id": 101},
    {"id": 2, "name": "Bob", "dept_id": 102},
    {"id": 3, "name": "Charlie", "dept_id": 103},  # Dept 103 doesn't exist in depts
]

departments = [
    {"id": 101, "dept_name": "Engineering", "location": "Building A"},
    {"id": 102, "dept_name": "HR", "location": "Building B"},
    {"id": 104, "dept_name": "Marketing", "location": "Building C"},  # No user has this dept
]

# Inner join - only matching records
inner_result = Q(users).join(departments, left_on="dept_id", right_on="id").to_list()

# Left join - all users, with department info where available
left_result = Q(users).left_join(departments, left_on="dept_id", right_on="id").to_list()

# Right join - all departments, with user info where available
right_result = Q(users).right_join(departments, left_on="dept_id", right_on="id").to_list()

# Full outer join - all users and all departments
outer_result = Q(users).outer_join(departments, left_on="dept_id", right_on="id").to_list()
```

### File Querying Example
```python
import tempfile
import csv
import json

# Query CSV file directly
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    writer = csv.writer(f)
    writer.writerow(["product", "category", "price", "rating"])
    writer.writerow(["Laptop", "Electronics", "1200.00", "4.5"])
    writer.writerow(["Phone", "Electronics", "800.00", "4.7"])
    temp_csv = f.name

result = (Q(temp_csv)
          .map({"price": float, "rating": float})
          .where("category", "eq", "Electronics")
          .where("price", "lt", 1000.0)
          .select(["product", "price"], as_=["item", "cost"])
          .to_list())
```

## CLI Usage

PyQL also provides a command-line interface for querying data files directly from the terminal:

### Installation
After installing PyQL, the CLI tool will be available as `pyql`.

### Basic Usage
```bash
# Query a JSON file
pyql data.json --where 'age > 25' --select 'name,age' --output json

# Filter CSV data
pyql data.csv --where 'status == "active"' --output csv

# Chain operations
pyql data.json --where 'age > 30' --select 'name,salary' --sort 'salary' --output table

# Use custom filters
pyql data.json --filter 'lambda x: x["age"] > 25 and x["salary"] > 50000'
```

### Available Options
- `--where`: Filter conditions (e.g., "age > 25", "name == Alice")
- `--select`: Fields to select, comma-separated (e.g., "name,age")
- `--filter`: Custom filter function as a lambda expression
- `--sort`: Field to sort by
- `--limit`: Limit number of results
- `--output`: Output format (json, csv, table, list) - default is json
- `--output-file`: Output file path (default: stdout)

### Examples
```bash
# Filter and select from a JSON file
pyql employees.json --where 'age > 30' --select 'name,department,salary' --output table

# Limit results from a CSV file
pyql sales.csv --where 'amount > 1000' --limit 10 --output csv

# Sort and format output as a table
pyql products.json --where 'category == electronics' --sort 'price' --output table
```

## Troubleshooting

### Common Issues

1. **Import Errors**: If you're getting import errors, make sure you're importing from the correct location:
   ```python
   # Correct import
   from pyql import Q
   ```

2. **Type Errors**: When using `map` for type casting, ensure the data can be converted:
   ```python
   # Safe type casting
   result = Q(data).map({"age": lambda x: int(x) if x else 0}).to_list()
   ```

3. **Field Access Errors**: When using `where` or `select`, ensure field names exist:
   ```python
   # Safe field access
   result = Q(data).where("optional_field", "is_not_null").to_list()
   ```

### Performance Tips

1. **Filter Early**: Apply filters as early as possible in your chain
2. **Limit Results**: Use `.limit(n)` when you only need a subset
3. **Avoid Unnecessary Operations**: Only perform transformations you actually need
4. **Use Appropriate Data Types**: Store data in appropriate types to avoid repeated casting

## Contributing

Contributions are welcome! Please read our contributing guidelines.

## License

MIT