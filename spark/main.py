"""Main entry point for SPARK Personal application."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from spark.config import Config
from spark.database import Database
from spark.main_window import MainWindow
from spark.demo_data import create_demo_data


def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("SPARK (Snippet, Personal Archive, and Reference Keeper) Personal")
    app.setOrganizationName("LCD-Code")

    # Set application icon
    icon_path = Path(__file__).parent.parent / "spark.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    

    # Load configuration
    config = Config()

    # Initialize database
    db_path = config.get_database_path()
    database = Database(db_path)

    # Create demo data for first-time users
    create_demo_data(database, config)

    # Create and show main window
    window = MainWindow(database, config)
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
