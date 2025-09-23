"""
Tests for pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def test_basic_filtering():
    """Test basic filtering functionality."""
    data = [1, 2, 3, 4, 5]
    result = Q(data).filter(lambda x: x > 3).to_list()
    assert result == [4, 5], f"Expected [4, 5], got {result}"
    print("✓ Basic filtering test passed")


def test_where_alias():
    """Test that where is an alias for filter."""
    data = [1, 2, 3, 4, 5]
    result1 = Q(data).filter(lambda x: x > 3).to_list()
    result2 = Q(data).where(lambda x: x > 3).to_list()
    assert result1 == result2, f"filter and where should produce the same result"
    print("✓ Where alias test passed")


def test_select():
    """Test select functionality."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    result = Q(data).select("name").to_list()
    assert result == ["Alice", "Bob"], f"Expected ['Alice', 'Bob'], got {result}"
    print("✓ Select test passed")


def test_map():
    """Test map functionality."""
    data = [1, 2, 3, 4, 5]
    result = Q(data).map(lambda x: x * 2).to_list()
    assert result == [2, 4, 6, 8, 10], f"Expected [2, 4, 6, 8, 10], got {result}"
    print("✓ Map test passed")


def test_limit():
    """Test limit functionality."""
    data = [1, 2, 3, 4, 5]
    result = Q(data).limit(3).to_list()
    assert result == [1, 2, 3], f"Expected [1, 2, 3], got {result}"
    print("✓ Limit test passed")


def test_skip():
    """Test skip functionality."""
    data = [1, 2, 3, 4, 5]
    result = Q(data).skip(2).to_list()
    assert result == [3, 4, 5], f"Expected [3, 4, 5], got {result}"
    print("✓ Skip test passed")


def test_order_by():
    """Test order_by functionality."""
    data = [{"name": "Bob", "age": 30}, {"name": "Alice", "age": 25}]
    result = Q(data).order_by("age").to_list()
    expected = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Order by test passed")


def test_chaining():
    """Test chaining multiple operations."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    result = Q(data).where(lambda x: x["age"] >= 30).order_by("age").select("name").to_list()
    assert result == ["Bob", "Charlie"], f"Expected ['Bob', 'Charlie'], got {result}"
    print("✓ Chaining test passed")


def test_to_dict():
    """Test to_dict functionality."""
    # Test with key-value pairs
    data = [("a", 1), ("b", 2)]
    result = Q(data).to_dict()
    expected = {"a": 1, "b": 2}
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test with dict items
    data = [{"key": "a", "value": 1}, {"key": "b", "value": 2}]
    result = Q(data).to_dict()
    expected = {"a": 1, "b": 2}
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ To dict test passed")


def run_all_tests():
    """Run all tests."""
    print("Running tests for pyql...")
    test_basic_filtering()
    test_where_alias()
    test_select()
    test_map()
    test_limit()
    test_skip()
    test_order_by()
    test_chaining()
    test_to_dict()
    print("All tests passed! 🎉")


if __name__ == "__main__":
    run_all_tests()