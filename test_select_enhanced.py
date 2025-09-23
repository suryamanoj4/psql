"""
Tests for enhanced select method in pyql
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def test_select_single_field():
    """Test select with single field."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    result = Q(data).select("name").to_list()
    assert result == ["Alice", "Bob"], f"Expected ['Alice', 'Bob'], got {result}"
    print("✓ Select single field test passed")


def test_select_single_field_with_alias():
    """Test select with single field and alias."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    result = Q(data).select("name", as_="full_name").to_list()
    expected = [{"full_name": "Alice"}, {"full_name": "Bob"}]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Select single field with alias test passed")


def test_select_multiple_fields():
    """Test select with multiple fields."""
    data = [{"name": "Alice", "age": 25, "city": "New York"}, {"name": "Bob", "age": 30, "city": "London"}]
    result = Q(data).select(["name", "age"]).to_list()
    expected = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Select multiple fields test passed")


def test_select_multiple_fields_with_alias():
    """Test select with multiple fields and aliases."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    result = Q(data).select(["name", "age"], as_=["full_name", "years"]).to_list()
    expected = [{"full_name": "Alice", "years": 25}, {"full_name": "Bob", "years": 30}]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Select multiple fields with aliases test passed")


def test_select_with_callable():
    """Test select with callable."""
    data = [{"name": "alice", "age": 25}, {"name": "bob", "age": 30}]
    result = Q(data).select(lambda x: x["name"].upper()).to_list()
    assert result == ["ALICE", "BOB"], f"Expected ['ALICE', 'BOB'], got {result}"
    print("✓ Select with callable test passed")


def test_select_missing_fields():
    """Test select with missing fields."""
    data = [{"name": "Alice", "age": 25}, {"name": "Bob"}]  # Second item missing "age"
    result = Q(data).select(["name", "age"]).to_list()
    expected = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": None}]
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Select missing fields test passed")


def run_all_tests():
    """Run all tests."""
    print("Running tests for enhanced select method...")
    test_select_single_field()
    test_select_single_field_with_alias()
    test_select_multiple_fields()
    test_select_multiple_fields_with_alias()
    test_select_with_callable()
    test_select_missing_fields()
    print("All enhanced select tests passed! 🎉")


if __name__ == "__main__":
    run_all_tests()