"""
CLI module for pyql - The Universal, Lazy, Super-Friendly Querying Toolkit for Python
"""

import argparse
import json
import csv
import sys
from pathlib import Path
from typing import Any, Dict, List

from .pyql import Q


def load_data_from_file(filepath: str) -> List[Dict[str, Any]]:
    """Load data from various file formats."""
    path = Path(filepath)
    
    if path.suffix.lower() == '.json':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # If it's a list of objects, return as is
            if isinstance(data, list):
                return data
            # If it's a single object, wrap in a list
            else:
                return [data]
    elif path.suffix.lower() == '.csv':
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    else:
        # For other formats or if we can't determine, try to read as JSON first
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content.startswith('[') or content.startswith('{'):
                    data = json.loads(content)
                    if isinstance(data, list):
                        return data
                    else:
                        return [data]
        except json.JSONDecodeError:
            pass
        
        # If not JSON, return as a single-item list with raw content
        with open(filepath, 'r', encoding='utf-8') as f:
            return [{"content": f.read()}]


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PyQL - Universal, Lazy, Super-Friendly Querying Toolkit for Python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query a JSON file
  pyql data.json --where 'age > 25' --select 'name,age' --output json
  
  # Filter CSV data
  pyql data.csv --where 'status == "active"' --output csv
  
  # Chain operations
  pyql data.json --where 'age > 30' --select 'name,salary' --sort 'salary' --output table
  
  # Use custom filters
  pyql data.json --filter 'lambda x: x["age"] > 25 and x["salary"] > 50000'
        """
    )
    
    parser.add_argument(
        'input',
        help='Input file path or JSON string'
    )
    
    parser.add_argument(
        '--where',
        dest='where_conditions',
        action='append',
        help='Filter conditions (e.g., "age > 25", "name == Alice")'
    )
    
    parser.add_argument(
        '--select',
        help='Fields to select, comma-separated (e.g., "name,age")'
    )
    
    parser.add_argument(
        '--filter',
        help='Custom filter function as a lambda expression'
    )
    
    parser.add_argument(
        '--sort',
        help='Field to sort by'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of results'
    )
    
    parser.add_argument(
        '--output',
        choices=['json', 'csv', 'table', 'list'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--output-file',
        help='Output file path (default: stdout)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load data
        if Path(args.input).exists():
            data = load_data_from_file(args.input)
        else:
            # Treat as JSON string
            try:
                data = json.loads(args.input)
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError:
                print(f"Error: Input '{args.input}' is not a valid file or JSON string", file=sys.stderr)
                sys.exit(1)
        
        # Create queryable
        query = Q(data)
        
        # Apply filters
        if args.where_conditions:
            for condition in args.where_conditions:
                # Parse simple conditions like "field op value"
                parts = condition.strip().split(' ', 2)
                if len(parts) == 3:
                    field, op, value = parts
                    # Try to convert value to appropriate type
                    try:
                        # Try numeric conversion
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        # Keep as string, remove quotes if present
                        value = value.strip('"\'')
                    
                    # Map operators to pyql equivalents
                    op_map = {
                        '>': 'gt', '>=': 'ge', '<': 'lt', '<=': 'le',
                        '==': 'eq', '!=': 'ne', 'in': 'in', 'not': 'not_in'
                    }
                    pyql_op = op_map.get(op, 'eq')
                    query = query.where(field, pyql_op, value)
        
        # Apply custom filter
        if args.filter:
            try:
                # Evaluate the filter as a lambda function
                filter_func = eval(args.filter, {"__builtins__": {}})
                query = query.filter(filter_func)
            except Exception as e:
                print(f"Error evaluating filter: {e}", file=sys.stderr)
                sys.exit(1)
        
        # Apply selection
        if args.select:
            fields = [f.strip() for f in args.select.split(',')]
            query = query.select(fields)
        
        # Apply sorting
        if args.sort:
            query = query.order_by(args.sort)
        
        # Apply limit
        if args.limit:
            query = query.limit(args.limit)
        
        # Execute query and format output
        result = query.to_list()
        
        # Format output based on selected format
        output = ""
        if args.output == 'json':
            output = json.dumps(result, indent=2)
        elif args.output == 'csv':
            if result and isinstance(result[0], dict):
                output_lines = []
                fieldnames = result[0].keys()
                output_lines.append(','.join(fieldnames))
                for item in result:
                    row = []
                    for field in fieldnames:
                        value = item.get(field, "")
                        # Escape commas and quotes for CSV
                        if isinstance(value, str) and (',' in value or '"' in value or '\n' in value):
                            value = '"' + value.replace('"', '""') + '"'
                        row.append(str(value))
                    output_lines.append(','.join(row))
                output = '\n'.join(output_lines)
            else:
                output = "# No data or incompatible format for CSV"
        elif args.output == 'table':
            if result and isinstance(result[0], dict):
                # Create a simple ASCII table
                fieldnames = list(result[0].keys())
                col_widths = {}
                
                # Calculate column widths
                for field in fieldnames:
                    col_widths[field] = max(
                        len(field),
                        max(len(str(item.get(field, ""))) for item in result)
                    )
                
                # Create header
                header_parts = [field.ljust(col_widths[field]) for field in fieldnames]
                header = "| " + " | ".join(header_parts) + " |"
                
                separator_parts = ["-" * (col_widths[field] + 2) for field in fieldnames]
                separator = "|" + "+".join(separator_parts) + "|"
                
                # Create rows
                rows = [header, separator]
                for item in result:
                    row_parts = [str(item.get(field, "")).ljust(col_widths[field]) for field in fieldnames]
                    rows.append("| " + " | ".join(row_parts) + " |")
                
                output = "\n".join(rows)
            else:
                output = str(result)
        elif args.output == 'list':
            output = str(result)
        
        # Output result
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Results written to {args.output_file}")
        else:
            print(output)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()