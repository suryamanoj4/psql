"""
Comprehensive example showcasing all enhanced features of pyql
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def comprehensive_example():
    """Comprehensive example showcasing all enhanced features."""
    print("=== Comprehensive Example: Employee Data Analysis ===")
    
    # Sample data with mixed types (strings that should be numbers)
    employees = [
        {"name": "alice smith", "department": "engineering", "age": "25", "salary": "90000.50", "join_date": "2020-01-15"},
        {"name": "bob johnson", "department": "marketing", "age": "30", "salary": "75000.75", "join_date": "2019-03-22"},
        {"name": "charlie brown", "department": "engineering", "age": "35", "salary": "120000.00", "join_date": "2018-07-10"},
        {"name": "david wilson", "department": "sales", "age": "28", "salary": "95000.25", "join_date": "2021-05-30"},
        {"name": "eve davis", "department": "engineering", "age": "32", "salary": "110000.00", "join_date": "2019-11-17"},
        {"name": "frank miller", "department": "marketing", "age": "29", "salary": "80000.00", "join_date": "2020-09-12"}
    ]
    
    print("Original data:")
    for emp in employees:
        print(f"  {emp}")
    
    print("\n1. Type casting and data cleaning:")
    # Type cast age and salary fields
    cleaned_data = Q(employees).map({
        "age": int,
        "salary": float,
        "name": lambda x: x.title()  # Capitalize names
    }).to_list()
    
    print("Cleaned data:")
    for emp in cleaned_data:
        print(f"  {emp}")
    
    print("\n2. Filtering with enhanced where:")
    # Find engineers older than 30 with salary > 100000
    result = (Q(cleaned_data)
              .where("department", "eq", "engineering")
              .where("age", "gt", 30)
              .where("salary", "gt", 100000)
              .select(["name", "age", "salary"])
              .to_list())
    
    print("Engineers over 30 with salary > 100k:")
    for emp in result:
        print(f"  {emp}")
    
    print("\n3. Selecting with aliases:")
    # Select fields with more descriptive names
    result = (Q(cleaned_data)
              .select(["name", "department", "age", "salary"], 
                     as_=["full_name", "dept", "years", "annual_income"])
              .to_list())
    
    print("Data with aliased field names:")
    for emp in result:
        print(f"  {emp}")
    
    print("\n4. Complex transformations with map:")
    # Add computed fields
    result = (Q(cleaned_data)
              .map(lambda x: {
                  **x,
                  "salary": f"${x['salary']:,.2f}",  # Format salary
                  "age_group": "Senior" if x["age"] > 30 else "Junior"  # Add age group
              })
              .select(["name", "age_group", "salary"])
              .to_list())
    
    print("Data with formatted salary and age groups:")
    for emp in result:
        print(f"  {emp}")
    
    print("\n5. Chaining multiple operations:")
    # Complex query: High earners in engineering, sorted by salary, limited to top 2
    result = (Q(cleaned_data)
              .where("department", "eq", "engineering")
              .where("salary", "gt", 100000)
              .order_by(lambda x: -x["salary"])  # Descending order
              .limit(2)
              .select(["name", "salary"], as_=["engineer", "compensation"])
              .to_list())
    
    print("Top 2 highest paid engineers:")
    for emp in result:
        print(f"  {emp}")
    
    print("\n6. Grouping and aggregation (using map for transformation):")
    # Calculate average salary by department
    dept_groups = (Q(cleaned_data)
                   .group_by("department")
                   .map(lambda group: {
                       "department": group[0],
                       "count": len(group[1]),
                       "avg_salary": sum(emp["salary"] for emp in group[1]) / len(group[1])
                   })
                   .to_list())
    
    print("Average salary by department:")
    for dept in dept_groups:
        print(f"  {dept['department'].title()}: {dept['count']} employees, "
              f"Avg Salary: ${dept['avg_salary']:,.2f}")
    
    print("\nAll examples completed! 🎉")


if __name__ == "__main__":
    comprehensive_example()