# pyql Core Functionalities Implementation Roadmap

## Current State Assessment

### What We Have:
1. **Solid Foundation**: Core architecture with adapters, registry, and common representation
2. **Basic Query Engine**: Filter, where, select, map, order_by, group_by operations
3. **Multiple Data Sources**: Lists, dictionaries, CSV files, JSON files, list of lists
4. **Output Serialization**: to_list, to_dict, to_json, to_csv, to_df
5. **Basic Testing Framework**: Unit tests and integration tests

### Issues Identified:
1. **File Adapter Problems**: CSV and JSON file adapters not working correctly in tests
2. **Incomplete Features**: Some enhanced features from earlier work need integration
3. **Edge Case Handling**: Better error handling and type safety needed
4. **Performance Optimization**: Memory usage and processing speed improvements
5. **Documentation Gaps**: Missing API documentation and usage examples

## Revised Approach: From Scratch Implementation

### Key Principles:
1. **Zero External Dependencies**: Build everything from standard library only
2. **Maximum Laziness**: Everything should be lazy-evaluated by default
3. **Universal Compatibility**: Work with DFS, CSVs, JSONs, lists, and other popular data formats
4. **Extreme Simplicity**: User experience should be as simple as possible
5. **Future-Proof Design**: Easy to extend for DB connectivity and SQLAlchemy integration

## Core Functionalities to Implement/Enhance

### 1. Enhanced Query Operations

#### A. Advanced Filtering (`where`)
```python
# Current: Basic conditions (gt, lt, eq, in, etc.)
# Enhancement: Complex conditions and expressions
result = Q(data).where("age > 25 AND salary BETWEEN 50000 AND 100000").to_list()

# Regular expressions
result = Q(data).where("name", "matches", r"^A.*e$").to_list()

# Date/time operations
result = Q(data).where("created_at", "last_30_days").to_list()

# Null/None handling
result = Q(data).where("status", "is_null").to_list()
result = Q(data).where("status", "is_not_null").to_list()
```

#### B. Advanced Selection (`select`)
```python
# Current: Basic field selection and aliasing
# Enhancement: Calculated fields and expressions
result = Q(data).select([
    "name", 
    "age",
    {"full_name": lambda x: f"{x['first_name']} {x['last_name']}"},  # Calculated field
    {"annual_salary": "salary * 12"},  # Expression
    {"experience_level": "CASE WHEN age > 30 THEN 'Senior' ELSE 'Junior' END"}  # Conditional
]).to_list()
```

#### C. Advanced Mapping (`map`)
```python
# Current: Type casting and transformations
# Enhancement: Complex data transformations
result = Q(data).map({
    "created_at": datetime.fromisoformat,  # Custom parser
    "tags": lambda x: x.split(",") if x else [],  # Array parsing
    "coordinates": lambda x: {"lat": float(x["latitude"]), "lng": float(x["longitude"])},  # Nested structuring
    "nested": "json.loads",  # JSON deserialization
}).to_list()
```

### 2. Aggregation Functions

#### A. Basic Aggregations
```python
# COUNT, SUM, AVG, MIN, MAX
result = Q(data).aggregate({
    "total_records": "COUNT(*)",
    "total_salary": "SUM(salary)",
    "average_age": "AVG(age)",
    "min_salary": "MIN(salary)", 
    "max_salary": "MAX(salary)"
}).to_dict()
```

#### B. Grouped Aggregations
```python
# GROUP BY with aggregations
result = Q(data).group_by("department").aggregate({
    "employee_count": "COUNT(*)",
    "avg_salary": "AVG(salary)",
    "total_budget": "SUM(salary)"
}).to_list()
```

#### C. Window Functions
```python
# ROW_NUMBER, RANK, LAG, LEAD
result = Q(data).order_by("salary").window({
    "rank": "ROW_NUMBER() OVER (ORDER BY salary DESC)",
    "previous_salary": "LAG(salary, 1) OVER (ORDER BY hire_date)"
}).to_list()
```

### 3. Join Operations

#### A. Inner Joins
```python
# Join with another dataset
departments = [{"id": 1, "name": "Engineering"}, {"id": 2, "name": "Marketing"}]
employees = [{"name": "Alice", "dept_id": 1}, {"name": "Bob", "dept_id": 2}]

result = Q(employees).join(departments, on="dept_id=id").to_list()
# [{"name": "Alice", "dept_id": 1, "department_name": "Engineering"}, ...]
```

#### B. Left/Right Joins
```python
# LEFT JOIN
result = Q(employees).left_join(departments, on="dept_id=id").to_list()

# RIGHT JOIN  
result = Q(employees).right_join(departments, on="dept_id=id").to_list()
```

#### C. Self Joins and Cross Joins
```python
# Self join for hierarchical data
managers = Q(employees).self_join(on="manager_id=id").to_list()

# Cross join for Cartesian product
result = Q(dataset1).cross_join(dataset2).to_list()
```

### 4. Subqueries and Complex Queries

#### A. Subqueries in WHERE
```python
# IN with subquery
high_performers = Q(performances).where("score > 90").select("employee_id")
result = Q(employees).where("id", "in", high_performers).to_list()

# EXISTS with subquery
result = Q(employees).where("EXISTS", Q(projects).where("employee_id = employees.id")).to_list()
```

#### B. Derived Tables
```python
# Complex derived table
top_performers = Q(performances).where("score > 90").group_by("employee_id").select([
    "employee_id",
    {"avg_score": "AVG(score)"}
])

result = Q(employees).join(top_performers, on="id=employee_id").to_list()
```

### 5. Performance Optimizations

#### A. Query Planning and Optimization
```python
# Automatic query optimization
optimized_query = Q(large_dataset).where("age > 25").select("name").optimize()

# Index hints for large datasets
result = Q(large_dataset).index_hint("age_idx").where("age > 25").to_list()
```

#### B. Streaming Processing
```python
# Process large files without loading into memory
result = Q("huge_dataset.csv").stream().where("status = 'active'").take(1000).to_list()
```

#### C. Parallel Processing
```python
# Parallel processing for CPU-intensive operations
result = Q(large_dataset).parallel(4).map(complex_transformation).to_list()
```

### 6. Advanced Data Sources

#### A. Database Integration
```python
# Direct SQL query execution
result = Q("postgresql://user:pass@localhost/db").sql("SELECT * FROM users WHERE age > 25").to_list()

# ORM-style querying
result = Q(User.objects).where("age > 25").select("name, email").to_list()
```

#### B. API Integration
```python
# REST API querying
users = Q("https://api.example.com/users").where("active = true").to_list()

# GraphQL integration
result = Q("https://api.example.com/graphql").gql("{ users(active: true) { name email } }").to_list()
```

#### C. Streaming Data Sources
```python
# Kafka integration
messages = Q(KafkaConsumer("topic")).where("priority = 'high'").to_list()

# WebSocket streaming
live_data = Q(WebSocket("ws://localhost:8080/data")).to_list()
```

### 7. Schema and Validation

#### A. Schema Definition
```python
# Define schema for validation
schema = {
    "name": {"type": str, "required": True},
    "age": {"type": int, "min": 0, "max": 150},
    "email": {"type": str, "format": "email"}
}

validated_data = Q(raw_data).validate(schema).to_list()
```

#### B. Type Inference and Auto-conversion
```python
# Auto-detect and convert types
clean_data = Q(messy_data).infer_types().to_list()
# Automatically converts strings to appropriate types based on content
```

### 8. Error Handling and Debugging

#### A. Enhanced Error Reporting
```python
# Detailed error information
try:
    result = Q(bad_data).where("age > 'not_a_number'").to_list()
except QueryError as e:
    print(e.details)  # Shows exactly which record caused the error
```

#### B. Query Profiling
```python
# Performance profiling
profile = Q(large_dataset).where("complex_condition").profile()
print(profile.execution_time)
print(profile.memory_usage)
```

## Implementation Priority

### Phase 1: Foundation Strengthening (Week 1-2)
1. Fix file adapter issues - **ZERO DEPENDENCY APPROACH**
2. Improve error handling and type safety
3. Complete missing features from previous work
4. Enhance existing test coverage
5. Ensure all functionality uses only standard library

### Phase 2: Core Operations Enhancement (Week 3-4)
1. Advanced filtering and selection
2. Aggregation functions
3. Basic join operations
4. Performance optimizations
5. Maintain zero external dependencies

### Phase 3: Advanced Features (Week 5-6)
1. Subqueries and complex queries
2. Schema validation
3. Comprehensive error handling
4. Prepare foundation for DB connectivity (without implementing yet)

### Phase 4: Production Ready (Week 7-8)
1. Full test coverage
2. Documentation and examples
3. Performance benchmarking
4. Release preparation
5. Design interfaces for future DB connectivity

## Technical Considerations

### 1. Zero External Dependencies
- Use only Python standard library (collections, itertools, json, csv, etc.)
- Do not import or depend on pandas, numpy, or any third-party libraries
- Provide optional integration points for popular libraries (without requiring them)

### 2. Maximum Laziness
- All operations must be lazy-evaluated
- Use generators and iterators exclusively
- Only materialize data when explicitly requested (to_list(), to_json(), etc.)

### 3. Universal Compatibility
- Must work with:
  - Standard Python data structures (lists, dicts, tuples)
  - CSV files (using stdlib csv module)
  - JSON files (using stdlib json module)
  - File-like objects
  - Iterables/generators
  - Future: Database connections (design interfaces now)

### 4. Extreme Simplicity
- API should be intuitive for both SQL and Python developers
- Method chaining should feel natural
- Error messages should be clear and helpful
- Documentation should be comprehensive but accessible

### 5. Future-Proof Design
- Design clean interfaces for future database connectivity
- Prepare extension points for SQLAlchemy integration
- Ensure architecture supports streaming data sources
- Make it easy to add new data source adapters

## Success Metrics

### 1. Performance
- Query execution time < 100ms for datasets < 10K records
- Memory usage < 2x original dataset size
- Scalability to 1M+ records with streaming

### 2. Usability
- 90% of common use cases covered by intuitive APIs
- Comprehensive documentation with examples
- Minimal learning curve for SQL/Python developers

### 3. Reliability
- 99.9% uptime for stable data sources
- Graceful degradation for unstable sources
- Comprehensive error reporting and recovery

### 4. Independence
- Zero external dependencies
- Optional integration with popular libraries (pandas, sqlalchemy, etc.)
- Easy to install and use in any Python environment

### 5. Extensibility
- Plugin architecture for new data sources
- Custom operation registration
- Hook system for preprocessing/postprocessing
- Clean interfaces for future database connectivity