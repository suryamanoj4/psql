"""
Examples for enhanced map method in pyql
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def example_enhanced_map():
    """Example showing the enhanced map method."""
    print("=== Enhanced Map Method Examples ===")
    
    # Using map with a transformation function
    print("1. Using map with a transformation function:")
    numbers = [1, 2, 3, 4, 5]
    result = Q(numbers).map(lambda x: x * 2).to_list()
    print(f"   Original: {numbers}")
    print(f"   Doubled:  {result}")
    
    # Using map with type casting
    print("\n2. Using map with type casting:")
    string_numbers = ["1", "2", "3", "4", "5"]
    result = Q(string_numbers).map(int).to_list()
    print(f"   Original: {string_numbers}")
    print(f"   Integers: {result}")
    
    # Using map with field-specific type casting
    print("\n3. Using map with field-specific type casting:")
    employees = [
        {"name": "Alice", "age": "25", "salary": "90000.50"},
        {"name": "Bob", "age": "30", "salary": "75000.75"},
        {"name": "Charlie", "age": "35", "salary": "120000.00"}
    ]
    result = Q(employees).map(int, field="age").map(float, field="salary").to_list()
    print(f"   Original: {employees}")
    print(f"   Typed:    {result}")
    
    # Using map with dict of field-specific functions
    print("\n4. Using map with dict of field-specific functions:")
    data = [
        {"name": "alice", "department": "engineering", "age": "25"},
        {"name": "bob", "department": "marketing", "age": "30"},
        {"name": "charlie", "department": "engineering", "age": "35"}
    ]
    result = Q(data).map({
        "name": lambda x: x.capitalize(),
        "department": lambda x: x.title(),
        "age": int
    }).to_list()
    print(f"   Original: {data}")
    print(f"   Formatted:{result}")
    
    # Using map with error handling
    print("\n5. Using map with error handling:")
    mixed_data = ["1", "2", "invalid", "4", "5.5", "not_a_number"]
    result = Q(mixed_data).map(float).to_list()
    print(f"   Original: {mixed_data}")
    print(f"   Floats:   {result}")
    
    # Using map for complex transformations
    print("\n6. Using map for complex transformations:")
    products = [
        {"name": "Laptop", "price": "1200.00", "rating": "4.5"},
        {"name": "Phone", "price": "800.00", "rating": "4.7"},
        {"name": "Tablet", "price": "500.00", "rating": "4.2"}
    ]
    result = Q(products).map({
        "price": lambda x: f"${float(x):.2f}",
        "rating": float
    }).to_list()
    print(f"   Original: {products}")
    print(f"   Formatted:{result}")
    
    print()


def example_comparison_map_vs_select():
    """Example comparing map and select usage."""
    print("=== Comparison: map vs select ===")
    
    employees = [
        {"name": "Alice", "age": "25", "department": "Engineering", "salary": "90000"},
        {"name": "Bob", "age": "30", "department": "Marketing", "salary": "75000"},
        {"name": "Charlie", "age": "35", "department": "Engineering", "salary": "120000"}
    ]
    
    # Using map to transform data
    print("1. Using map to type cast fields:")
    result = Q(employees).map(int, field="age").map(int, field="salary").to_list()
    print(f"   {result}")
    
    # Using select to extract fields (without transformation)
    print("\n2. Using select to extract fields:")
    result = Q(employees).select(["name", "age", "salary"]).to_list()
    print(f"   {result}")
    
    # Using map with dict for multiple transformations
    print("\n3. Using map with dict for multiple transformations:")
    result = Q(employees).map({
        "age": int,
        "salary": int,
        "name": lambda x: x.upper()
    }).to_list()
    print(f"   {result}")
    
    # Using select with aliases (but without type casting)
    print("\n4. Using select with aliases:")
    result = Q(employees).select(["name", "age", "salary"], as_=["full_name", "years", "annual_income"]).to_list()
    print(f"   {result}")
    
    print()


def run_all_examples():
    """Run all examples."""
    print("Running examples for enhanced map method in pyql...\n")
    
    example_enhanced_map()
    example_comparison_map_vs_select()
    
    print("All examples completed! 🎉")


if __name__ == "__main__":
    run_all_examples()