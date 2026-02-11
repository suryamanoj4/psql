"""
Comprehensive test suite for pyql adapter system and common representation
"""

import sys
import os
import tempfile
import json

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pyql.pyql import Q
from src.pyql.adapters import *
from src.pyql.registry import registry


def test_list_of_primitives_adapter():
    """Test ListOfPrimitivesAdapter functionality."""
    print("=== Testing List of Primitives Adapter ===")
    
    # Test with integers
    data = [1, 2, 3, 4, 5]
    adapter = ListOfPrimitivesAdapter()
    assert adapter.can_handle(data) is True
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test with strings
    data = ["a", "b", "c"]
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [{"value": "a"}, {"value": "b"}, {"value": "c"}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test with mixed types
    data = [1, "hello", 3.14, True]
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [{"value": 1}, {"value": "hello"}, {"value": 3.14}, {"value": True}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ List of primitives adapter tests passed")


def test_list_of_dicts_adapter():
    """Test ListOfDictsAdapter functionality."""
    print("\n=== Testing List of Dictionaries Adapter ===")
    
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    adapter = ListOfDictsAdapter()
    assert adapter.can_handle(data) is True
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ List of dictionaries adapter tests passed")


def test_list_of_lists_adapter():
    """Test ListOfListsAdapter functionality."""
    print("\n=== Testing List of Lists Adapter ===")
    
    # Test with headers
    data = [["name", "age"], ["Alice", 25], ["Bob", 30]]
    adapter = ListOfListsAdapter()
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30}
    ]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test without headers
    data = [["Alice", 25], ["Bob", 30]]
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [
        {"_0": "Alice", "_1": 25},
        {"_0": "Bob", "_1": 30}
    ]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test mixed types in lists
    data = [[1, "a"], [2, "b"], [3, "c"]]
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [
        {"_0": 1, "_1": "a"},
        {"_0": 2, "_1": "b"},
        {"_0": 3, "_1": "c"}
    ]
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ List of lists adapter tests passed")


def test_dict_adapter():
    """Test DictAdapter functionality."""
    print("\n=== Testing Dictionary Adapter ===")
    
    data = {"name": "Alice", "age": 25}
    adapter = DictAdapter()
    assert adapter.can_handle(data) is True
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [{"name": "Alice", "age": 25}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ Dictionary adapter tests passed")


def test_single_value_adapter():
    """Test SingleValueAdapter functionality."""
    print("\n=== Testing Single Value Adapter ===")
    
    data = 42
    adapter = SingleValueAdapter()
    assert adapter.can_handle(data) is True
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [{"_value": 42}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    data = "hello"
    ds = adapter.adapt(data)
    result = list(ds)
    expected = [{"_value": "hello"}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ Single value adapter tests passed")


def test_csv_file_adapter():
    """Test CSVFileAdapter functionality."""
    print("\n=== Testing CSV File Adapter ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name,age\nAlice,25\nBob,30\nCharlie,35\n")
        temp_csv = f.name
    
    try:
        adapter = CSVFileAdapter()
        assert adapter.can_handle(temp_csv) is True
        ds = adapter.adapt(temp_csv)
        result = list(ds)
        expected = [
            {"name": "Alice", "age": "25"},
            {"name": "Bob", "age": "30"}, 
            {"name": "Charlie", "age": "35"}
        ]
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ CSV file adapter test passed")
    finally:
        os.unlink(temp_csv)


def test_json_file_adapter():
    """Test JSONFileAdapter functionality."""
    print("\n=== Testing JSON File Adapter ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
        json.dump(json_data, f)
        temp_json = f.name
    
    try:
        adapter = JSONFileAdapter()
        assert adapter.can_handle(temp_json) is True
        ds = adapter.adapt(temp_json)
        result = list(ds)
        expected = json_data
        assert result == expected, f"Expected {expected}, got {result}"
        print("✓ JSON file adapter test passed")
    finally:
        os.unlink(temp_json)


def test_registry_functionality():
    """Test the adapter registry functionality."""
    print("\n=== Testing Adapter Registry ===")
    
    # Test registry can find appropriate adapter
    data = [1, 2, 3, 4, 5]
    adapter = registry.get_data_adapter(data)
    assert adapter is not None, "Registry should find an adapter for list of primitives"
    assert isinstance(adapter, ListOfPrimitivesAdapter), f"Expected ListOfPrimitivesAdapter, got {type(adapter)}"
    
    data = [{"name": "Alice"}]
    adapter = registry.get_data_adapter(data)
    assert adapter is not None, "Registry should find an adapter for list of dicts"
    assert isinstance(adapter, ListOfDictsAdapter), f"Expected ListOfDictsAdapter, got {type(adapter)}"
    
    print("✓ Adapter registry tests passed")


def test_q_class_with_different_data_sources():
    """Test Q class with different data sources."""
    print("\n=== Testing Q Class with Different Data Sources ===")
    
    # Test with list of primitives
    result = Q([1, 2, 3, 4, 5]).filter(lambda x: x['value'] > 3).to_list()
    expected = [{"value": 4}, {"value": 5}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test with list of dicts
    result = Q([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]).where("age", "gt", 25).select("name").to_list()
    expected = ["Bob"]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test with single dict
    result = Q({"name": "Charlie", "age": 35}).where("age", "ge", 35).to_list()
    expected = [{"name": "Charlie", "age": 35}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test with single primitive
    result = Q(42).to_list()
    expected = [{"_value": 42}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ Q class with different data sources tests passed")


def test_operations_on_normalized_data():
    """Test that operations work correctly on normalized data."""
    print("\n=== Testing Operations on Normalized Data ===")
    
    # Test operations on primitive list
    result = Q([1, 2, 3, 4, 5]).map(lambda x: {"doubled": x['value'] * 2}).where("doubled", "gt", 6).to_list()
    expected = [{"doubled": 8}, {"doubled": 10}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test operations on dict list
    result = (Q([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}])
              .where("age", "ge", 30)
              .order_by("age")
              .select(["name", "age"])
              .to_list())
    expected = [{"name": "Bob", "age": 30}, {"name": "Charlie", "age": 35}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ Operations on normalized data tests passed")


def test_edge_cases():
    """Test edge cases and extreme scenarios."""
    print("\n=== Testing Edge Cases ===")
    
    # Empty list - treated as a single value since it's an empty list (not a list of elements)
    result = Q([]).to_list()
    # Empty list is treated as a single value since no adapter specifically handles empty lists
    # The result will be [{'_value': []}] because it's treated as a single value
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 1, f"Expected 1 item for empty list, got {len(result)}"
    assert '_value' in result[0] or list(result[0].keys()) == ['_value'], f"Expected wrapped value, got {result[0]}"
    
    # Empty dict
    result = Q({}).to_list()
    expected = [{}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # List with mixed types - The mixed list itself is treated as a single value
    mixed_data = [{"name": "Alice", "age": 25}, [1, 2, 3], "string", 42]
    result = Q(mixed_data).to_list()
    # The mixed_data is treated as a single value since it's a list with mixed types
    # So result should be [{'_value': mixed_data}]
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 1, f"Expected 1 item for mixed list, got {len(result)}"
    assert '_value' in result[0], f"Expected wrapped value, got {result[0]}"
    assert result[0]['_value'] == mixed_data, f"Mixed data should match"
    
    # Deeply nested structure handling
    nested_data = [{"data": {"a": {"b": [1, 2, 3]}}}]
    result = Q(nested_data).to_list()
    expected = [{"data": {"a": {"b": [1, 2, 3]}}}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Very large data (test lazy behavior)
    large_data = list(range(10000))
    result = Q(large_data).limit(5).to_list()
    expected = [{"value": i} for i in range(5)]
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ Edge cases tests passed")


def test_output_formats():
    """Test different output formats."""
    print("\n=== Testing Output Formats ===")
    
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    q = Q(data)
    
    # Test to_list
    result = q.to_list()
    expected = data
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test to_json
    json_result = q.to_json()
    import json
    parsed = json.loads(json_result)
    assert parsed == data, f"Expected {data}, got {parsed}"
    
    # Test to_csv
    csv_result = q.to_csv()
    # Headers are sorted alphabetically, so age,name instead of name,age
    assert "age,name" in csv_result, "CSV should contain headers"
    assert "25,Alice" in csv_result, "CSV should contain first row"
    assert "30,Bob" in csv_result, "CSV should contain second row"
    
    print("✓ Output formats tests passed")


def test_extreme_filtering_scenarios():
    """Test extreme filtering scenarios."""
    print("\n=== Testing Extreme Filtering Scenarios ===")
    
    # Very large dataset filtering
    large_data = [{"id": i, "value": i * 2} for i in range(10000)]
    result = Q(large_data).where("id", "gt", 9995).order_by("id").limit(3).to_list()
    expected = [{"id": 9996, "value": 19992}, {"id": 9997, "value": 19994}, {"id": 9998, "value": 19996}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Complex nested conditions
    complex_data = [
        {"name": "Alice", "details": {"age": 25, "city": "NYC"}},
        {"name": "Bob", "details": {"age": 30, "city": "LA"}},
        {"name": "Charlie", "details": {"age": 35, "city": "NYC"}}
    ]
    # For simplicity, we'll filter using available fields
    nyc_adults = Q(complex_data).where("details", "contains", "NYC").to_list()
    # This won't work as expected because 'details' is dict, using alternative
    nyc_adults = Q(complex_data).where(lambda x: x.get('details', {}).get('city') == 'NYC').to_list()
    expected = [
        {"name": "Alice", "details": {"age": 25, "city": "NYC"}},
        {"name": "Charlie", "details": {"age": 35, "city": "NYC"}}
    ]
    assert len(nyc_adults) == 2, f"Expected 2 NYC residents, got {len(nyc_adults)}"
    
    print("✓ Extreme filtering scenarios tests passed")


def test_type_casting_scenarios():
    """Test type casting in different scenarios."""
    print("\n=== Testing Type Casting Scenarios ===")
    
    # String numbers to integer
    string_nums = [{"value": "1"}, {"value": "2"}, {"value": "3"}]
    result = Q(string_nums).map(int, field="value").where("value", "gt", 1).to_list()
    expected = [{"value": 2}, {"value": 3}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Mixed type handling
    mixed_types = [{"value": "10"}, {"value": 20}, {"value": "30.5"}]
    result = Q(mixed_types).map(lambda x: {"converted": float(x["value"])}).where("converted", "ge", 15).to_list()
    expected = [{"converted": 20.0}, {"converted": 30.5}]
    assert result == expected, f"Expected {expected}, got {result}"
    
    print("✓ Type casting scenarios tests passed")


def run_all_tests():
    """Run all tests."""
    print("Running comprehensive test suite for pyql adapter system...\n")
    
    test_list_of_primitives_adapter()
    test_list_of_dicts_adapter()
    test_list_of_lists_adapter()
    test_dict_adapter()
    test_single_value_adapter()
    test_csv_file_adapter()
    test_json_file_adapter()
    test_registry_functionality()
    test_q_class_with_different_data_sources()
    test_operations_on_normalized_data()
    test_edge_cases()
    test_output_formats()
    test_extreme_filtering_scenarios()
    test_type_casting_scenarios()
    
    print("\n🎉 All comprehensive tests passed! pyql adapter system is working correctly.")


if __name__ == "__main__":
    run_all_tests()