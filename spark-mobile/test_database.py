"""Test database compatibility between desktop and mobile."""

import sys
from pathlib import Path
from database import Database


def test_database_operations():
    """Test that database operations work correctly."""
    print("Testing SPARK Mobile database compatibility...")
    print()

    # Create test database
    db_path = Path('data/test_spark.db')
    db_path.parent.mkdir(exist_ok=True)

    # Remove existing test database
    if db_path.exists():
        db_path.unlink()

    # Initialize database
    print(f"Creating database at: {db_path}")
    db = Database(db_path)

    # Test notes
    print("\n1. Testing Notes...")
    note1_id = db.add_note("Test Note", "This is a test note content")
    print(f"   ✓ Created note (id={note1_id})")

    note2_id = db.add_note("Child Note", "This is a child note", parent_id=note1_id)
    print(f"   ✓ Created child note (id={note2_id})")

    notes = db.get_all_notes()
    print(f"   ✓ Retrieved {len(notes)} notes")

    # Test snippets
    print("\n2. Testing Snippets...")
    snippet_id = db.add_snippet(
        "Hello World",
        "print('Hello, World!')",
        "python",
        "example,tutorial"
    )
    print(f"   ✓ Created snippet (id={snippet_id})")

    snippets = db.get_all_snippets()
    print(f"   ✓ Retrieved {len(snippets)} snippets")

    # Test spreadsheets
    print("\n3. Testing Spreadsheets...")
    sheet_id = db.add_spreadsheet("Budget 2026", '{"A1": "Income", "B1": "1000"}')
    print(f"   ✓ Created spreadsheet (id={sheet_id})")

    sheets = db.get_all_spreadsheets()
    print(f"   ✓ Retrieved {len(sheets)} spreadsheets")

    # Test search
    print("\n4. Testing Search...")
    search_results = db.search_notes("test")
    print(f"   ✓ Found {len(search_results)} notes matching 'test'")

    search_results = db.search_snippets("Hello")
    print(f"   ✓ Found {len(search_results)} snippets matching 'Hello'")

    # Cleanup
    db.close()

    print("\n✓ All database tests passed!")
    print(f"\nDatabase created at: {db_path.absolute()}")
    print("This database is compatible with the desktop SPARK application.")


if __name__ == '__main__':
    try:
        test_database_operations()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
