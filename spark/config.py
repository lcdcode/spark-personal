"""Configuration management for SPARK Personal."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG = {
    "theme": "Light",
    "font_family": "Consolas",
    "font_size": 10,
    "window_width": 1200,
    "window_height": 800,
    "database_location": "",  # Empty means use default
    "backup_location": "",
    "backup_enabled": True,
    "backup_interval_hours": 24,
    "autosave_enabled": True,
    "autosave_interval_seconds": 300,
    "editor_tab_width": 4,
}


class Config:
    """Manages application configuration."""

    def __init__(self):
        self.config_dir = Path.home() / ".spark_personal"
        self.config_file = self.config_dir / "config.yaml"
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from file or create default."""
        if not self.config_dir.exists():
            # Create config directory with restricted permissions (user-only)
            self.config_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        else:
            # Ensure existing directory has correct permissions
            try:
                os.chmod(self.config_dir, 0o700)
            except OSError:
                pass  # May fail on some systems, not critical

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = {}

        # Merge with defaults
        for key, value in DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config[key] = value

        # Save to ensure config file exists with all defaults
        self.save()

    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            # Set restricted permissions on config file (user-only read/write)
            try:
                os.chmod(self.config_file, 0o600)
            except OSError:
                pass  # May fail on some systems, not critical
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        self.save()

    def get_database_path(self) -> Path:
        """Get the database file path."""
        db_location = self.config.get("database_location", "")
        if db_location:
            return Path(db_location)
        return self.config_dir / "spark.db"

    def get_images_dir(self) -> Path:
        """Get the images directory path."""
        db_path = self.get_database_path()
        images_dir = db_path.parent / "images"
        images_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Ensure correct permissions on existing directory
        try:
            os.chmod(images_dir, 0o700)
        except OSError:
            pass
        return images_dir

    def get_backup_dir(self) -> Path:
        """Get the backup directory path."""
        backup_location = self.config.get("backup_location", "")
        if backup_location:
            return Path(backup_location)
        backup_dir = self.config_dir / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Ensure correct permissions on existing directory
        try:
            os.chmod(backup_dir, 0o700)
        except OSError:
            pass
        return backup_dir
