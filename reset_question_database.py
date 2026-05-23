#!/usr/bin/env python3
"""
Reset Question Database Script

This script resets all "seen" fields to False in a question database JSON file.
The file path is provided as a command-line parameter.

Usage:
    python reset_question_database.py <file_path>

Example:
    python reset_question_database.py data/questions.json
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Union


def reset_seen_fields(data: Union[Dict[str, Any], list]) -> None:
    """
    Recursively traverse the data structure and reset all 'seen' fields to False.
    
    Args:
        data: The data structure to traverse (dict or list)
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "seen":
                data[key] = False
            else:
                reset_seen_fields(value)
    elif isinstance(data, list):
        for item in data:
            reset_seen_fields(item)


def validate_file_path(file_path: str) -> Path:
    """
    Validate that the file path exists and is accessible.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Path object if valid
        
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file is not readable
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    if not path.suffix.lower() == '.json':
        print(f"Warning: File doesn't have .json extension: {file_path}")
    
    return path


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Load and parse the JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        json.JSONDecodeError: If file contains invalid JSON
        PermissionError: If file is not readable
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {file_path}: {e.msg}", e.doc, e.pos)
    except PermissionError:
        raise PermissionError(f"Permission denied reading file: {file_path}")


def save_json_file(file_path: Path, data: Dict[str, Any]) -> None:
    """
    Save the modified data back to the JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to save
        
    Raises:
        PermissionError: If file is not writable
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except PermissionError:
        raise PermissionError(f"Permission denied writing to file: {file_path}")


def count_seen_fields(data: Union[Dict[str, Any], list]) -> Dict[str, int]:
    """
    Count the number of 'seen' fields and their values.
    
    Args:
        data: The data structure to analyze
        
    Returns:
        Dictionary with counts of True/False seen fields
    """
    counts = {"true": 0, "false": 0, "total": 0}
    
    def _count_recursive(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == "seen":
                    counts["total"] += 1
                    if value:
                        counts["true"] += 1
                    else:
                        counts["false"] += 1
                else:
                    _count_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                _count_recursive(item)
    
    _count_recursive(data)
    return counts


def main():
    """Main function to handle command-line arguments and execute the reset."""
    parser = argparse.ArgumentParser(
        description="Reset all 'seen' fields to False in a question database JSON file.",
        epilog="Example: python reset_question_database.py data/questions.json"
    )
    parser.add_argument(
        "file_path",
        help="Path to the JSON file containing the question database"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without actually modifying the file"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create a backup of the original file before modifying"
    )
    
    args = parser.parse_args()
    
    try:
        # Validate file path
        file_path = validate_file_path(args.file_path)
        print(f"Processing file: {file_path}")
        
        # Load JSON data
        data = load_json_file(file_path)
        print("✓ JSON file loaded successfully")
        
        # Count current seen fields
        initial_counts = count_seen_fields(data)
        print(f"Found {initial_counts['total']} questions with 'seen' fields:")
        print(f"  - Currently seen: {initial_counts['true']}")
        print(f"  - Currently unseen: {initial_counts['false']}")
        
        if initial_counts['total'] == 0:
            print("No 'seen' fields found in the file.")
            return
        
        if args.dry_run:
            print("\n[DRY RUN] Would reset all 'seen' fields to False")
            if initial_counts['true'] > 0:
                print(f"[DRY RUN] Would change {initial_counts['true']} fields from True to False")
            else:
                print("[DRY RUN] All 'seen' fields are already False - no changes needed")
            return
        
        # Create backup if requested
        if args.backup:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
            print(f"✓ Backup created: {backup_path}")
        
        # Reset seen fields
        reset_seen_fields(data)
        
        # Verify the reset
        final_counts = count_seen_fields(data)
        
        # Save the modified data
        save_json_file(file_path, data)
        
        print(f"\n✓ Successfully reset {initial_counts['true']} 'seen' fields to False")
        print(f"✓ File updated: {file_path}")
        print(f"Final state: {final_counts['false']} unseen, {final_counts['true']} seen")
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()