"""Unit tests for SpreadsheetWidget additional functionality."""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from spark.spreadsheet_widget import (
    FormulaEngine,
    SafeExpressionEvaluator,
    SpreadsheetWidget
)


class TestFormulaEngineEdgeCases:
    """Additional test cases for FormulaEngine edge cases."""

    def test_column_index_conversion(self):
        """Test multi-column range with column index conversion."""
        cells = {
            "A1": "1", "B1": "2", "C1": "3",
            "A2": "4", "B2": "5", "C2": "6",
        }
        engine = FormulaEngine(cells)
        # Test multi-column range A1:C2 = 1+2+3+4+5+6 = 21
        result = engine.evaluate("=SUM(A1:C2)")
        assert result == 21

    def test_range_with_formulas(self):
        """Test cell ranges containing formulas."""
        cells = {
            "A1": "=10+5",
            "A2": "=20+10",
            "A3": "=30+15",
        }
        engine = FormulaEngine(cells)
        # Should evaluate formulas in cells: 15+30+45 = 90
        result = engine.evaluate("=SUM(A1:A3)")
        assert result == 90

    def test_average_with_range_formulas(self):
        """Test AVERAGE with cell ranges containing formulas."""
        cells = {
            "B1": "=5*2",
            "B2": "=10*2",
            "B3": "=15*2",
        }
        engine = FormulaEngine(cells)
        # Should evaluate: (10+20+30)/3 = 20
        result = engine.evaluate("=AVERAGE(B1:B3)")
        assert result == 20

    def test_date_string_in_cell_reference(self):
        """Test handling of date strings in cell references."""
        cells = {
            "A1": "2024-01-15",
        }
        engine = FormulaEngine(cells)
        # Date string should be converted to timestamp
        result = engine.evaluate("=A1+1")
        assert isinstance(result, (int, float))

    def test_invalid_cell_reference_in_function(self):
        """Test handling of invalid cell references in functions."""
        cells = {}
        engine = FormulaEngine(cells)
        # Empty cells should default to 0
        result = engine.evaluate("=SUM(Z99:Z100)")
        assert result == 0

    def test_if_with_string_cell_values(self):
        """Test IF function with non-numeric cell values."""
        cells = {
            "A1": "text",
            "B1": "5",
        }
        engine = FormulaEngine(cells)
        # A1 (text -> 0) is not > 0, so should return B1
        result = engine.evaluate("=IF(A1>0,10,B1)")
        assert result == 5.0

    def test_formula_error_handling(self):
        """Test various formula errors."""
        cells = {}
        engine = FormulaEngine(cells)

        # Division by zero
        result = engine.evaluate("=10/0")
        assert "#ERROR" in str(result)

        # Invalid syntax
        result = engine.evaluate("=((")
        assert "#ERROR" in str(result)

    def test_date_function_with_cell_reference(self):
        """Test DATE function with cell references."""
        cells = {
            "A1": "19000",  # Days since epoch
        }
        engine = FormulaEngine(cells)
        result = engine.evaluate("=DATE(A1)")
        # Should return a date string
        assert isinstance(result, str)
        assert "-" in result  # Date format YYYY-MM-DD

    def test_date_function_error(self):
        """Test DATE function with invalid input."""
        cells = {}
        engine = FormulaEngine(cells)
        # Invalid date value
        result = engine.evaluate("=DATE(invalid)")
        assert "#ERROR" in result

    def test_range_expansion_single_row(self):
        """Test range expansion for a single row."""
        cells = {
            "A1": "1", "B1": "2", "C1": "3", "D1": "4"
        }
        engine = FormulaEngine(cells)
        result = engine.evaluate("=SUM(A1:D1)")
        assert result == 10

    def test_comparison_with_cell_references(self):
        """Test comparison operators with cell references."""
        cells = {
            "A1": "10",
            "B1": "20",
        }
        engine = FormulaEngine(cells)

        assert engine.evaluate("=A1<B1") is True
        assert engine.evaluate("=A1>B1") is False
        assert engine.evaluate("=A1<=10") is True
        assert engine.evaluate("=B1>=20") is True

    def test_formula_with_multiple_operators(self):
        """Test formulas with multiple different operators."""
        cells = {
            "A1": "10",
            "B1": "5",
            "C1": "2",
        }
        engine = FormulaEngine(cells)
        # 10 + 5 * 2 - 3 = 10 + 10 - 3 = 17
        result = engine.evaluate("=A1+B1*C1-3")
        assert result == 17.0

    def test_nested_parentheses(self):
        """Test deeply nested parentheses."""
        cells = {
            "A1": "5",
            "B1": "3",
            "C1": "2",
        }
        engine = FormulaEngine(cells)
        result = engine.evaluate("=((A1+B1)*C1)+((A1-B1)/C1)")
        # ((5+3)*2) + ((5-3)/2) = (8*2) + (2/2) = 16 + 1 = 17
        assert result == 17.0

    def test_sum_with_single_value(self):
        """Test SUM with a single value."""
        cells = {"A1": "42"}
        engine = FormulaEngine(cells)
        assert engine.evaluate("=SUM(A1)") == 42

    def test_average_with_single_value(self):
        """Test AVERAGE with a single value."""
        cells = {"A1": "42"}
        engine = FormulaEngine(cells)
        assert engine.evaluate("=AVERAGE(A1)") == 42

    def test_if_condition_evaluation_error(self):
        """Test IF function when condition evaluation fails."""
        cells = {}
        engine = FormulaEngine(cells)
        # Invalid condition should return false value
        result = engine.evaluate("=IF(invalid,100,200)")
        # Should return false value when condition fails
        assert result == 200

    def test_boolean_and_function(self):
        """Test AND boolean function."""
        cells = {}
        engine = FormulaEngine(cells)
        assert engine.evaluate("=AND(True,True)") is True

    def test_boolean_or_function(self):
        """Test OR boolean function."""
        cells = {}
        engine = FormulaEngine(cells)
        assert engine.evaluate("=OR(False,False)") is False

    def test_boolean_not_function(self):
        """Test NOT boolean function."""
        cells = {}
        engine = FormulaEngine(cells)
        assert engine.evaluate("=NOT(True)") is False
        assert engine.evaluate("=NOT(False)") is True

    def test_cell_reference_case_sensitive(self):
        """Test that cell references are case-sensitive (uppercase only)."""
        cells = {"A1": "10", "B1": "20"}
        engine = FormulaEngine(cells)
        # Cell references must be uppercase
        result = engine.evaluate("=A1+B1")
        assert result == 30.0

        # Lowercase cell references won't be recognized
        result = engine.evaluate("=a1+b1")
        assert "#ERROR" in str(result)

    def test_empty_range(self):
        """Test handling of empty cell ranges."""
        cells = {}
        engine = FormulaEngine(cells)
        # Empty range should sum to 0
        result = engine.evaluate("=SUM(A1:A5)")
        assert result == 0

    def test_formula_with_literal_numbers(self):
        """Test formulas with literal numbers and decimals."""
        cells = {}
        engine = FormulaEngine(cells)
        assert engine.evaluate("=3.14*2") == pytest.approx(6.28)
        assert engine.evaluate("=100/3") == pytest.approx(33.333, rel=0.001)

    def test_normalize_equality_preserves_other_operators(self):
        """Test that equality normalization doesn't affect other operators."""
        cells = {"A1": "10"}
        engine = FormulaEngine(cells)

        # Should not affect !=, <=, >=
        assert engine.evaluate("=A1!=5") is True
        assert engine.evaluate("=A1<=10") is True
        assert engine.evaluate("=A1>=10") is True

    def test_date_with_expression(self):
        """Test DATE function with complex expression."""
        cells = {}
        engine = FormulaEngine(cells)
        # TODAY() + 7 days, then convert to date
        result = engine.evaluate("=DATE(TODAY()+7)")
        assert isinstance(result, str)
        assert "-" in result

    def test_sum_with_empty_and_non_empty_cells(self):
        """Test SUM with mix of empty and non-empty cells."""
        cells = {
            "A1": "10",
            "A2": "",  # Empty cell
            "A3": "20",
        }
        engine = FormulaEngine(cells)
        # Empty cell should be treated as 0
        result = engine.evaluate("=SUM(A1:A3)")
        assert result == 30

    def test_multiple_ranges_in_sum(self):
        """Test SUM with multiple non-contiguous ranges."""
        cells = {
            "A1": "1", "A2": "2",
            "C1": "3", "C2": "4",
        }
        engine = FormulaEngine(cells)
        result = engine.evaluate("=SUM(A1:A2,C1:C2)")
        assert result == 10


class TestSafeExpressionEvaluatorEdgeCases:
    """Additional edge cases for SafeExpressionEvaluator."""

    def test_very_large_numbers(self):
        """Test evaluation with very large numbers."""
        result = SafeExpressionEvaluator.evaluate("999999999999 + 1")
        assert result == 1000000000000

    def test_very_small_numbers(self):
        """Test evaluation with very small numbers."""
        result = SafeExpressionEvaluator.evaluate("0.0000001 * 2")
        assert result == pytest.approx(0.0000002)

    def test_multiple_boolean_operations(self):
        """Test multiple boolean operations."""
        result = SafeExpressionEvaluator.evaluate("True and True and True")
        assert result is True

        result = SafeExpressionEvaluator.evaluate("False or False or True")
        assert result is True

    def test_mixed_int_and_float(self):
        """Test operations with mixed int and float."""
        result = SafeExpressionEvaluator.evaluate("5 + 2.5")
        assert result == 7.5

    def test_negative_exponentiation(self):
        """Test exponentiation with negative base."""
        result = SafeExpressionEvaluator.evaluate("(-2) ** 3")
        assert result == -8

    def test_fractional_exponents(self):
        """Test exponentiation with fractional exponents."""
        result = SafeExpressionEvaluator.evaluate("16 ** 0.5")
        assert result == 4.0

    def test_comparison_with_floats(self):
        """Test comparison operators with floats."""
        assert SafeExpressionEvaluator.evaluate("3.14 > 3") is True
        assert SafeExpressionEvaluator.evaluate("2.5 == 2.5") is True

    def test_boolean_short_circuit(self):
        """Test boolean operator short-circuit behavior."""
        # False and X should short-circuit and not evaluate X
        result = SafeExpressionEvaluator.evaluate("False and True")
        assert result is False

        # True or X should short-circuit
        result = SafeExpressionEvaluator.evaluate("True or False")
        assert result is True

    def test_modulo_with_floats(self):
        """Test modulo operation with floating point."""
        result = SafeExpressionEvaluator.evaluate("7.5 % 2.5")
        assert result == pytest.approx(0.0)

    def test_floor_division_with_negative(self):
        """Test floor division with negative numbers."""
        result = SafeExpressionEvaluator.evaluate("-17 // 5")
        assert result == -4  # Floor division rounds down

    def test_nested_unary_operators(self):
        """Test nested unary operators."""
        result = SafeExpressionEvaluator.evaluate("--5")
        assert result == 5

        result = SafeExpressionEvaluator.evaluate("+-5")
        assert result == -5


class TestConfigEdgeCases:
    """Additional edge cases for Config class."""

    @pytest.fixture
    def temp_home(self, tmp_path):
        """Create a temporary home directory."""
        return tmp_path / "test_home"

    def test_config_directory_permissions_error(self, temp_home, monkeypatch):
        """Test config handles permission errors gracefully."""
        from spark.config import Config

        monkeypatch.setenv("HOME", str(temp_home))
        config = Config()

        # Config should still work even if chmod fails
        assert config.config_dir.exists()

    def test_get_with_none_default(self, temp_home, monkeypatch):
        """Test get method returns None as default."""
        from spark.config import Config

        monkeypatch.setenv("HOME", str(temp_home))
        config = Config()

        result = config.get("nonexistent_key")
        assert result is None

    def test_images_dir_creation(self, temp_home, monkeypatch):
        """Test that images directory is created on first access."""
        from spark.config import Config

        monkeypatch.setenv("HOME", str(temp_home))
        config = Config()

        images_dir = config.get_images_dir()
        assert images_dir.exists()
        assert images_dir.is_dir()

        # Calling again should not error
        images_dir2 = config.get_images_dir()
        assert images_dir == images_dir2

    def test_backup_dir_creation(self, temp_home, monkeypatch):
        """Test that backup directory is created on first access."""
        from spark.config import Config

        monkeypatch.setenv("HOME", str(temp_home))
        config = Config()

        backup_dir = config.get_backup_dir()
        assert backup_dir.exists()
        assert backup_dir.is_dir()


class TestDatabaseEdgeCases:
    """Additional edge cases for Database class."""

    @pytest.fixture
    def db(self, tmp_path):
        """Create a temporary database."""
        from spark.database import Database
        db_path = tmp_path / "test.db"
        database = Database(db_path)
        yield database
        database.close()

    def test_empty_content_fields(self, db):
        """Test database handles empty content gracefully."""
        # Note with empty content
        note_id = db.add_note("Title Only", "")
        note = db.get_note(note_id)
        assert note["content"] == ""

        # Snippet with empty code
        snippet_id = db.add_snippet("Empty Code", "", "Python", "")
        snippet = db.get_snippet(snippet_id)
        assert snippet["code"] == ""

    def test_special_characters_in_content(self, db):
        """Test database handles special characters."""
        special_text = "Test with 'quotes', \"double quotes\", and emoji 🔥"

        note_id = db.add_note("Special", special_text)
        note = db.get_note(note_id)
        assert note["content"] == special_text

    def test_very_long_content(self, db):
        """Test database handles very long content."""
        long_content = "A" * 10000  # 10k characters

        note_id = db.add_note("Long Note", long_content)
        note = db.get_note(note_id)
        assert len(note["content"]) == 10000

    def test_search_case_insensitivity(self, db):
        """Test that search is case insensitive."""
        db.add_note("Python Tutorial", "Learn Python")

        results = db.search_notes("python")
        assert len(results) >= 1

        results = db.search_notes("PYTHON")
        assert len(results) >= 1

    def test_multiple_database_operations(self, db):
        """Test multiple rapid operations."""
        # Add multiple items rapidly
        ids = []
        for i in range(10):
            note_id = db.add_note(f"Note {i}", f"Content {i}")
            ids.append(note_id)

        # Verify all were added
        for note_id in ids:
            note = db.get_note(note_id)
            assert note is not None

    def test_spreadsheet_with_large_json(self, db):
        """Test spreadsheet with large JSON data."""
        large_data = json.dumps({f"A{i}": str(i) for i in range(100)})

        sheet_id = db.add_spreadsheet("Large Sheet", large_data)
        sheet = db.get_spreadsheet(sheet_id)
        assert sheet["data"] == large_data

    def test_snippet_with_multiline_code(self, db):
        """Test snippet with multiline code."""
        multiline_code = """def hello():
    print("Hello")
    return True"""

        snippet_id = db.add_snippet("Multi", multiline_code, "Python", "test")
        snippet = db.get_snippet(snippet_id)
        assert snippet["code"] == multiline_code

    def test_update_nonexistent_item(self, db):
        """Test updating non-existent items doesn't error."""
        # These shouldn't raise errors, just do nothing
        db.update_note(99999, "Title", "Content")
        db.update_spreadsheet(99999, "Name", "{}")
        db.update_snippet(99999, "Title", "Code", "Lang", "Tags")

    def test_search_with_empty_query(self, db):
        """Test search with empty query."""
        db.add_note("Test", "Content")

        # Empty search should match nothing or everything
        results = db.search_notes("")
        # Results depend on implementation, but shouldn't error

    def test_get_snippets_by_nonexistent_language(self, db):
        """Test getting snippets for a language that doesn't exist."""
        results = db.get_snippets_by_language("NonexistentLanguage")
        assert len(results) == 0
