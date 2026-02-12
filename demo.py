"""
Demonstration of pyql's universal querying capabilities
"""

import sys
import os
import tempfile
import json

# Add the parent directory to the path so we can import src.pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pyql import Q


def demonstrate_universal_querying():
    """Demonstrate pyql's ability to query anything, anywhere."""
    print("=== pyql: Universal Querying Demo ===")
    print()

    # 1. Query a simple list of numbers
    print("1. Querying a list of numbers:")
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    result = Q(numbers).filter(lambda x: x['value'] > 5).select("value").to_list()
    print(f"   Numbers > 5: {[r for r in result]}")
    print()

    # 2. Query JSON file directly (employees)
    print("2. Querying JSON file (employees):")
    employees_json = "examples/employees.json"
    high_earners = (Q(employees_json)
                    .map({"age": int, "salary": int})
                    .where("salary", "gt", 80000)
                    .where("status", "eq", "active")
                    .select(["name", "department", "salary"], as_=["employee", "dept", "compensation"])
                    .order_by("compensation")
                    .to_list())
    print(f"   High-earning active employees: {high_earners}")
    print()

    # 3. Query CSV file directly (products)
    print("3. Querying CSV file (products):")
    products_csv = "examples/products.csv"
    premium_electronics = (Q(products_csv)
                           .map({"price": float, "stock_quantity": int, "rating": float, "reviews_count": int})
                           .where("category", "eq", "Electronics")
                           .where("price", "gt", 500.0)  # Changed back to 500 for premium
                           .where("rating", "ge", 4.5)
                           .select(["product_name", "brand", "price", "rating"], as_=["item", "maker", "cost", "stars"])
                           .order_by("price")
                           .to_list())
    print(f"   Premium electronics: {premium_electronics}")
    print()

    # 4. Query JSON file (transactions) with complex operations
    print("4. Querying JSON file (transactions) with complex operations:")
    transactions_json = "examples/transactions.json"
    completed_transactions = (Q(transactions_json)
                              .map({"quantity": int, "unit_price": float, "total_amount": float,
                                   "discount_applied": float, "final_amount": float})
                              .where("status", "eq", "completed")
                              .where("final_amount", "gt", 500.0)
                              .select(["customer_name", "product_name", "final_amount", "payment_method"])
                              .order_by("final_amount")
                              .to_list())
    print(f"   High-value completed transactions: {completed_transactions}")
    print()

    # 5. Demonstrate JOIN functionality
    print("5. Demonstrating JOIN functionality:")
    # Inner join: products and their transactions
    product_transactions = (Q(products_csv)
                             .join(transactions_json, left_on="product_id", right_on="product_id", how="inner")
                             .where("status", "eq", "completed")
                             .select(["product_name", "category", "customer_name", "final_amount"])
                             .to_list())
    print(f"   Products with completed transactions: {len(product_transactions)} results")
    for item in product_transactions[:3]:  # Show first 3
        print(f"     {item}")
    print()

    # 6. Demonstrate LEFT JOIN functionality
    print("6. Demonstrating LEFT JOIN functionality:")
    all_products_with_transaction_info = (Q(products_csv)
                                         .left_join(transactions_json, left_on="product_id", right_on="product_id")
                                         .select(["product_name", "category", "customer_name", "final_amount"])
                                         .to_list())
    print(f"   All products (with transaction info if available): {len(all_products_with_transaction_info)} results")
    for item in all_products_with_transaction_info[:3]:  # Show first 3
        print(f"     {item}")
    print()

    # 7. Demonstrate RIGHT JOIN functionality
    print("7. Demonstrating RIGHT JOIN functionality:")
    all_transactions_with_product_info = (Q(products_csv)
                                         .right_join(transactions_json, left_on="product_id", right_on="product_id")
                                         .select(["product_name", "category", "customer_name", "final_amount", "status"])
                                         .to_list())
    print(f"   All transactions (with product info if available): {len(all_transactions_with_product_info)} results")
    for item in all_transactions_with_product_info[:3]:  # Show first 3
        print(f"     {item}")
    print()

    # 8. Demonstrate CROSS JOIN functionality
    print("8. Demonstrating CROSS JOIN functionality:")
    departments = [{"dept_name": "Engineering"}, {"dept_name": "Marketing"}, {"dept_name": "Sales"}]
    locations = [{"city": "New York"}, {"city": "San Francisco"}, {"city": "Austin"}]
    dept_location_combinations = (Q(departments)
                                  .cross_join(locations)
                                  .to_list())
    print(f"   Department-location combinations: {dept_location_combinations}")
    print()

    # 9. Demonstrate advanced filtering with multiple conditions
    print("9. Demonstrating advanced filtering with multiple conditions:")
    filtered_products = (Q(products_csv)
                         .map({"price": float, "stock_quantity": int, "rating": float})
                         .where("price", "between", [50.0, 500.0])  # Note: between would need to be implemented
                         .where("rating", "gte", 4.0)
                         .where("stock_quantity", "gt", 30)
                         .select(["product_name", "category", "price", "rating", "stock_quantity"])
                         .order_by("rating")
                         .limit(5)
                         .to_list())
    # Since 'between' is not implemented, let's use gt and lt
    filtered_products = (Q(products_csv)
                         .map({"price": float, "stock_quantity": int, "rating": float})
                         .where("price", "gt", 50.0)
                         .where("price", "lt", 500.0)
                         .where("rating", "ge", 4.0)
                         .where("stock_quantity", "gt", 30)
                         .select(["product_name", "category", "price", "rating", "stock_quantity"])
                         .order_by("rating")
                         .limit(5)
                         .to_list())
    print(f"   Mid-range highly-rated products in stock: {filtered_products}")
    print()

    # 10. Demonstrate GROUP BY and AGGREGATION (simulated)
    print("10. Demonstrating GROUP BY functionality:")
    # Group products by category and count
    products_by_category = (Q(products_csv)
                            .map({"price": float, "stock_quantity": int, "rating": float})
                            .group_by("category")
                            .to_list())
    print(f"   Products grouped by category: {len(products_by_category)} groups")
    for group in products_by_category[:3]:  # Show first 3 groups
        category, items = group
        print(f"     {category}: {len(items)} products")
    print()

    # 11. Demonstrate complex chained operations
    print("11. Demonstrating complex chained operations:")
    # Find top-selling products by category
    top_categories = (Q(transactions_json)
                      .map({"quantity": int, "unit_price": float, "total_amount": float,
                           "discount_applied": float, "final_amount": float})
                      .where("status", "eq", "completed")
                      .join(products_csv, left_on="product_id", right_on="product_id")
                      .select(["category", "product_name", "final_amount"])
                      .order_by("final_amount")
                      .limit(5)
                      .to_list())
    print(f"   Top transactions by amount: {top_categories}")
    print()

    # 12. Demonstrate output formats
    print("12. Demonstrating different output formats:")
    
    # JSON output
    json_result = Q(employees_json).where("department", "eq", "Engineering").to_json()
    print(f"   JSON output (first 100 chars): {json_result[:100]}...")
    
    # CSV output
    csv_result = Q(employees_json).where("age", "lt", 35).select(["name", "age", "department"]).to_csv()
    print(f"   CSV output (first 100 chars): {csv_result[:100]}...")
    print()

    print("✨ With pyql, you can query anything, anywhere, using one simple, chainable, lazy syntax!")
    print("   Stop converting. Stop boilerplate. Stop switching syntax.")
    print("   Query like you're speaking Python. 🐍")


def demonstrate_cli_equivalents():
    """Show equivalent CLI commands for the operations above."""
    print("\n=== CLI EQUIVALENT COMMANDS ===")
    print()
    print("# Query JSON file for high earners")
    print("pyql examples/employees.json --where 'salary > 80000' --where 'status == active' --select 'name,department,salary' --sort 'salary'")
    print()
    print("# Query CSV file for premium electronics")
    print("pyql examples/products.csv --where 'category == Electronics' --where 'price > 500.0' --select 'product_name,brand,price' --sort 'price'")
    print()
    print("# Filter transactions")
    print("pyql examples/transactions.json --where 'status == completed' --where 'final_amount > 500.0' --select 'customer_name,product_name,final_amount' --sort 'final_amount'")
    print()


if __name__ == "__main__":
    demonstrate_universal_querying()
    demonstrate_cli_equivalents()
