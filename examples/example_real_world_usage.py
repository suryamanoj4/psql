"""
Real-world usage examples for src.pyql - showcasing the adapter system and common representation
"""

import sys
import os
import tempfile
import json

# Add the parent directory to the path so we can import src.pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pyql import Q


def example_data_normalization():
    """Example showing how different data formats get normalized to Iterator[Dict[str, Any]]."""
    print("=== Data Normalization Examples ===")
    
    # Example 1: List of primitives
    print("1. List of primitives:")
    data = [1, 2, 3, 4, 5]
    result = Q(data).to_list()
    print(f"   Input: {data}")
    print(f"   Normalized: {result}")
    print()
    
    # Example 2: List of dictionaries
    print("2. List of dictionaries:")
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    result = Q(data).to_list()
    print(f"   Input: {data}")
    print(f"   Normalized: {result}")
    print()
    
    # Example 3: Single dictionary
    print("3. Single dictionary:")
    data = {"name": "Charlie", "age": 35}
    result = Q(data).to_list()
    print(f"   Input: {data}")
    print(f"   Normalized: {result}")
    print()
    
    # Example 4: List of lists with headers
    print("4. List of lists with headers:")
    data = [["Name", "Age"], ["Alice", 25], ["Bob", 30]]
    result = Q(data).to_list()
    print(f"   Input: {data}")
    print(f"   Normalized: {result}")
    print()


def example_csv_file_integration():
    """Example showing CSV file integration."""
    print("=== CSV File Integration Example ===")
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name,age,salary\nAlice,25,50000\nBob,30,60000\nCharlie,35,70000\n")
        temp_csv = f.name
    
    try:
        print(f"Processing CSV file: {temp_csv}")
        
        # Query the CSV file directly
        result = (Q(temp_csv)
                  .where("age", "gt", 25)
                  .map({"age": int, "salary": int})
                  .where("salary", "gt", 55000)
                  .select(["name", "salary"], as_=["employee", "income"])
                  .order_by("income")
                  .to_list())
        
        print(f"Result: {result}")
        print()
    finally:
        os.unlink(temp_csv)


def example_json_file_integration():
    """Example showing JSON file integration."""
    print("=== JSON File Integration Example ===")
    
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_data = [
            {"name": "Alice", "department": "Engineering", "salary": "90000"},
            {"name": "Bob", "department": "Marketing", "salary": "75000"},
            {"name": "Charlie", "department": "Engineering", "salary": "120000"}
        ]
        json.dump(json_data, f)
        temp_json = f.name
    
    try:
        print(f"Processing JSON file: {temp_json}")
        
        # Query the JSON file directly
        result = (Q(temp_json)
                  .map({"salary": int})
                  .where("department", "eq", "Engineering")
                  .where("salary", "gt", 95000)
                  .select(["name", "salary"])
                  .to_list())
        
        print(f"Result: {result}")
        print()
    finally:
        os.unlink(temp_json)


def example_real_world_financial_data():
    """Real-world example with financial data processing."""
    print("=== Real-World Financial Data Example ===")
    
    # Simulate API response data - list of transactions
    transactions = [
        {"date": "2023-01-15", "amount": "120.50", "category": "food", "type": "debit"},
        {"date": "2023-01-16", "amount": "85.25", "category": "gas", "type": "debit"},
        {"date": "2023-01-17", "amount": "200.00", "category": "salary", "type": "credit"},
        {"date": "2023-01-18", "amount": "95.75", "category": "shopping", "type": "debit"},
        {"date": "2023-01-19", "amount": "150.30", "category": "salary", "type": "credit"},
    ]
    
    # Process the financial data
    processed_transactions = (Q(transactions)
                              .map({
                                  "amount": float,
                                  "month": lambda x: x["date"][:7]  # Extract year-month
                              })
                              .to_list())
    
    print("Processed transactions:")
    for trans in processed_transactions:
        print(f"  {trans}")
    
    # Find all debit transactions over $100
    large_debits = (Q(processed_transactions)
                    .where("type", "eq", "debit")
                    .where("amount", "gt", 100.0)
                    .order_by("amount")
                    .select(["date", "amount", "category"], as_=["date", "amount", "expense_type"])
                    .to_list())
    
    print(f"\nLarge debit transactions: {large_debits}")
    
    # Group by month and calculate totals
    monthly_totals = (Q(processed_transactions)
                      .group_by("month")
                      .map(lambda group: {
                          "month": group[0],
                          "total_debits": sum(t["amount"] for t in group[1] if t["type"] == "debit"),
                          "total_credits": sum(t["amount"] for t in group[1] if t["type"] == "credit"),
                          "net": sum(t["amount"] for t in group[1] if t["type"] == "credit") - 
                                sum(t["amount"] for t in group[1] if t["type"] == "debit")
                      })
                      .to_list())
    
    print(f"\nMonthly summaries: {monthly_totals}")
    print()


def example_mixed_data_processing():
    """Example showing processing of mixed data types."""
    print("=== Mixed Data Processing Example ===")
    
    # Simulate data from different sources
    user_data = [
        {"user_id": "1", "name": "Alice Johnson", "age": "25", "status": "active"},
        {"user_id": "2", "name": "Bob Smith", "age": "30", "status": "inactive"},
        {"user_id": "3", "name": "Charlie Brown", "age": "35", "status": "active"}
    ]
    
    activity_data = [
        {"user_id": "1", "action": "login", "timestamp": "2023-01-15T08:30:00"},
        {"user_id": "1", "action": "purchase", "timestamp": "2023-01-15T10:15:00"},
        {"user_id": "2", "action": "login", "timestamp": "2023-01-15T09:00:00"},
        {"user_id": "3", "action": "login", "timestamp": "2023-01-15T11:00:00"},
    ]
    
    # Process and combine data
    active_users = (Q(user_data)
                    .map({"age": int, "user_id": int})
                    .where("status", "eq", "active")
                    .to_list())
    
    print(f"Active users: {active_users}")
    
    # Count activities per user
    user_activity_counts = (Q(activity_data)
                            .group_by("user_id")
                            .map(lambda group: {
                                "user_id": group[0],
                                "activity_count": len(group[1])
                            })
                            .to_list())
    
    print(f"User activity counts: {user_activity_counts}")
    
    # Join user data with activity data (simple approach)
    combined_result = []
    for user in active_users:
        user_id = str(user["user_id"])
        activity_count = next((item["activity_count"] for item in user_activity_counts if item["user_id"] == user_id), 0)
        combined_result.append({
            "name": user["name"],
            "age": user["age"],
            "activity_count": activity_count
        })
    
    print(f"Combined result: {combined_result}")
    print()


def example_output_formats():
    """Example showing different output formats."""
    print("=== Output Formats Example ===")
    
    data = [
        {"name": "Alice", "age": "25", "department": "Engineering"},
        {"name": "Bob", "age": "30", "department": "Marketing"},
        {"name": "Charlie", "age": "35", "department": "Engineering"}
    ]
    
    # Process data
    processed = (Q(data)
                 .map({"age": int})
                 .where("age", "gt", 27)
                 .select(["name", "age"]))
    
    # Output in different formats
    print("As list:")
    print(f"  {processed.to_list()}")
    
    print("\nAs JSON:")
    print(f"  {processed.to_json()}")
    
    print("\nAs CSV:")
    print(f"  {repr(processed.to_csv())}")
    
    print()


def run_all_examples():
    """Run all examples."""
    print("Running real-world usage examples for src.pyql adapter system...\n")
    
    example_data_normalization()
    example_csv_file_integration()
    example_json_file_integration()
    example_real_world_financial_data()
    example_mixed_data_processing()
    example_output_formats()
    
    print("🎉 All real-world examples completed!")


if __name__ == "__main__":
    run_all_examples()