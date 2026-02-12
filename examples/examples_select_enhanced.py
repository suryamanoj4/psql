"""
Examples for enhanced select method with as_ parameter in src.pyql
"""

import sys
import os

# Add the parent directory to the path so we can import src.pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pyql import Q


def example_enhanced_select():
    """Example showing the enhanced select method with as_ parameter."""
    print("=== Enhanced Select Method Examples ===")
    
    employees = [
        {"name": "Alice Smith", "department": "Engineering", "salary": 90000, "age": 25, "city": "New York"},
        {"name": "Bob Johnson", "department": "Marketing", "salary": 75000, "age": 30, "city": "London"},
        {"name": "Charlie Brown", "department": "Engineering", "salary": 120000, "age": 35, "city": "Paris"},
        {"name": "David Wilson", "department": "Sales", "salary": 95000, "age": 28, "city": "Tokyo"},
        {"name": "Eve Davis", "department": "Engineering", "salary": 110000, "age": 32, "city": "Berlin"}
    ]
    
    # Using select with single field
    print("1. Selecting names only:")
    result = Q(employees).select("name").to_list()
    print(f"   {result}")
    
    # Using select with single field and alias
    print("\n2. Selecting name with alias:")
    result = Q(employees).select("name", as_="full_name").to_list()
    print(f"   {result}")
    
    # Using select with multiple fields
    print("\n3. Selecting name and salary:")
    result = Q(employees).select(["name", "salary"]).to_list()
    print(f"   {result}")
    
    # Using select with multiple fields and aliases
    print("\n4. Selecting name and salary with aliases:")
    result = Q(employees).select(["name", "salary"], as_=["full_name", "annual_income"]).to_list()
    print(f"   {result}")
    
    # Using select with callable
    print("\n5. Selecting with transformation (uppercase names):")
    result = Q(employees).select(lambda x: x["name"].upper()).to_list()
    print(f"   {result}")
    
    # Using select with callable to create new computed field
    print("\n6. Selecting with computed field (salary in thousands):")
    result = Q(employees).select(lambda x: {"name": x["name"], "salary_k": x["salary"] // 1000}).to_list()
    print(f"   {result}")
    
    # Using select with missing fields (handling gracefully)
    print("\n7. Selecting fields when some items might be missing them:")
    data_with_missing = [
        {"name": "Alice", "age": 25, "department": "Engineering"},
        {"name": "Bob", "age": 30},  # Missing department
        {"name": "Charlie", "department": "Marketing"}  # Missing age
    ]
    result = Q(data_with_missing).select(["name", "age", "department"]).to_list()
    print(f"   {result}")
    
    print()


def example_comparison_select_vs_map():
    """Example comparing select and map usage."""
    print("=== Comparison: select vs map ===")
    
    products = [
        {"name": "Laptop", "category": "Electronics", "price": 1200, "rating": 4.5},
        {"name": "Phone", "category": "Electronics", "price": 800, "rating": 4.7},
        {"name": "Tablet", "category": "Electronics", "price": 500, "rating": 4.2},
        {"name": "Book", "category": "Education", "price": 20, "rating": 4.8},
        {"name": "Desk", "category": "Furniture", "price": 300, "rating": 4.3}
    ]
    
    # Using select to extract fields
    print("1. Using select to extract fields:")
    result = Q(products).select(["name", "price"]).to_list()
    print(f"   {result}")
    
    # Using map to transform data (more flexible but more verbose)
    print("\n2. Using map to achieve similar result:")
    result = Q(products).map(lambda x: {"name": x["name"], "price": x["price"]}).to_list()
    print(f"   {result}")
    
    # Using select with field renaming
    print("\n3. Using select with field renaming:")
    result = Q(products).select(["name", "price"], as_=["product_name", "cost"]).to_list()
    print(f"   {result}")
    
    # Using map to achieve similar result
    print("\n4. Using map to achieve similar result:")
    result = Q(products).map(lambda x: {"product_name": x["name"], "cost": x["price"]}).to_list()
    print(f"   {result}")
    
    print()


def run_all_examples():
    """Run all examples."""
    print("Running examples for enhanced select method in src.pyql...\n")
    
    example_enhanced_select()
    example_comparison_select_vs_map()
    
    print("All examples completed! 🎉")


if __name__ == "__main__":
    run_all_examples()