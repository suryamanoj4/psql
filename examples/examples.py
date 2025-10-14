"""
Comprehensive examples for pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def example_1_basic_operations():
    """Example 1: Basic operations with lists of numbers."""
    print("=== Example 1: Basic operations with lists of numbers ===")
    
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    
    # Filter even numbers
    evens = Q(numbers).filter(lambda x: x % 2 == 0).to_list()
    print(f"Even numbers: {evens}")
    
    # Square all numbers
    squares = Q(numbers).map(lambda x: x ** 2).to_list()
    print(f"Squares: {squares}")
    
    # First 5 numbers
    first_five = Q(numbers).limit(5).to_list()
    print(f"First 5 numbers: {first_five}")
    
    # Skip first 5 numbers
    skip_five = Q(numbers).skip(5).to_list()
    print(f"Skip first 5: {skip_five}")
    
    print()


def example_2_working_with_dicts():
    """Example 2: Working with lists of dictionaries."""
    print("=== Example 2: Working with lists of dictionaries ===")
    
    employees = [
        {"name": "Alice", "department": "Engineering", "salary": 90000, "age": 25},
        {"name": "Bob", "department": "Marketing", "salary": 75000, "age": 30},
        {"name": "Charlie", "department": "Engineering", "salary": 120000, "age": 35},
        {"name": "David", "department": "Sales", "salary": 95000, "age": 28},
        {"name": "Eve", "department": "Engineering", "salary": 110000, "age": 32}
    ]
    
    # Engineers only
    engineers = Q(employees).filter(lambda x: x["department"] == "Engineering").to_list()
    print(f"Engineers: {[e['name'] for e in engineers]}")
    
    # High earners (salary > 100k)
    high_earners = Q(employees).where(lambda x: x["salary"] > 100000).select("name").to_list()
    print(f"High earners: {high_earners}")
    
    # Names of employees ordered by age
    names_by_age = Q(employees).order_by("age").select("name").to_list()
    print(f"Names ordered by age: {names_by_age}")
    
    print()


def example_3_chaining_operations():
    """Example 3: Chaining multiple operations."""
    print("=== Example 3: Chaining multiple operations ===")
    
    products = [
        {"name": "Laptop", "category": "Electronics", "price": 1200, "rating": 4.5},
        {"name": "Phone", "category": "Electronics", "price": 800, "rating": 4.7},
        {"name": "Tablet", "category": "Electronics", "price": 500, "rating": 4.2},
        {"name": "Book", "category": "Education", "price": 20, "rating": 4.8},
        {"name": "Desk", "category": "Furniture", "price": 300, "rating": 4.3}
    ]
    
    # Get names of top-rated electronics under $1000
    result = (Q(products)
              .filter(lambda x: x["category"] == "Electronics")
              .filter(lambda x: x["price"] < 1000)
              .order_by(lambda x: -x["rating"])  # Negative for descending order
              .select("name")
              .limit(2)
              .to_list())
    
    print(f"Top-rated electronics under $1000: {result}")
    print()


def example_4_lazy_evaluation():
    """Example 4: Demonstrating lazy evaluation."""
    print("=== Example 4: Demonstrating lazy evaluation ===")
    
    def expensive_operation(x):
        print(f"Processing {x}")  # This will show when the operation actually runs
        return x * 2
    
    numbers = [1, 2, 3, 4, 5]
    
    # Create a query but don't execute it yet
    query = Q(numbers).map(expensive_operation).filter(lambda x: x > 5)
    print("Query created but not executed yet")
    
    # Now execute it
    print("Executing query:")
    result = query.to_list()
    print(f"Result: {result}")
    print()


def example_5_working_with_different_data_types():
    """Example 5: Working with different data types."""
    print("=== Example 5: Working with different data types ===")
    
    # Strings
    words = ["apple", "banana", "cherry", "date", "elderberry"]
    long_words = Q(words).filter(lambda x: len(x) > 5).to_list()
    print(f"Long words: {long_words}")
    
    # Nested data
    nested = [
        {"name": "Alice", "scores": [85, 92, 78]},
        {"name": "Bob", "scores": [90, 88, 95]},
        {"name": "Charlie", "scores": [70, 80, 85]}
    ]
    
    # Get average scores
    avg_scores = Q(nested).map(
        lambda x: {
            "name": x["name"], 
            "avg_score": sum(x["scores"]) / len(x["scores"])
        }
    ).to_list()
    
    print(f"Average scores: {avg_scores}")
    print()


def run_all_examples():
    """Run all examples."""
    print("Running comprehensive examples for pyql...\n")
    
    example_1_basic_operations()
    example_2_working_with_dicts()
    example_3_chaining_operations()
    example_4_lazy_evaluation()
    example_5_working_with_different_data_types()
    
    print("All examples completed! 🎉")


if __name__ == "__main__":
    run_all_examples()