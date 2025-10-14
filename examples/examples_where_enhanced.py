"""
Examples for enhanced where method in pyql
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def example_enhanced_where():
    """Example showing the enhanced where method."""
    print("=== Enhanced Where Method Examples ===")
    
    employees = [
        {"name": "Alice Smith", "department": "Engineering", "salary": 90000, "age": 25},
        {"name": "Bob Johnson", "department": "Marketing", "salary": 75000, "age": 30},
        {"name": "Charlie Brown", "department": "Engineering", "salary": 120000, "age": 35},
        {"name": "David Wilson", "department": "Sales", "salary": 95000, "age": 28},
        {"name": "Eve Davis", "department": "Engineering", "salary": 110000, "age": 32}
    ]
    
    # Using where with lambda (same as filter)
    print("1. High earners (salary > 100000):")
    result = Q(employees).where(lambda x: x["salary"] > 100000).select("name").to_list()
    print(f"   {result}")
    
    # Using where with gt condition
    print("\n2. Employees older than 30:")
    result = Q(employees).where("age", "gt", 30).select("name").to_list()
    print(f"   {result}")
    
    # Using where with lt condition
    print("\n3. Employees younger than 30:")
    result = Q(employees).where("age", "lt", 30).select("name").to_list()
    print(f"   {result}")
    
    # Using where with eq condition
    print("\n4. Employees in Engineering department:")
    result = Q(employees).where("department", "eq", "Engineering").select("name").to_list()
    print(f"   {result}")
    
    # Using where with ne condition
    print("\n5. Employees not in Engineering department:")
    result = Q(employees).where("department", "ne", "Engineering").select("name").to_list()
    print(f"   {result}")
    
    # Using where with ge condition
    print("\n6. Employees 30 or older:")
    result = Q(employees).where("age", "ge", 30).select("name").to_list()
    print(f"   {result}")
    
    # Using where with le condition
    print("\n7. Employees 30 or younger:")
    result = Q(employees).where("age", "le", 30).select("name").to_list()
    print(f"   {result}")
    
    # Using where with in condition
    print("\n8. Employees in Engineering or Marketing:")
    result = Q(employees).where("department", "in", ["Engineering", "Marketing"]).select("name").to_list()
    print(f"   {result}")
    
    # Using where with not_in condition
    print("\n9. Employees not in Engineering or Marketing:")
    result = Q(employees).where("department", "not_in", ["Engineering", "Marketing"]).select("name").to_list()
    print(f"   {result}")
    
    # Using where with contains condition
    print("\n10. Employees whose names contain 'son':")
    result = Q(employees).where("name", "contains", "son").select("name").to_list()
    print(f"    {result}")
    
    # Using where with starts_with condition
    print("\n11. Employees whose names start with 'A' or 'B':")
    result = Q(employees).where("name", "starts_with", "A").to_list() + \
             Q(employees).where("name", "starts_with", "B").to_list()
    result = [emp["name"] for emp in result]
    print(f"    {result}")
    
    # Using where with ends_with condition
    print("\n12. Employees whose names end with 'son' or 'is':")
    result = Q(employees).where("name", "ends_with", "son").to_list() + \
             Q(employees).where("name", "ends_with", "is").to_list()
    result = [emp["name"] for emp in result]
    print(f"    {result}")
    
    # Using where with only field name (checks for truthiness)
    print("\n13. Employees with non-empty names:")
    result = Q(employees).where("name").select("name").to_list()
    print(f"    {result}")
    
    print()


def example_comparison_with_filter():
    """Example comparing where and filter usage."""
    print("=== Comparison: where vs filter ===")
    
    products = [
        {"name": "Laptop", "category": "Electronics", "price": 1200, "rating": 4.5},
        {"name": "Phone", "category": "Electronics", "price": 800, "rating": 4.7},
        {"name": "Tablet", "category": "Electronics", "price": 500, "rating": 4.2},
        {"name": "Book", "category": "Education", "price": 20, "rating": 4.8},
        {"name": "Desk", "category": "Furniture", "price": 300, "rating": 4.3}
    ]
    
    # Using filter with lambda (more flexible but more verbose)
    print("1. Using filter with lambda:")
    result = Q(products).filter(lambda x: x["price"] > 500 and x["rating"] > 4.5).select("name").to_list()
    print(f"   {result}")
    
    # Using where with multiple conditions (more readable for simple conditions)
    print("\n2. Using where with multiple calls:")
    result = Q(products).where("price", "gt", 500).where("rating", "gt", 4.5).select("name").to_list()
    print(f"   {result}")
    
    # Complex condition with filter
    print("\n3. Complex condition with filter:")
    result = Q(products).filter(lambda x: x["category"] == "Electronics" and x["price"] < 1000).select("name").to_list()
    print(f"   {result}")
    
    # Same complex condition with where
    print("\n4. Same condition with where:")
    result = Q(products).where("category", "eq", "Electronics").where("price", "lt", 1000).select("name").to_list()
    print(f"   {result}")
    
    print()


def run_all_examples():
    """Run all examples."""
    print("Running examples for enhanced where method in pyql...\n")
    
    example_enhanced_where()
    example_comparison_with_filter()
    
    print("All examples completed! 🎉")


if __name__ == "__main__":
    run_all_examples()