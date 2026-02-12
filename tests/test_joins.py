import unittest
import os
import csv
from src.pyql import Q

class TestJoins(unittest.TestCase):

    def setUp(self):
        self.users = [
            {"id": 1, "name": "Alice", "dept_id": 101},
            {"id": 2, "name": "Bob", "dept_id": 102},
            {"id": 3, "name": "Charlie", "dept_id": 103},  # Dept 103 doesn't exist in depts
        ]
        
        self.depts = [
            {"id": 101, "dept_name": "Engineering", "location": "Building A"},
            {"id": 102, "dept_name": "HR", "location": "Building B"},
            {"id": 104, "dept_name": "Marketing", "location": "Building C"},
        ]
        
        self.projects = [
            {"code": "P1", "owner_id": 1, "title": "Alpha"},
            {"code": "P2", "owner_id": 2, "title": "Beta"},
        ]

    def test_inner_join_list_dicts(self):
        # Inner join users and depts on dept_id = id
        result = (Q(self.users)
                  .join(self.depts, left_on="dept_id", right_on="id", how="inner")
                  .to_list())
        
        self.assertEqual(len(result), 2) # Alice and Bob match
        
        alice_entry = next(r for r in result if r["name"] == "Alice")
        self.assertEqual(alice_entry["dept_name"], "Engineering")
        self.assertEqual(alice_entry["dept_id"], 101)
        self.assertEqual(alice_entry["id_joined"], 101) # 'id' from depts collided with 'id' from users

    def test_left_join_list_dicts(self):
        # Left join users and depts
        result = (Q(self.users)
                  .join(self.depts, left_on="dept_id", right_on="id", how="left")
                  .to_list())
        
        self.assertEqual(len(result), 3) # All 3 users
        
        charlie_entry = next(r for r in result if r["name"] == "Charlie")
        # Charlie has no matching dept, so dept fields shouldn't exist (or be handled as per logic)
        self.assertNotIn("dept_name", charlie_entry)

    def test_chained_join(self):
        # Join Users -> Depts -> Projects (join on user.id = project.owner_id)
        # Note: Users joined with Depts first.
        
        result = (Q(self.users)
                  .join(self.depts, left_on="dept_id", right_on="id")
                  .join(self.projects, left_on="id", right_on="owner_id")
                  .to_list())
        
        # Alice (id 1) -> Eng (101) -> Project P1 (owner 1)
        # Bob (id 2) -> HR (102) -> Project P2 (owner 2)
        
        self.assertEqual(len(result), 2)
        
        alice = next(r for r in result if r["name"] == "Alice")
        self.assertEqual(alice["title"], "Alpha")
        self.assertEqual(alice["dept_name"], "Engineering")

    def test_join_with_csv(self):
        # Create a temporary CSV
        csv_path = "temp_test_roles.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "role"])
            writer.writerow(["1", "Admin"])
            writer.writerow(["2", "User"])
        
        try:
            # Approach: Cast users id to string first to match CSV
            users_str_id = [{"id": str(u["id"]), "name": u["name"]} for u in self.users]
            
            result = (Q(users_str_id)
                      .join(csv_path, left_on="id", right_on="user_id")
                      .to_list())
            
            self.assertEqual(len(result), 2)
            admin = next(r for r in result if r["role"] == "Admin")
            self.assertEqual(admin["name"], "Alice")
            
        finally:
            if os.path.exists(csv_path):
                os.remove(csv_path)

if __name__ == "__main__":
    unittest.main()