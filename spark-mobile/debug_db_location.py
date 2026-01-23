"""Debug script to test database path detection on Android."""

import sys
from pathlib import Path

def test_db_paths():
    """Test all possible database paths."""
    print("\n" + "="*50)
    print("SPARK Database Location Detector")
    print("="*50 + "\n")

    results = []

    # Test 1: Primary external storage
    try:
        from android.storage import primary_external_storage_path
        storage_path = primary_external_storage_path()
        path1 = Path(storage_path) / 'SPARK' / 'spark.db'
        results.append(("Primary external storage", str(path1), "SHOULD WORK"))
        print(f"✓ Primary storage: {storage_path}")
        print(f"  → Database would be: {path1}")
    except Exception as e:
        results.append(("Primary external storage", "FAILED", str(e)))
        print(f"✗ Primary storage failed: {e}")

    # Test 2: App storage path
    try:
        from android.storage import app_storage_path
        app_path = app_storage_path()
        path2 = Path(app_path) / 'spark.db'
        results.append(("App internal storage", str(path2), "PRIVATE"))
        print(f"✓ App storage: {app_path}")
        print(f"  → Database would be: {path2}")
    except Exception as e:
        results.append(("App internal storage", "FAILED", str(e)))
        print(f"✗ App storage failed: {e}")

    # Test 3: Hard-coded fallback
    path3 = Path('/storage/emulated/0/SPARK/spark.db')
    results.append(("Hard-coded path", str(path3), "FALLBACK"))
    print(f"✓ Hard-coded: {path3}")

    # Test 4: Check what actually exists
    print("\n" + "-"*50)
    print("Checking which paths exist:")
    print("-"*50)

    for name, path_str, status in results:
        if path_str != "FAILED":
            path = Path(path_str).parent
            exists = path.exists()
            print(f"{name}: {'EXISTS' if exists else 'DOES NOT EXIST'}")
            if exists:
                print(f"  → Can write: {path.is_dir()}")

    print("\n" + "="*50)
    print("FINAL ANSWER:")
    print("="*50)

    # Determine actual path being used
    if sys.platform == 'android':
        try:
            from android.storage import primary_external_storage_path
            storage_path = primary_external_storage_path()
            final_path = Path(storage_path) / 'SPARK' / 'spark.db'
            print(f"Database location: {final_path}")
        except:
            final_path = Path('/storage/emulated/0/SPARK/spark.db')
            print(f"Database location (fallback): {final_path}")
    else:
        final_path = Path.cwd() / 'data' / 'spark.db'
        print(f"Database location (desktop): {final_path}")

    print("\nTo find this file on your device:")
    print("1. Open any file manager app")
    print("2. Look in Internal Storage root")
    print("3. Find the 'SPARK' folder")
    print("4. The database is 'spark.db' inside")
    print("="*50 + "\n")

    return final_path

if __name__ == '__main__':
    test_db_paths()
