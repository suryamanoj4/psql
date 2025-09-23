"""
Tests for enhanced where method in pyql
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def test_where_with_lambda():
    """Test where with lambda function (should work like filter)."""
    data = [1, 2, 3, 4, 5]
    result = Q(data).where(lambda x: x > 3).to_list()
    assert result == [4, 5], f"Expected [4, 5], got {result}"
    print("✓ Where with lambda test passed")


def test_where_gt():
    """Test where with greater than condition."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where("age", "gt", 30).to_list()
    assert len(result) == 1 and result[0]["name"] == "Charlie", f"Expected Charlie, got {result}"
    print("✓ Where greater than test passed")


def test_where_lt():
    """Test where with less than condition."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where("age", "lt", 30).to_list()
    assert len(result) == 1 and result[0]["name"] == "Alice", f"Expected Alice, got {result}"
    print("✓ Where less than test passed")


def test_where_eq():
    """Test where with equals condition."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where("name", "eq", "Bob").to_list()
    assert len(result) == 1 and result[0]["name"] == "Bob", f"Expected Bob, got {result}"
    print("✓ Where equals test passed")


def test_where_ne():
    """Test where with not equals condition."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where("name", "ne", "Bob").to_list()
    assert len(result) == 2 and "Bob" not in [item["name"] for item in result], f"Expected Alice and Charlie, got {result}"
    print("✓ Where not equals test passed")


def test_where_ge():
    """Test where with greater than or equal condition."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where("age", "ge", 30).to_list()
    assert len(result) == 2 and all(item["age"] >= 30 for item in result), f"Expected Bob and Charlie, got {result}"
    print("✓ Where greater than or equal test passed")


def test_where_le():
    """Test where with less than or equal condition."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where("age", "le", 30).to_list()
    assert len(result) == 2 and all(item["age"] <= 30 for item in result), f"Expected Alice and Bob, got {result}"
    print("✓ Where less than or equal test passed")


def test_where_in():
    """Test where with in condition."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where("name", "in", ["Alice", "Charlie"]).to_list()
    assert len(result) == 2 and all(item["name"] in ["Alice", "Charlie"] for item in result), f"Expected Alice and Charlie, got {result}"
    print("✓ Where in test passed")


def test_where_not_in():
    """Test where with not in condition."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where("name", "not_in", ["Alice", "Charlie"]).to_list()
    assert len(result) == 1 and result[0]["name"] == "Bob", f"Expected Bob, got {result}"
    print("✓ Where not in test passed")


def test_where_contains():
    """Test where with contains condition."""
    data = [{"name": "Alice Smith", "age": 25}, {"name": "Bob Johnson", "age": 30}, {"name": "Charlie Brown", "age": 35}]
    result = Q(data).where("name", "contains", "Smith").to_list()
    assert len(result) == 1 and result[0]["name"] == "Alice Smith", f"Expected Alice Smith, got {result}"
    print("✓ Where contains test passed")


def test_where_starts_with():
    """Test where with starts_with condition."""
    data = [{"name": "Alice Smith", "age": 25}, {"name": "Bob Johnson", "age": 30}, {"name": "Charlie Brown", "age": 35}]
    result = Q(data).where("name", "starts_with", "Alice").to_list()
    assert len(result) == 1 and result[0]["name"] == "Alice Smith", f"Expected Alice Smith, got {result}"
    print("✓ Where starts with test passed")


def test_where_ends_with():
    """Test where with ends_with condition."""
    data = [{"name": "Alice Smith", "age": 25}, {"name": "Bob Johnson", "age": 30}, {"name": "Charlie Brown", "age": 35}]
    result = Q(data).where("name", "ends_with", "Johnson").to_list()
    assert len(result) == 1 and result[0]["name"] == "Bob Johnson", f"Expected Bob Johnson, got {result}"
    print("✓ Where ends with test passed")


def test_where_field_exists():
    """Test where with only field name (checks for truthiness)."""
    data = [{"name": "Alice", "age": 25}, {"name": "", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where("name").to_list()
    assert len(result) == 2 and all(item["name"] for item in result), f"Expected Alice and Charlie, got {result}"
    print("✓ Where field exists test passed")


def run_all_tests():
    """Run all tests."""
    print("Running tests for enhanced where method...")
    test_where_with_lambda()
    test_where_gt()
    test_where_lt()
    test_where_eq()
    test_where_ne()
    test_where_ge()
    test_where_le()
    test_where_in()
    test_where_not_in()
    test_where_contains()
    test_where_starts_with()
    test_where_ends_with()
    test_where_field_exists()
    print("All enhanced where tests passed! 🎉")


if __name__ == "__main__":
    run_all_tests()