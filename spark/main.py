"""Main entry point for SPARK Personal application."""

import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Add parent directory to path if running directly
# This allows: python3 /path/to/spark/main.py
if __name__ == "__main__":
    spark_module_dir = Path(__file__).parent.parent
    if str(spark_module_dir) not in sys.path:
        sys.path.insert(0, str(spark_module_dir))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from spark.config import Config
from spark.database import Database
from spark.main_window import MainWindow
from spark.demo_data import create_demo_data


def setup_logging():
    """Set up comprehensive logging for SPARK."""
    # Create logs directory
    log_dir = Path.home() / ".spark_personal"
    log_dir.mkdir(exist_ok=True)

    # Create log file with timestamp
    log_file = log_dir / "spark_debug.log"

    # Configure logging with detailed format
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info(f"SPARK Personal started at {datetime.now()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 80)

    return logger


def excepthook(exc_type, exc_value, exc_tb):
    """Global exception handler to catch unhandled exceptions."""
    logger = logging.getLogger(__name__)
    logger.critical("Unhandled exception occurred!", exc_info=(exc_type, exc_value, exc_tb))

    # Format the traceback
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
    tb_text = ''.join(tb_lines)

    # Show error dialog to user
    try:
        app = QApplication.instance()
        if app:
            error_msg = f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}\n\nCheck ~/.spark_personal/spark_debug.log for details."
            QMessageBox.critical(None, "SPARK Error", error_msg)
    except:
        pass

    # Call the default handler
    sys.__excepthook__(exc_type, exc_value, exc_tb)


def main():
    """Main application entry point."""
    # Set up logging first
    logger = setup_logging()

    # Install global exception handler
    sys.excepthook = excepthook

    try:
        logger.info("Creating QApplication")
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("SPARK (Snippet, Personal Archive, and Reference Keeper) Personal")
        app.setOrganizationName("LCD-Code")

        logger.info("Setting application icon")
        # Set application icon
        icon_path = Path(__file__).parent.parent / "spark.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        else:
            logger.warning(f"Icon file not found: {icon_path}")

        logger.info("Loading configuration")
        # Load configuration
        config = Config()

        logger.info("Initializing database")
        # Initialize database
        db_path = config.get_database_path()
        logger.info(f"Database path: {db_path}")
        database = Database(db_path)

        logger.info("Creating demo data (if needed)")
        # Create demo data for first-time users
        create_demo_data(database, config)

        logger.info("Creating main window")
        # Create and show main window
        window = MainWindow(database, config)

        logger.info("Showing main window")
        window.show()

        logger.info("Starting application event loop")
        # Run application
        exit_code = app.exec()
        logger.info(f"Application exited with code: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Fatal error in main(): {e}", exc_info=True)
        try:
            QMessageBox.critical(None, "SPARK Fatal Error",
                               f"Failed to start SPARK:\n\n{e}\n\nCheck ~/.spark_personal/spark_debug.log for details.")
        except:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
