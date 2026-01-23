"""SPARK Mobile - Touch-first knowledgebase for Android/iOS."""

import os
import sys
import logging
from pathlib import Path

# Configure logging FIRST - before any other imports
logging.basicConfig(
    level=logging.DEBUG,
    format='SPARK: %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

print("="*60)
print("SPARK MOBILE STARTUP - INITIAL LOGGING TEST")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Working directory: {os.getcwd()}")
print("="*60)
sys.stdout.flush()

try:
    from kivy.app import App
    print("✓ Kivy imported successfully")
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
    from kivy.core.window import Window
    from kivy.config import Config
    print("✓ Kivy UI components imported")

    # Import database and screens
    from database import Database
    print("✓ Database module imported")
    from notes_screen import NotesScreen
    print("✓ NotesScreen imported")
    from snippets_screen import SnippetsScreen
    print("✓ SnippetsScreen imported")
    from spreadsheets_screen import SpreadsheetsScreen
    print("✓ SpreadsheetsScreen imported")

    # Configure Kivy
    Config.set('kivy', 'exit_on_escape', '0')
    Config.set('graphics', 'resizable', False)
    print("✓ Kivy configured")

except Exception as e:
    import traceback
    print("="*60)
    print("CRITICAL ERROR DURING IMPORTS:")
    print(str(e))
    print("-"*60)
    traceback.print_exc()
    print("="*60)
    sys.stdout.flush()
    raise


class SparkMobile(App):
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None

    def build(self):
        """Build the UI."""
        # Set app title
        self.title = "SPARK Mobile"

        # Set icon
        self.icon = 'icon.png'

        # Request storage permissions on Android
        if sys.platform == 'android':
            self.request_android_permissions()

        # Initialize database
        db_path = self.get_db_path()
        print(f"Database path: {db_path}")
        self.db = Database(db_path)

        # Create main layout with dark theme
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        # Create tabbed interface
        tabs = TabbedPanel(
            do_default_tab=False,
            tab_pos='top_mid',
            tab_width=Window.width / 3
        )

        # Notes tab
        notes_tab = TabbedPanelItem(text='Notes')
        notes_tab.add_widget(NotesScreen(self.db, db_path=str(db_path)))
        tabs.add_widget(notes_tab)

        # Snippets tab
        snippets_tab = TabbedPanelItem(text='Snippets')
        snippets_tab.add_widget(SnippetsScreen(self.db))
        tabs.add_widget(snippets_tab)

        # Spreadsheets tab
        sheets_tab = TabbedPanelItem(text='Sheets')
        sheets_tab.add_widget(SpreadsheetsScreen(self.db))
        tabs.add_widget(sheets_tab)

        return tabs

    def get_db_path(self) -> Path:
        """Get platform-appropriate database path."""
        from kivy.utils import platform as kivy_platform

        if kivy_platform == 'android':
            print("SPARK: ===== DATABASE PATH DETECTION =====")

            # Try Downloads directory first
            try:
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')

                # Get Downloads directory
                downloads_dir = Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_DOWNLOADS
                )
                downloads_path = Path(str(downloads_dir.getAbsolutePath()))

                print(f"SPARK: Downloads path: {downloads_path}")

                # Try to create SPARK subfolder
                try:
                    spark_dir = downloads_path / 'SPARK'
                    spark_dir.mkdir(exist_ok=True, parents=True)

                    # Test if we can actually write here
                    test_file = spark_dir / '.test'
                    test_file.touch()
                    test_file.unlink()

                    db_path = spark_dir / 'spark.db'
                    print(f"SPARK: ✓ SUCCESS! Database at: {db_path}")
                    print(f"SPARK: This location is accessible by Syncthing!")
                    print(f"SPARK: Configure Syncthing to sync: Download/SPARK/")
                    print(f"SPARK: ==========================================")
                    return db_path

                except (PermissionError, OSError) as mkdir_err:
                    print(f"SPARK: Cannot create folder in Downloads: {mkdir_err}")
                    print(f"SPARK: Trying Downloads root...")

                    # Try Downloads root directly
                    try:
                        test_file = downloads_path / '.test'
                        test_file.touch()
                        test_file.unlink()

                        db_path = downloads_path / 'spark.db'
                        print(f"SPARK: ✓ Using Downloads root: {db_path}")
                        print(f"SPARK: Configure Syncthing to sync entire Download folder")
                        print(f"SPARK: ==========================================")
                        return db_path
                    except (PermissionError, OSError) as write_err:
                        print(f"SPARK: Cannot write to Downloads: {write_err}")

            except Exception as e:
                import traceback
                print(f"SPARK: Error accessing Downloads: {e}")
                traceback.print_exc()

            # Fallback to internal storage
            print("SPARK: ==========================================")
            print(f"SPARK: Using internal storage (not accessible to Syncthing)")
            print(f"SPARK: Use the 📤 export button to copy DB to Downloads")
            print(f"SPARK: ==========================================")
            from android.storage import app_storage_path
            return Path(app_storage_path()) / 'spark.db'
        else:
            # On desktop, use current directory for testing
            data_dir = Path.cwd() / 'data'
            data_dir.mkdir(exist_ok=True)
            return data_dir / 'spark.db'

    def on_pause(self):
        """Handle app pause (required for Android)."""
        # Save any pending changes
        if self.db:
            self.db.close()
        return True

    def on_resume(self):
        """Handle app resume (required for Android)."""
        # Reconnect to database
        if self.db:
            self.db.connect()

    def on_stop(self):
        """Handle app stop."""
        if self.db:
            self.db.close()

    def request_android_permissions(self):
        """Request storage permissions on Android."""
        from kivy.utils import platform as kivy_platform

        if kivy_platform == 'android':
            try:
                from android.permissions import request_permissions, Permission, check_permission

                # Request all storage permissions
                permissions = [
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                ]

                print("SPARK: Requesting storage permissions...")
                request_permissions(permissions)

                # Check if permissions were granted
                write_granted = check_permission(Permission.WRITE_EXTERNAL_STORAGE)
                read_granted = check_permission(Permission.READ_EXTERNAL_STORAGE)

                print(f"SPARK: WRITE_EXTERNAL_STORAGE: {'✓ Granted' if write_granted else '✗ Denied'}")
                print(f"SPARK: READ_EXTERNAL_STORAGE: {'✓ Granted' if read_granted else '✗ Denied'}")

                if not write_granted or not read_granted:
                    print("SPARK: ⚠ WARNING: Storage permissions not granted!")
                    print("SPARK: Please enable storage permissions in Android Settings")

            except Exception as e:
                print(f"SPARK: Error requesting permissions: {e}")


if __name__ == '__main__':
    SparkMobile().run()
