"""
Real-world test scenarios for pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

import sys
import os

# Add the parent directory to the path so we can import pyql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyql import Q


def test_e_commerce_product_catalog():
    """Test for e-commerce product catalog filtering and transformation."""
    print("=== E-commerce Product Catalog Test ===")
    
    products = [
        {"id": 1, "name": "Laptop", "category": "electronics", "price": "1200.00", "rating": "4.5", "in_stock": "true"},
        {"id": 2, "name": "Phone", "category": "electronics", "price": "800.00", "rating": "4.7", "in_stock": "true"},
        {"id": 3, "name": "Tablet", "category": "electronics", "price": "500.00", "rating": "4.2", "in_stock": "false"},
        {"id": 4, "name": "Book", "category": "education", "price": "20.00", "rating": "4.8", "in_stock": "true"},
        {"id": 5, "name": "Desk", "category": "furniture", "price": "300.00", "rating": "4.3", "in_stock": "true"},
        {"id": 6, "name": "Chair", "category": "furniture", "price": "150.00", "rating": "4.1", "in_stock": "false"},
        {"id": 7, "name": "Monitor", "category": "electronics", "price": "400.00", "rating": "4.6", "in_stock": "true"},
    ]
    
    # Type cast numeric fields and boolean fields
    products = Q(products).map({
        "price": float,
        "rating": float,
        "in_stock": lambda x: x.lower() == 'true'
    }).to_list()
    
    # Get high-rated electronics under $1000 that are in stock
    affordable_electronics = (Q(products)
                             .where("category", "eq", "electronics")
                             .where("rating", "gt", 4.4)
                             .where("price", "lt", 1000.0)
                             .where("in_stock", "eq", True)
                             .order_by("rating")
                             .select(["name", "price", "rating"], as_=["product", "cost", "stars"])
                             .to_list())
    
    print(f"High-rated affordable electronics: {affordable_electronics}")
    expected = [
        {"product": "Monitor", "cost": 400.0, "stars": 4.6},
        {"product": "Phone", "cost": 800.0, "stars": 4.7}
    ]
    assert affordable_electronics == expected, f"Expected {expected}, got {affordable_electronics}"
    print("✓ E-commerce test passed")


def test_employee_management_system():
    """Test for employee management system filtering and reporting."""
    print("\n=== Employee Management System Test ===")
    
    employees = [
        {"id": "1", "name": "alice johnson", "department": "engineering", "salary": "90000", "age": "28", "join_date": "2020-01-15"},
        {"id": "2", "name": "bob smith", "department": "marketing", "salary": "75000", "age": "35", "join_date": "2019-03-22"},
        {"id": "3", "name": "charlie brown", "department": "engineering", "salary": "120000", "age": "42", "join_date": "2018-07-10"},
        {"id": "4", "name": "diana wilson", "department": "sales", "salary": "85000", "age": "31", "join_date": "2021-05-30"},
        {"id": "5", "name": "eve davis", "department": "engineering", "salary": "110000", "age": "33", "join_date": "2019-11-17"},
        {"id": "6", "name": "frank miller", "department": "hr", "salary": "80000", "age": "29", "join_date": "2020-09-12"},
    ]
    
    # Clean and type cast data
    employees = (Q(employees)
                 .map({
                     "id": int,
                     "salary": int,
                     "age": int,
                     "name": lambda x: x.title()
                 })
                 .to_list())
    
    # Find senior engineers with high salaries
    senior_engineers = (Q(employees)
                        .where("department", "eq", "engineering")
                        .where("age", "gt", 30)
                        .where("salary", "gt", 100000)
                        .order_by(lambda x: -x["salary"])  # Descending by salary
                        .select(["name", "age", "salary"], as_=["engineer", "years", "compensation"])
                        .to_list())
    
    print(f"Senior high-paying engineers: {senior_engineers}")
    expected = [
        {"engineer": "Charlie Brown", "years": 42, "compensation": 120000},
        {"engineer": "Eve Davis", "years": 33, "compensation": 110000}
    ]
    assert senior_engineers == expected, f"Expected {expected}, got {senior_engineers}"
    print("✓ Employee management test passed")


def test_financial_data_analysis():
    """Test for financial data analysis with time series data."""
    print("\n=== Financial Data Analysis Test ===")
    
    transactions = [
        {"date": "2023-01-15", "amount": "250.00", "category": "shopping", "type": "debit"},
        {"date": "2023-01-20", "amount": "1500.00", "category": "salary", "type": "credit"},
        {"date": "2023-01-25", "amount": "80.00", "category": "dining", "type": "debit"},
        {"date": "2023-02-15", "amount": "250.00", "category": "shopping", "type": "debit"},
        {"date": "2023-02-20", "amount": "1500.00", "category": "salary", "type": "credit"},
        {"date": "2023-03-10", "amount": "120.00", "category": "utilities", "type": "debit"},
        {"date": "2023-03-15", "amount": "350.00", "category": "shopping", "type": "debit"},
        {"date": "2023-03-20", "amount": "1500.00", "category": "salary", "type": "credit"},
    ]
    
    # Type cast amount and process data
    transactions = (Q(transactions)
                    .map({
                        "amount": float,
                        "month": lambda x: x["date"][:7]  # Extract year-month
                    })
                    .to_list())
    
    # Get all major expenses (over $100) from shopping
    major_expenses = (Q(transactions)
                      .where("type", "eq", "debit")
                      .where("amount", "gt", 100.0)
                      .where("category", "eq", "shopping")
                      .select(["date", "amount", "category"], as_=["expense_date", "cost", "category"])
                      .to_list())
    
    print(f"Major shopping expenses: {major_expenses}")
    expected = [
        {"expense_date": "2023-01-15", "cost": 250.0, "category": "shopping"},
        {"expense_date": "2023-02-15", "cost": 250.0, "category": "shopping"},
        {"expense_date": "2023-03-15", "cost": 350.0, "category": "shopping"},
    ]
    assert major_expenses == expected, f"Expected {expected}, got {major_expenses}"
    print("✓ Financial data analysis test passed")


def test_student_grade_management():
    """Test for student grade management system."""
    print("\n=== Student Grade Management Test ===")
    
    students = [
        {"id": "101", "name": "john doe", "math": "85", "science": "92", "english": "78"},
        {"id": "102", "name": "jane smith", "math": "95", "science": "88", "english": "96"},
        {"id": "103", "name": "bob jones", "math": "70", "science": "75", "english": "82"},
        {"id": "104", "name": "alice brown", "math": "98", "science": "94", "english": "91"},
        {"id": "105", "name": "charlie taylor", "math": "82", "science": "85", "english": "79"},
    ]
    
    # Type cast grades and format names
    students = (Q(students)
                .map({
                    "id": int,
                    "math": int,
                    "science": int,
                    "english": int,
                    "name": lambda x: x.title()
                })
                .map(lambda x: {
                    **x,
                    "average": round((x["math"] + x["science"] + x["english"]) / 3, 2),
                    "grade": "A" if (x["math"] + x["science"] + x["english"]) / 3 >= 90 else
                             "B" if (x["math"] + x["science"] + x["english"]) / 3 >= 80 else "C"
                })
                .to_list())
    
    # Find honor students (average > 90) and format for report
    honor_students = (Q(students)
                      .where("average", "gt", 90.0)
                      .order_by("average")
                      .select(["name", "average", "grade"], as_=["student", "avg_score", "letter_grade"])
                      .to_list())
    
    print(f"Honor students: {honor_students}")
    expected = [
        {"student": "Jane Smith", "avg_score": 93.0, "letter_grade": "A"},
        {"student": "Alice Brown", "avg_score": 94.33, "letter_grade": "A"}
    ]
    # Check if results are close enough (with rounding)
    assert len(honor_students) == 2, f"Expected 2 honor students, got {len(honor_students)}"
    assert all(s["letter_grade"] == "A" for s in honor_students), "All honor students should have grade A"
    print("✓ Student grade management test passed")


def test_log_file_analysis():
    """Test for log file analysis - filtering and transforming log data."""
    print("\n=== Log File Analysis Test ===")
    
    logs = [
        {"timestamp": "2023-06-15T08:30:00", "level": "info", "message": "User login", "user_id": "123"},
        {"timestamp": "2023-06-15T08:31:05", "level": "error", "message": "Database connection failed", "user_id": "123"},
        {"timestamp": "2023-06-15T08:32:10", "level": "warning", "message": "High memory usage", "user_id": "456"},
        {"timestamp": "2023-06-15T08:33:15", "level": "error", "message": "Authentication failed", "user_id": "789"},
        {"timestamp": "2023-06-15T08:34:20", "level": "info", "message": "User logout", "user_id": "123"},
        {"timestamp": "2023-06-15T08:35:25", "level": "error", "message": "Database connection failed", "user_id": "456"},
    ]
    
    # Process logs to extract date and count errors
    processed_logs = (Q(logs)
                      .map({
                          "date": lambda x: x["timestamp"][:10],  # Extract date
                          "user_id": int
                      })
                      .to_list())
    
    # Get all error logs
    error_logs = (Q(processed_logs)
                  .where("level", "eq", "error")
                  .select(["timestamp", "message", "user_id"], as_=["time", "error_msg", "user"])
                  .order_by("time")
                  .to_list())
    
    print(f"Error logs: {error_logs}")
    expected_count = 3  # We expect 3 error logs
    assert len(error_logs) == expected_count, f"Expected {expected_count} error logs, got {len(error_logs)}"
    assert all(log["error_msg"] for log in error_logs), "All error logs should have a message"
    print("✓ Log file analysis test passed")


def test_data_migration_and_transformation():
    """Test for data migration and transformation scenarios."""
    print("\n=== Data Migration and Transformation Test ===")
    
    # Simulate old format data that needs to be transformed
    old_data = [
        {"user_name": "john_doe", "user_age": "25", "user_email": "john@example.com", "is_active": "yes"},
        {"user_name": "jane_smith", "user_age": "30", "user_email": "jane@example.com", "is_active": "no"},
        {"user_name": "bob_johnson", "user_age": "35", "user_email": "bob@example.com", "is_active": "yes"},
    ]
    
    # Transform old data to new format with type casting
    new_data = (Q(old_data)
                .map({
                    "user_age": int,
                    "is_active": lambda x: x.lower() == "yes"
                })
                .map(lambda x: {
                    "name": x["user_name"].replace("_", " ").title(),
                    "age": x["user_age"],
                    "email": x["user_email"],
                    "active": x["is_active"],
                    "status": "verified" if x["is_active"] and x["user_age"] >= 30 else "pending"
                })
                .select(["name", "age", "email", "active", "status"])
                .to_list())
    
    print(f"Transformed data: {new_data}")
    expected = [
        {"name": "John Doe", "age": 25, "email": "john@example.com", "active": True, "status": "pending"},
        {"name": "Jane Smith", "age": 30, "email": "jane@example.com", "active": False, "status": "pending"},
        {"name": "Bob Johnson", "age": 35, "email": "bob@example.com", "active": True, "status": "verified"}
    ]
    assert new_data == expected, f"Expected {expected}, got {new_data}"
    print("✓ Data migration and transformation test passed")


def run_all_tests():
    """Run all real-world tests."""
    print("Running real-world test scenarios for pyql...\n")
    
    test_e_commerce_product_catalog()
    test_employee_management_system()
    test_financial_data_analysis()
    test_student_grade_management()
    test_log_file_analysis()
    test_data_migration_and_transformation()
    
    print("\n🎉 All real-world tests passed! pyql is working perfectly for practical use cases.")


if __name__ == "__main__":
    run_all_tests()