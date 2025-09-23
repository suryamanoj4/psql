"""
Tests for enhanced map method in pyql
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def test_map_with_function():
    """Test map with a transformation function."""
    data = [1, 2, 3, 4, 5]
    result = Q(data).map(lambda x: x * 2).to_list()
    assert result == [2, 4, 6, 8, 10], f"Expected [2, 4, 6, 8, 10], got {result}"
    print("✓ Map with function test passed")


def test_map_with_type_casting():
    """Test map with type casting."""
    data = ["1", "2", "3", "4", "5"]
    result = Q(data).map(int).to_list()
    assert result == [1, 2, 3, 4, 5], f"Expected [1, 2, 3, 4, 5], got {result}"
    print("✓ Map with type casting test passed")


def test_map_field_with_type_casting():
    """Test map with field-specific type casting."""
    data = [{"name": "Alice", "age": "25"}, {"name": "Bob", "age": "30"}]
    result = Q(data).map(int, field="age").to_list()
    expected = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Map field with type casting test passed")


def test_map_dict_with_functions():
    """Test map with dict of field-specific functions."""
    data = [{"name": "alice", "age": "25"}, {"name": "bob", "age": "30"}]
    result = Q(data).map({"name": lambda x: x.capitalize(), "age": int}).to_list()
    expected = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Map dict with functions test passed")


def test_map_with_error_handling():
    """Test map with error handling."""
    data = ["1", "2", "invalid", "4", "5"]
    result = Q(data).map(int).to_list()
    # Invalid values should be kept as is
    assert result == [1, 2, "invalid", 4, 5], f"Expected [1, 2, 'invalid', 4, 5], got {result}"
    print("✓ Map with error handling test passed")


def run_all_tests():
    """Run all tests."""
    print("Running tests for enhanced map method...")
    test_map_with_function()
    test_map_with_type_casting()
    test_map_field_with_type_casting()
    test_map_dict_with_functions()
    test_map_with_error_handling()
    print("All enhanced map tests passed! 🎉")


if __name__ == "__main__":
    run_all_tests()