"""
Final showcase of src.pyql capabilities
"""

import sys
import os

# Add the parent directory to the path so we can import src.pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pyql import Q


def showcase_src.pyql_power():
    """Showcase the power of src.pyql with a comprehensive example."""
    print("=== src.pyql: The Universal, Lazy, Super-Friendly Querying Toolkit ===")
    print()
    
    # Example 1: E-commerce data processing
    print("1. E-commerce Data Processing:")
    products = [
        {"id": "1", "name": "laptop", "category": "electronics", "price": "1200.00", "rating": "4.5", "in_stock": "true"},
        {"id": "2", "name": "phone", "category": "electronics", "price": "800.00", "rating": "4.7", "in_stock": "true"},
        {"id": "3", "name": "book", "category": "education", "price": "20.00", "rating": "4.8", "in_stock": "false"},
        {"id": "4", "name": "desk", "category": "furniture", "price": "300.00", "rating": "4.3", "in_stock": "true"},
    ]
    
    # Process with src.pyql
    affordable_electronics = (
        Q(products)
        .map({"price": float, "rating": float, "in_stock": lambda x: x.lower() == "true", "id": int})
        .where("category", "eq", "electronics")
        .where("price", "lt", 1000.0)
        .where("in_stock", "eq", True)
        .where("rating", "gt", 4.0)
        .select(["name", "price", "rating"], as_=["product", "cost", "stars"])
        .order_by("rating")
        .to_list()
    )
    
    print(f"   Affordable electronics: {affordable_electronics}")
    
    # Example 2: Employee management
    print("\n2. Employee Management:")
    employees = [
        {"name": "alice johnson", "age": "28", "salary": "90000", "dept": "engineering"},
        {"name": "bob smith", "age": "35", "salary": "75000", "dept": "marketing"},
        {"name": "charlie brown", "age": "42", "salary": "120000", "dept": "engineering"},
    ]
    
    senior_devs = (
        Q(employees)
        .map({"age": int, "salary": int, "name": lambda x: x.title()})
        .where("dept", "eq", "engineering")
        .where("age", "gt", 30)
        .map(lambda x: {**x, "is_senior": True})
        .select(["name", "age", "salary", "is_senior"])
        .to_list()
    )
    
    print(f"   Senior engineers: {senior_devs}")
    
    # Example 3: Financial data analysis
    print("\n3. Financial Data Analysis:")
    transactions = [
        {"date": "2023-01-15", "amount": "250.00", "type": "debit", "category": "shopping"},
        {"date": "2023-01-20", "amount": "1500.00", "type": "credit", "category": "salary"},
        {"date": "2023-01-25", "amount": "80.00", "type": "debit", "category": "dining"},
    ]
    
    monthly_summary = (
        Q(transactions)
        .map({"amount": float, "month": lambda x: x["date"][:7]})
        .where("type", "eq", "debit")
        .group_by("month")
        .map(lambda group: {
            "month": group[0],
            "total_expenses": sum(t["amount"] for t in group[1]),
            "transaction_count": len(group[1])
        })
        .to_list()
    )
    
    print(f"   Monthly expenses: {monthly_summary}")
    
    # Example 4: Student grade management
    print("\n4. Student Grade Management:")
    students = [
        {"name": "john doe", "math": "85", "science": "92", "english": "78"},
        {"name": "jane smith", "math": "95", "science": "88", "english": "96"},
    ]
    
    honor_students = (
        Q(students)
        .map({
            "math": int, "science": int, "english": int,
            "name": lambda x: x.title()
        })
        .map(lambda x: {
            **x,
            "average": round((x["math"] + x["science"] + x["english"]) / 3, 2),
            "grade": "A" if (x["math"] + x["science"] + x["english"]) / 3 >= 90 else "B"
        })
        .where("average", "gt", 85.0)
        .select(["name", "average", "grade"], as_=["student", "avg_score", "letter"])
        .to_list()
    )
    
    print(f"   Honor students: {honor_students}")
    
    print("\n✨ With src.pyql, you can query anything, anywhere, using one simple, chainable, lazy syntax!")
    print("   Stop converting. Stop boilerplate. Stop switching syntax.")
    print("   Query like you're speaking Python. 🐍")


if __name__ == "__main__":
    showcase_src.pyql_power()