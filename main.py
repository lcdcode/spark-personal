"""
Main entry point for SPARK Personal application.
This file is required by pyside6-android-deploy (must be named main.py).
"""

import sys
import os
from pathlib import Path

# Add spark directory to path
# On Android, Python runs from /data/data/org.spark.spark/files/app/
# and the spark module is directly in the app directory
if hasattr(sys, 'getandroidapilevel'):
    # Running on Android - add current directory to path
    app_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, app_dir)

    # Debug: Print sys.path and directory contents to logcat
    print(f"SPARK DEBUG: sys.path = {sys.path}")
    print(f"SPARK DEBUG: app_dir = {app_dir}")
    print(f"SPARK DEBUG: Contents of app_dir:")
    try:
        for item in os.listdir(app_dir):
            item_path = os.path.join(app_dir, item)
            if os.path.isdir(item_path):
                print(f"  [DIR]  {item}")
                # List contents of spark directory if it exists
                if item == 'spark':
                    print(f"    Contents of spark/:")
                    for subitem in os.listdir(item_path):
                        print(f"      {subitem}")
            else:
                print(f"  [FILE] {item}")
    except Exception as e:
        print(f"SPARK DEBUG: Error listing directory: {e}")
else:
    # Running on desktop - use standard path setup
    spark_dir = Path(__file__).parent / "spark"
    sys.path.insert(0, str(spark_dir.parent))

# Import and run the application
from spark.database import Database
from spark.config import Config
from spark.qt_compat import QApplication
from spark.main_window import MainWindow


def main():
    """Main entry point."""
    # Initialize configuration and database
    config = Config()
    database = Database(config.get_database_path())

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("SPARK Personal")
    app.setOrganizationName("LCDcode")

    # Create and show main window
    window = MainWindow(database, config)
    window.show()

    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
