"""Unit tests for themes module."""

import pytest
from spark.themes import THEMES, get_stylesheet


class TestThemes:
    """Test cases for theme definitions."""

    def test_all_themes_exist(self):
        """Test that all expected themes are defined."""
        expected_themes = ["Light", "Dark", "Solarized Light", "Solarized Dark", "Gruvbox"]
        for theme_name in expected_themes:
            assert theme_name in THEMES

    def test_theme_structure(self):
        """Test that each theme has all required color keys."""
        required_keys = [
            "background", "foreground", "accent", "border", "hover",
            "selected", "editor_bg", "editor_fg", "tree_bg"
        ]

        for theme_name, theme_data in THEMES.items():
            for key in required_keys:
                assert key in theme_data, f"Theme {theme_name} missing key {key}"

    def test_theme_colors_are_hex(self):
        """Test that all theme colors are hex codes."""
        for theme_name, theme_data in THEMES.items():
            for color_key, color_value in theme_data.items():
                assert isinstance(color_value, str)
                assert color_value.startswith("#"), \
                    f"Color {color_key} in theme {theme_name} should start with #"
                assert len(color_value) == 7, \
                    f"Color {color_key} in theme {theme_name} should be 7 chars"

    def test_light_theme_colors(self):
        """Test Light theme has light colors."""
        light = THEMES["Light"]
        assert light["background"] == "#ffffff"
        assert light["foreground"] == "#000000"

    def test_dark_theme_colors(self):
        """Test Dark theme has dark colors."""
        dark = THEMES["Dark"]
        assert dark["background"] == "#1e1e1e"
        assert dark["foreground"] == "#d4d4d4"

    def test_get_stylesheet_with_valid_theme(self):
        """Test stylesheet generation with valid theme."""
        stylesheet = get_stylesheet("Light", "Arial", 12)

        assert isinstance(stylesheet, str)
        assert len(stylesheet) > 0
        assert "QMainWindow" in stylesheet
        assert "QWidget" in stylesheet
        assert "background-color: #ffffff" in stylesheet
        assert "font-family: Arial" in stylesheet
        assert "font-size: 12pt" in stylesheet

    def test_get_stylesheet_with_dark_theme(self):
        """Test stylesheet generation with Dark theme."""
        stylesheet = get_stylesheet("Dark", "Consolas", 10)

        assert isinstance(stylesheet, str)
        assert "background-color: #1e1e1e" in stylesheet
        assert "font-family: Consolas" in stylesheet
        assert "font-size: 10pt" in stylesheet

    def test_get_stylesheet_with_invalid_theme(self):
        """Test stylesheet generation falls back to Light theme for invalid theme."""
        stylesheet = get_stylesheet("NonexistentTheme", "Arial", 12)

        # Should fall back to Light theme
        assert isinstance(stylesheet, str)
        assert "background-color: #ffffff" in stylesheet  # Light theme background

    def test_get_stylesheet_with_all_themes(self):
        """Test stylesheet generation for all themes."""
        for theme_name in THEMES.keys():
            stylesheet = get_stylesheet(theme_name, "Arial", 12)
            assert isinstance(stylesheet, str)
            assert len(stylesheet) > 0
            assert "QMainWindow" in stylesheet

    def test_stylesheet_contains_all_widget_types(self):
        """Test that stylesheet includes all expected widget types."""
        stylesheet = get_stylesheet("Light", "Arial", 12)

        widget_types = [
            "QMainWindow", "QWidget", "QTreeWidget", "QListWidget",
            "QTextEdit", "QPlainTextEdit", "QLineEdit", "QPushButton",
            "QTabWidget", "QTabBar", "QMenuBar", "QMenu", "QTableWidget",
            "QHeaderView", "QComboBox", "QStatusBar", "QScrollBar"
        ]

        for widget_type in widget_types:
            assert widget_type in stylesheet

    def test_stylesheet_hover_states(self):
        """Test that stylesheet includes hover states."""
        stylesheet = get_stylesheet("Light", "Arial", 12)

        assert "hover" in stylesheet
        assert ":hover" in stylesheet

    def test_stylesheet_selected_states(self):
        """Test that stylesheet includes selected states."""
        stylesheet = get_stylesheet("Light", "Arial", 12)

        assert "selected" in stylesheet
        assert ":selected" in stylesheet

    def test_stylesheet_with_different_font_sizes(self):
        """Test stylesheet with various font sizes."""
        for size in [8, 10, 12, 14, 16]:
            stylesheet = get_stylesheet("Light", "Arial", size)
            assert f"font-size: {size}pt" in stylesheet

    def test_stylesheet_with_different_fonts(self):
        """Test stylesheet with various font families."""
        fonts = ["Arial", "Consolas", "Courier New", "Times New Roman"]
        for font in fonts:
            stylesheet = get_stylesheet("Light", font, 12)
            assert f"font-family: {font}" in stylesheet

    def test_solarized_themes(self):
        """Test Solarized theme variants."""
        solarized_light = THEMES["Solarized Light"]
        solarized_dark = THEMES["Solarized Dark"]

        # Both should have the same accent color
        assert solarized_light["accent"] == solarized_dark["accent"] == "#268bd2"

        # But different backgrounds
        assert solarized_light["background"] == "#fdf6e3"
        assert solarized_dark["background"] == "#002b36"

    def test_gruvbox_theme(self):
        """Test Gruvbox theme colors."""
        gruvbox = THEMES["Gruvbox"]

        assert gruvbox["background"] == "#282828"
        assert gruvbox["foreground"] == "#ebdbb2"
        assert gruvbox["accent"] == "#fe8019"

    def test_theme_consistency(self):
        """Test that themes have consistent structure."""
        first_theme_keys = set(THEMES["Light"].keys())

        for theme_name, theme_data in THEMES.items():
            assert set(theme_data.keys()) == first_theme_keys, \
                f"Theme {theme_name} has inconsistent keys"

    def test_stylesheet_border_properties(self):
        """Test that stylesheet includes border properties."""
        stylesheet = get_stylesheet("Light", "Arial", 12)

        assert "border:" in stylesheet
        assert "border-radius:" in stylesheet

    def test_stylesheet_padding_properties(self):
        """Test that stylesheet includes padding properties."""
        stylesheet = get_stylesheet("Light", "Arial", 12)

        assert "padding:" in stylesheet

    def test_stylesheet_scrollbar_styling(self):
        """Test that stylesheet includes scrollbar styling."""
        stylesheet = get_stylesheet("Light", "Arial", 12)

        assert "QScrollBar:vertical" in stylesheet
        assert "QScrollBar:horizontal" in stylesheet
        assert "QScrollBar::handle" in stylesheet
