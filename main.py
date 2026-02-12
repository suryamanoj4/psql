from src.pyql.pyql import Q


def main():
    # Example 1: Querying a list of numbers
    print("Example 1: Filtering numbers > 3")
    data = [1, 2, 3, 4, 5]
    result = Q(data).filter(lambda x: x['value'] > 3).to_list()
    print(result)  # [{'value': 4}, {'value': 5}]
    
    # Example 2: Querying JSON-like data
    print("\nExample 2: Selecting names of people over 25")
    json_data = [
        {"name": "Alice", "age": 25}, 
        {"name": "Bob", "age": 30}, 
        {"name": "Charlie", "age": 35}
    ]
    result = Q(json_data).where(lambda x: x["age"] > 25).select("name").to_list()
    print(result)  # [{"name": "Bob"}, {"name": "Charlie"}]
    
    # Example 3: Chaining operations
    print("\nExample 3: Chaining operations")
    result = Q(json_data).where(lambda x: x["age"] >= 30).order_by("age").select("name").to_list()
    print(result)  # [{"name": "Bob"}, {"name": "Charlie"}]
    
    # Example 4: Using map
    print("\nExample 4: Using map to transform data")
    result = Q(data).map(lambda x: x['value'] * 2).to_list()
    print(result)  # [{'value': 2}, {'value': 4}, ...]
    
    # Example 5: Using limit and skip
    print("\nExample 5: Using limit and skip")
    result = Q(json_data).skip(1).limit(1).to_list()
    print(result)  # [{"name": "Bob", "age": 30}]


if __name__ == "__main__":
    main()
