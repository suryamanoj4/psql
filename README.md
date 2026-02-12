# pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python

✨ Query anything. Anywhere. Like you're speaking Python.

Stop converting. Stop boilerplate. Stop switching syntax.

With pyql, you can query lists, JSON, CSVs, Excel files, Pandas DataFrames, APIs, databases, and streams — using one simple, chainable, lazy, jQuery-meets-SQL syntax.

## Features

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

## Usage

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

## Enhanced API

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

## Real-World Examples

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

## Contributing

Contributions are welcome! Please read our contributing guidelines.

## License

MIT