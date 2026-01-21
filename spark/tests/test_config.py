"""Unit tests for Config class."""

import os
import tempfile
import shutil
import pytest
from pathlib import Path
import yaml

from spark.config import Config, DEFAULT_CONFIG


class TestConfig:
    """Test cases for Config class."""

    @pytest.fixture
    def temp_home(self, tmp_path):
        """Create a temporary home directory for testing."""
        return tmp_path / "test_home"

    @pytest.fixture
    def config(self, temp_home, monkeypatch):
        """Create a Config instance with temporary home directory."""
        monkeypatch.setenv("HOME", str(temp_home))
        return Config()

    def test_config_initialization(self, config):
        """Test that config initializes with default values."""
        assert config.config is not None
        assert isinstance(config.config, dict)

        # Check that all default config keys are present
        for key in DEFAULT_CONFIG.keys():
            assert key in config.config

    def test_config_directory_creation(self, config):
        """Test that config directory is created."""
        assert config.config_dir.exists()
        assert config.config_dir.is_dir()

    def test_config_file_creation(self, config):
        """Test that config file is created."""
        assert config.config_file.exists()
        assert config.config_file.is_file()

    def test_get_method(self, config):
        """Test getting configuration values."""
        assert config.get("theme") == DEFAULT_CONFIG["theme"]
        assert config.get("font_size") == DEFAULT_CONFIG["font_size"]
        assert config.get("nonexistent_key") is None
        assert config.get("nonexistent_key", "default") == "default"

    def test_set_method(self, config):
        """Test setting configuration values."""
        config.set("theme", "Dark")
        assert config.get("theme") == "Dark"

        config.set("font_size", 14)
        assert config.get("font_size") == 14

        # Verify it was saved to file
        with open(config.config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        assert saved_config["theme"] == "Dark"
        assert saved_config["font_size"] == 14

    def test_get_database_path_default(self, config):
        """Test getting default database path."""
        db_path = config.get_database_path()
        assert db_path == config.config_dir / "spark.db"

    def test_get_database_path_custom(self, config, temp_home):
        """Test getting custom database path."""
        custom_path = temp_home / "custom" / "my_db.db"
        config.set("database_location", str(custom_path))
        db_path = config.get_database_path()
        assert db_path == custom_path

    def test_get_images_dir(self, config):
        """Test getting images directory."""
        images_dir = config.get_images_dir()
        assert images_dir.exists()
        assert images_dir.is_dir()
        assert images_dir == config.config_dir / "images"

    def test_get_backup_dir_default(self, config):
        """Test getting default backup directory."""
        backup_dir = config.get_backup_dir()
        assert backup_dir.exists()
        assert backup_dir.is_dir()
        assert backup_dir == config.config_dir / "backups"

    def test_get_backup_dir_custom(self, config, temp_home):
        """Test getting custom backup directory."""
        custom_backup = temp_home / "my_backups"
        config.set("backup_location", str(custom_backup))
        backup_dir = config.get_backup_dir()
        assert backup_dir == custom_backup

    def test_config_persistence(self, config, temp_home, monkeypatch):
        """Test that config persists across instances."""
        config.set("theme", "Gruvbox")
        config.set("font_size", 16)

        # Create a new config instance
        monkeypatch.setenv("HOME", str(temp_home))
        new_config = Config()

        assert new_config.get("theme") == "Gruvbox"
        assert new_config.get("font_size") == 16

    def test_config_load_existing(self, config, temp_home, monkeypatch):
        """Test loading existing config file."""
        # Manually create a config file
        config_data = {
            "theme": "Solarized Dark",
            "font_size": 18,
            "custom_key": "custom_value"
        }
        with open(config.config_file, 'w') as f:
            yaml.dump(config_data, f)

        # Load it
        monkeypatch.setenv("HOME", str(temp_home))
        new_config = Config()

        assert new_config.get("theme") == "Solarized Dark"
        assert new_config.get("font_size") == 18
        assert new_config.get("custom_key") == "custom_value"

        # Check that defaults are still merged
        assert new_config.get("window_width") == DEFAULT_CONFIG["window_width"]

    def test_config_invalid_yaml(self, config, temp_home, monkeypatch):
        """Test handling of invalid YAML in config file."""
        # Write invalid YAML
        with open(config.config_file, 'w') as f:
            f.write("invalid: yaml: content: {{")

        # Should fall back to defaults
        monkeypatch.setenv("HOME", str(temp_home))
        new_config = Config()

        assert new_config.get("theme") == DEFAULT_CONFIG["theme"]

    def test_default_config_values(self):
        """Test that DEFAULT_CONFIG has expected structure."""
        assert "theme" in DEFAULT_CONFIG
        assert "font_family" in DEFAULT_CONFIG
        assert "font_size" in DEFAULT_CONFIG
        assert "window_width" in DEFAULT_CONFIG
        assert "window_height" in DEFAULT_CONFIG
        assert "backup_enabled" in DEFAULT_CONFIG
        assert "autosave_enabled" in DEFAULT_CONFIG
