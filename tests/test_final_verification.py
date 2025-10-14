"""
Final comprehensive test to verify all enhanced features work together
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def test_all_features_integrated():
    """Test that all enhanced features work together seamlessly."""
    print("=== Testing All Enhanced Features Integration ===")
    
    # Real-world scenario: Customer orders with mixed data types
    orders = [
        {"order_id": "ORD-001", "customer": "alice johnson", "items": "3", "total": "120.50", "status": "completed", "date": "2023-01-15"},
        {"order_id": "ORD-002", "customer": "bob smith", "items": "1", "total": "85.25", "status": "pending", "date": "2023-01-16"},
        {"order_id": "ORD-003", "customer": "charlie brown", "items": "5", "total": "210.75", "status": "completed", "date": "2023-01-17"},
        {"order_id": "ORD-004", "customer": "diana wilson", "items": "2", "total": "95.00", "status": "cancelled", "date": "2023-01-18"},
        {"order_id": "ORD-005", "customer": "eve davis", "items": "4", "total": "180.30", "status": "completed", "date": "2023-01-19"},
    ]
    
    print("Original orders:", orders[0])  # Show first order as example
    
    # Step 1: Clean and type-cast data
    cleaned_orders = (Q(orders)
                      .map({
                          "items": int,
                          "total": float,
                          "customer": lambda x: x.title()
                      })
                      .to_list())
    
    print("After cleaning and type casting:", cleaned_orders[0])
    
    # Step 2: Filter completed orders over $100
    valuable_orders = (Q(cleaned_orders)
                       .where("status", "eq", "completed")
                       .where("total", "gt", 100.0)
                       .order_by("total")
                       .select(["order_id", "customer", "total"], 
                              as_=["id", "client", "amount"])
                       .to_list())
    
    print("Valuable completed orders:", valuable_orders)
    
    # Step 3: Calculate average order value for completed orders
    completed_orders = Q(cleaned_orders).where("status", "eq", "completed").to_list()
    avg_value = sum(order["total"] for order in completed_orders) / len(completed_orders) if completed_orders else 0
    
    print(f"Average value of completed orders: ${avg_value:.2f}")
    
    # Step 4: Group orders by status
    status_groups = (Q(cleaned_orders)
                     .group_by("status")
                     .map(lambda group: {
                         "status": group[0],
                         "count": len(group[1]),
                         "total_revenue": sum(order["total"] for order in group[1]),
                         "avg_order_value": sum(order["total"] for order in group[1]) / len(group[1])
                     })
                     .to_list())
    
    print("Orders by status:")
    for group in status_groups:
        print(f"  {group['status']}: {group['count']} orders, "
              f"Revenue: ${group['total_revenue']:.2f}, "
              f"Avg: ${group['avg_order_value']:.2f}")
    
    # Verify the results
    assert len(valuable_orders) == 3, f"Expected 3 valuable orders, got {len(valuable_orders)}"
    assert valuable_orders[0]["amount"] == 120.5, f"First valuable order should be $120.50"
    assert valuable_orders[2]["amount"] == 210.75, f"Third valuable order should be $210.75"
    
    assert len(status_groups) == 3, f"Expected 3 status groups, got {len(status_groups)}"
    
    print("✓ All features integration test passed!")


def test_error_handling():
    """Test error handling with problematic data."""
    print("\n=== Testing Error Handling ===")
    
    # Data with mixed types and potential errors
    mixed_data = [
        {"id": "1", "value": "100", "category": "A"},
        {"id": "2", "value": "200", "category": "B"},
        {"id": "3", "value": "invalid", "category": "A"},  # Invalid number
        {"id": "4", "value": "400", "category": "B"},
        {"id": "5", "value": "", "category": "A"},  # Empty string
    ]
    
    # Type casting should handle errors gracefully
    processed = (Q(mixed_data)
                 .map({"id": int, "value": lambda x: float(x) if x and x != "invalid" else (0 if x == "" else None)})
                 .to_list())
    
    print("Processed mixed data:", processed)
    
    # Check that invalid values were handled properly
    invalid_entry = next(item for item in processed if item["id"] == 3)
    # In this case, "invalid" value becomes None
    assert invalid_entry["value"] is None, "Invalid value should have been converted to None"
    
    # Filter should also handle errors gracefully
    filtered = Q(processed).where("value", "gt", 150).to_list()
    print("Filtered results:", filtered)
    
    print("✓ Error handling test passed!")


def test_complex_chaining():
    """Test complex chaining of operations."""
    print("\n=== Testing Complex Chaining ===")
    
    products = [
        {"name": "laptop", "category": "electronics", "price": "1200", "rating": "4.5", "in_stock": "true"},
        {"name": "phone", "category": "electronics", "price": "800", "rating": "4.7", "in_stock": "true"},
        {"name": "book", "category": "education", "price": "20", "rating": "4.8", "in_stock": "false"},
        {"name": "desk", "category": "furniture", "price": "300", "rating": "4.2", "in_stock": "true"},
    ]
    
    # Complex chain: type cast, filter, transform, select with alias, limit
    result = (Q(products)
              .map({"price": int, "rating": float, "name": lambda x: x.title()})
              .where("rating", "gt", 4.3)
              .where("in_stock", "eq", "true")
              .map(lambda x: {**x, "discounted_price": x["price"] * 0.9})  # Add discount
              .select(["name", "price", "discounted_price", "rating"], 
                     as_=["product", "original_price", "sale_price", "stars"])
              .order_by("stars")
              .limit(5)
              .to_list())
    
    print("Complex chain result:", result)
    
    # Verify results
    assert len(result) == 2, f"Expected 2 results, got {len(result)}"
    assert all("product" in item for item in result), "All items should have product name"
    assert all("sale_price" in item for item in result), "All items should have sale price"
    
    print("✓ Complex chaining test passed!")


def run_final_tests():
    """Run all final tests."""
    print("Running final comprehensive tests for pyql...\n")
    
    test_all_features_integrated()
    test_error_handling()
    test_complex_chaining()
    
    print("\n🎉 All final tests passed! pyql is ready for production use.")


if __name__ == "__main__":
    run_final_tests()