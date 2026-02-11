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
    
    # 2. Query a list of dictionaries (JSON-like data)
    print("2. Querying JSON-like data:")
    employees = [
        {"name": "Alice", "department": "Engineering", "salary": "90000", "age": "25"},
        {"name": "Bob", "department": "Marketing", "salary": "75000", "age": "30"},
        {"name": "Charlie", "department": "Engineering", "salary": "120000", "age": "35"},
        {"name": "Diana", "department": "Sales", "salary": "85000", "age": "28"}
    ]
    high_earners = (Q(employees)
                    .map({"salary": int, "age": int})
                    .where("salary", "gt", 80000)
                    .where("department", "eq", "Engineering")
                    .select(["name", "salary"], as_=["employee", "compensation"])
                    .order_by("compensation")
                    .to_list())
    print(f"   High-earning engineers: {high_earners}")
    print()
    
    # 3. Query CSV file directly
    print("3. Querying CSV file directly:")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("product,category,price,rating\n")
        f.write("Laptop,Electronics,1200.00,4.5\n")
        f.write("Phone,Electronics,800.00,4.7\n")
        f.write("Book,Education,20.00,4.8\n")
        f.write("Desk,Furniture,300.00,4.3\n")
        temp_csv = f.name
    
    try:
        affordable_electronics = (Q(temp_csv)
                                  .map({"price": float, "rating": float})
                                  .where("category", "eq", "Electronics")
                                  .where("price", "lt", 1000.0)
                                  .where("rating", "gt", 4.0)
                                  .select(["product", "price"], as_=["item", "cost"])
                                  .order_by("rating")
                                  .to_list())
        print(f"   Affordable electronics: {affordable_electronics}")
    finally:
        os.unlink(temp_csv)
    print()
    
    # 4. Query JSON file directly
    print("4. Querying JSON file directly:")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_data = [
            {"name": "John", "scores": [85, 92, 78]},
            {"name": "Jane", "scores": [95, 88, 96]},
            {"name": "Bob", "scores": [70, 80, 85]}
        ]
        json.dump(json_data, f)
        temp_json = f.name
    
    try:
        honor_students = (Q(temp_json)
                          .map(lambda x: {
                              "name": x["name"],
                              "average": sum(x["scores"]) / len(x["scores"])
                          })
                          .where("average", "gt", 85.0)
                          .select(["name", "average"], as_=["student", "avg_score"])
                          .order_by("avg_score")
                          .to_list())
        print(f"   Honor students: {honor_students}")
    finally:
        os.unlink(temp_json)
    print()
    
    # 5. Query list of lists (spreadsheet-like data)
    print("5. Querying spreadsheet-like data:")
    spreadsheet_data = [
        ["Name", "Department", "Age", "Salary"],
        ["Alice", "Engineering", "25", "90000"],
        ["Bob", "Marketing", "30", "75000"],
        ["Charlie", "Engineering", "35", "120000"]
    ]
    senior_engineers = (Q(spreadsheet_data)
                        .map({"Age": int, "Salary": int})
                        .where("Department", "eq", "Engineering")
                        .where("Age", "gt", 30)
                        .select(["Name", "Salary"], as_=["Engineer", "Compensation"])
                        .to_list())
    print(f"   Senior engineers: {senior_engineers}")
    print()
    
    # 6. Complex chained operations
    print("6. Complex chained operations:")
    financial_data = [
        {"date": "2023-01-15", "amount": "250.00", "category": "Shopping", "type": "Debit"},
        {"date": "2023-01-20", "amount": "1500.00", "category": "Salary", "type": "Credit"},
        {"date": "2023-01-25", "amount": "80.00", "category": "Dining", "type": "Debit"},
        {"date": "2023-02-15", "amount": "250.00", "category": "Shopping", "type": "Debit"},
        {"date": "2023-02-20", "amount": "1500.00", "category": "Salary", "type": "Credit"}
    ]
    
    monthly_expenses = (Q(financial_data)
                         .map({"amount": float, "month": lambda x: x["date"][:7]})
                         .where("type", "eq", "Debit")
                         .where("amount", "gt", 100.0)
                         .group_by("month")
                         .map(lambda group: {
                             "period": group[0],
                             "total_spent": sum(t["amount"] for t in group[1]),
                             "transactions": len(group[1])
                         })
                         .order_by("period")
                         .to_list())
    print(f"   Monthly expenses: {monthly_expenses}")
    print()
    
    print("✨ With pyql, you can query anything, anywhere, using one simple, chainable, lazy syntax!")
    print("   Stop converting. Stop boilerplate. Stop switching syntax.")
    print("   Query like you're speaking Python. 🐍")


if __name__ == "__main__":
    demonstrate_universal_querying()