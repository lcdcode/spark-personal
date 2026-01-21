"""Backup management system for SPARK Personal."""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QLabel, QSpinBox, QCheckBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import QTimer, pyqtSignal


class BackupManager:
    """Manages database backups."""

    def __init__(self, config, db_path: Path):
        self.config = config
        self.db_path = db_path
        self.backup_dir = config.get_backup_dir()

    def create_backup(self) -> Path:
        """Create a backup of the database."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"spark_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name

        try:
            shutil.copy2(self.db_path, backup_path)
            # Set restrictive permissions on backup file (user-only read/write)
            try:
                os.chmod(backup_path, 0o600)
            except OSError:
                pass  # May fail on some systems, not critical
            return backup_path
        except Exception as e:
            raise Exception(f"Backup failed: {str(e)}")

    def list_backups(self):
        """List all available backups."""
        if not self.backup_dir.exists():
            return []

        backups = sorted(
            [f for f in self.backup_dir.glob("spark_backup_*.db")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        return backups

    def restore_backup(self, backup_path: Path):
        """Restore a backup."""
        try:
            # Create a backup of current database before restoring
            current_backup = self.backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(self.db_path, current_backup)
            # Set restrictive permissions on pre-restore backup
            try:
                os.chmod(current_backup, 0o600)
            except OSError:
                pass

            # Restore the backup
            shutil.copy2(backup_path, self.db_path)
            # Set restrictive permissions on restored database
            try:
                os.chmod(self.db_path, 0o600)
            except OSError:
                pass
        except Exception as e:
            raise Exception(f"Restore failed: {str(e)}")

    def delete_backup(self, backup_path: Path):
        """Delete a backup file."""
        try:
            backup_path.unlink()
        except Exception as e:
            raise Exception(f"Delete failed: {str(e)}")

    def cleanup_old_backups(self, keep_count: int = 10):
        """
        Keep only the most recent N backups PLUS time-based snapshots.

        Retention policy:
        - Keep the most recent N backups (default 10)
        - Keep one backup from the last 7 days (if not in recent N)
        - Keep one backup from the last 30 days (if not already kept)
        - Keep one backup from the last 90 days (if not already kept)
        """
        backups = self.list_backups()
        if len(backups) <= keep_count:
            return  # Nothing to clean up

        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)

        # Always keep the most recent N backups
        keep_backups = set(backups[:keep_count])

        # Find the oldest backup from each time period
        backup_7d = None
        backup_30d = None
        backup_90d = None

        for backup in reversed(backups[keep_count:]):
            backup_time = datetime.fromtimestamp(backup.stat().st_mtime)

            # Find oldest backup within last 7 days
            if not backup_7d and backup_time >= seven_days_ago:
                backup_7d = backup

            # Find oldest backup within last 30 days (but older than 7 days)
            if not backup_30d and backup_time >= thirty_days_ago:
                backup_30d = backup

            # Find oldest backup within last 90 days (but older than 30 days)
            if not backup_90d and backup_time >= ninety_days_ago:
                backup_90d = backup

        # Add time-based snapshots to keep set
        if backup_7d:
            keep_backups.add(backup_7d)
        if backup_30d and backup_30d != backup_7d:
            keep_backups.add(backup_30d)
        if backup_90d and backup_90d not in (backup_7d, backup_30d):
            keep_backups.add(backup_90d)

        # Delete backups not in the keep set
        for backup in backups:
            if backup not in keep_backups:
                try:
                    backup.unlink()
                except Exception as e:
                    print(f"Failed to delete backup {backup.name}: {e}")


class BackupDialog(QDialog):
    """Dialog for managing backups."""

    backup_created = pyqtSignal()

    def __init__(self, backup_manager: BackupManager, config, parent=None):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.config = config
        self.setWindowTitle("Backup Manager")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.init_ui()
        self.load_backups()

    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)

        # Backup location
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Backup Location:"))
        self.location_label = QLabel(str(self.backup_manager.backup_dir))
        location_layout.addWidget(self.location_label)
        self.btn_change_location = QPushButton("Change")
        self.btn_change_location.clicked.connect(self.change_backup_location)
        location_layout.addWidget(self.btn_change_location)
        layout.addLayout(location_layout)

        # Backup list
        layout.addWidget(QLabel("Available Backups:"))
        self.backup_list = QListWidget()
        layout.addWidget(self.backup_list)

        # Backup actions
        action_layout = QHBoxLayout()
        self.btn_create = QPushButton("Create Backup")
        self.btn_create.clicked.connect(self.create_backup)
        self.btn_restore = QPushButton("Restore Selected")
        self.btn_restore.clicked.connect(self.restore_backup)
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.clicked.connect(self.delete_backup)
        action_layout.addWidget(self.btn_create)
        action_layout.addWidget(self.btn_restore)
        action_layout.addWidget(self.btn_delete)
        layout.addLayout(action_layout)

        # Auto-backup settings
        layout.addWidget(QLabel("Automatic Backup Settings:"))
        auto_layout = QHBoxLayout()

        self.auto_backup_enabled = QCheckBox("Enable automatic backups")
        self.auto_backup_enabled.setChecked(self.config.get('backup_enabled', True))
        self.auto_backup_enabled.stateChanged.connect(self.save_settings)
        auto_layout.addWidget(self.auto_backup_enabled)

        auto_layout.addWidget(QLabel("Interval (hours):"))
        self.backup_interval = QSpinBox()
        self.backup_interval.setMinimum(1)
        self.backup_interval.setMaximum(168)  # 1 week
        self.backup_interval.setValue(self.config.get('backup_interval_hours', 24))
        self.backup_interval.valueChanged.connect(self.save_settings)
        auto_layout.addWidget(self.backup_interval)

        layout.addLayout(auto_layout)

        # Backup retention settings
        retention_layout = QHBoxLayout()
        retention_layout.addWidget(QLabel("Keep recent backups:"))
        self.backup_retention = QSpinBox()
        self.backup_retention.setMinimum(1)
        self.backup_retention.setMaximum(100)
        self.backup_retention.setValue(self.config.get('backup_retention_count', 10))
        self.backup_retention.valueChanged.connect(self.save_settings)
        retention_layout.addWidget(self.backup_retention)
        retention_layout.addWidget(QLabel("(+ snapshots at 7, 30, 90 days)"))
        retention_layout.addStretch()
        layout.addLayout(retention_layout)

        # Close button
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.accept)
        layout.addWidget(self.btn_close)

    def load_backups(self):
        """Load backups into the list."""
        self.backup_list.clear()
        backups = self.backup_manager.list_backups()

        for backup in backups:
            timestamp = backup.stat().st_mtime
            dt = datetime.fromtimestamp(timestamp)
            size = backup.stat().st_size / 1024  # KB
            item_text = f"{backup.name} - {dt.strftime('%Y-%m-%d %H:%M:%S')} ({size:.1f} KB)"
            self.backup_list.addItem(item_text)
            self.backup_list.item(self.backup_list.count() - 1).setData(
                0x0100, str(backup)
            )

    def create_backup(self):
        """Create a new backup."""
        try:
            backup_path = self.backup_manager.create_backup()
            QMessageBox.information(
                self, "Success",
                f"Backup created successfully:\n{backup_path.name}"
            )
            self.load_backups()
            self.backup_created.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def restore_backup(self):
        """Restore the selected backup."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a backup to restore.")
            return

        reply = QMessageBox.question(
            self, "Restore Backup",
            "Are you sure you want to restore this backup?\n"
            "Your current database will be backed up before restoring.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                backup_path = Path(current_item.data(0x0100))
                self.backup_manager.restore_backup(backup_path)
                QMessageBox.information(
                    self, "Success",
                    "Backup restored successfully!\nPlease restart the application."
                )
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def delete_backup(self):
        """Delete the selected backup."""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a backup to delete.")
            return

        reply = QMessageBox.question(
            self, "Delete Backup",
            "Are you sure you want to delete this backup?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                backup_path = Path(current_item.data(0x0100))
                self.backup_manager.delete_backup(backup_path)
                QMessageBox.information(self, "Success", "Backup deleted successfully!")
                self.load_backups()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def change_backup_location(self):
        """Change the backup location."""
        new_location = QFileDialog.getExistingDirectory(
            self, "Select Backup Location",
            str(self.backup_manager.backup_dir)
        )

        if new_location:
            self.config.set('backup_location', new_location)
            self.backup_manager.backup_dir = Path(new_location)
            self.location_label.setText(new_location)
            self.load_backups()

    def save_settings(self):
        """Save backup settings to config."""
        self.config.set('backup_enabled', self.auto_backup_enabled.isChecked())
        self.config.set('backup_interval_hours', self.backup_interval.value())
        self.config.set('backup_retention_count', self.backup_retention.value())


class AutoBackupTimer:
    """Timer for automatic backups."""

    def __init__(self, backup_manager: BackupManager, config):
        self.backup_manager = backup_manager
        self.config = config
        self.timer = QTimer()
        self.timer.timeout.connect(self.create_backup)

    def start(self):
        """Start the auto-backup timer."""
        if self.config.get('backup_enabled', True):
            interval_hours = self.config.get('backup_interval_hours', 24)
            interval_ms = interval_hours * 60 * 60 * 1000
            self.timer.start(interval_ms)

    def stop(self):
        """Stop the auto-backup timer."""
        self.timer.stop()

    def create_backup(self):
        """Create an automatic backup."""
        try:
            self.backup_manager.create_backup()
            # Cleanup old backups using configured retention count
            retention_count = self.config.get('backup_retention_count', 10)
            self.backup_manager.cleanup_old_backups(keep_count=retention_count)
        except Exception as e:
            print(f"Auto-backup failed: {e}")
