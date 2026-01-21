"""Unit tests for SafeExpressionEvaluator class."""

import pytest
from spark.spreadsheet_widget import SafeExpressionEvaluator


class TestSafeExpressionEvaluator:
    """Test cases for SafeExpressionEvaluator class."""

    def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        assert SafeExpressionEvaluator.evaluate("2 + 3") == 5
        assert SafeExpressionEvaluator.evaluate("10 - 4") == 6
        assert SafeExpressionEvaluator.evaluate("5 * 6") == 30
        assert SafeExpressionEvaluator.evaluate("20 / 4") == 5
        assert SafeExpressionEvaluator.evaluate("7 + 3 * 2") == 13  # Order of operations

    def test_floor_division(self):
        """Test floor division operator."""
        assert SafeExpressionEvaluator.evaluate("17 // 5") == 3
        assert SafeExpressionEvaluator.evaluate("20 // 6") == 3

    def test_modulo(self):
        """Test modulo operator."""
        assert SafeExpressionEvaluator.evaluate("17 % 5") == 2
        assert SafeExpressionEvaluator.evaluate("20 % 6") == 2

    def test_exponentiation(self):
        """Test exponentiation operator."""
        assert SafeExpressionEvaluator.evaluate("2 ** 8") == 256
        assert SafeExpressionEvaluator.evaluate("3 ** 3") == 27
        assert SafeExpressionEvaluator.evaluate("5 ** 2") == 25

    def test_unary_operators(self):
        """Test unary operators."""
        assert SafeExpressionEvaluator.evaluate("-5") == -5
        assert SafeExpressionEvaluator.evaluate("+10") == 10
        assert SafeExpressionEvaluator.evaluate("-(3 + 2)") == -5

    def test_parentheses(self):
        """Test parentheses for grouping."""
        assert SafeExpressionEvaluator.evaluate("(2 + 3) * 4") == 20
        assert SafeExpressionEvaluator.evaluate("2 + (3 * 4)") == 14
        assert SafeExpressionEvaluator.evaluate("((5 + 3) * 2) / 4") == 4

    def test_comparison_operators(self):
        """Test comparison operators."""
        assert SafeExpressionEvaluator.evaluate("5 == 5") is True
        assert SafeExpressionEvaluator.evaluate("5 == 6") is False
        assert SafeExpressionEvaluator.evaluate("5 != 6") is True
        assert SafeExpressionEvaluator.evaluate("5 != 5") is False
        assert SafeExpressionEvaluator.evaluate("5 < 6") is True
        assert SafeExpressionEvaluator.evaluate("5 < 5") is False
        assert SafeExpressionEvaluator.evaluate("5 <= 5") is True
        assert SafeExpressionEvaluator.evaluate("5 > 4") is True
        assert SafeExpressionEvaluator.evaluate("5 >= 5") is True

    def test_boolean_operators(self):
        """Test boolean operators."""
        assert SafeExpressionEvaluator.evaluate("True and True") is True
        assert SafeExpressionEvaluator.evaluate("True and False") is False
        assert SafeExpressionEvaluator.evaluate("False and False") is False
        assert SafeExpressionEvaluator.evaluate("True or False") is True
        assert SafeExpressionEvaluator.evaluate("False or False") is False
        assert SafeExpressionEvaluator.evaluate("True or True") is True

    def test_combined_boolean_comparison(self):
        """Test combining comparisons with boolean operators."""
        assert SafeExpressionEvaluator.evaluate("5 > 3 and 10 < 20") is True
        assert SafeExpressionEvaluator.evaluate("5 > 10 or 20 > 15") is True
        assert SafeExpressionEvaluator.evaluate("5 > 10 and 20 > 15") is False

    def test_complex_expressions(self):
        """Test complex nested expressions."""
        assert SafeExpressionEvaluator.evaluate("(2 + 3) * (4 - 1)") == 15
        assert SafeExpressionEvaluator.evaluate("2 ** 3 + 4 * 5") == 28
        assert SafeExpressionEvaluator.evaluate("(10 + 5) / 3") == 5

    def test_floating_point(self):
        """Test floating point operations."""
        assert SafeExpressionEvaluator.evaluate("2.5 + 3.5") == 6.0
        assert SafeExpressionEvaluator.evaluate("10.0 / 4.0") == 2.5
        assert SafeExpressionEvaluator.evaluate("3.14 * 2") == pytest.approx(6.28)

    def test_string_literals(self):
        """Test string literal support."""
        assert SafeExpressionEvaluator.evaluate('"hello"') == "hello"
        assert SafeExpressionEvaluator.evaluate("'world'") == "world"

    def test_invalid_expressions(self):
        """Test that invalid expressions raise errors."""
        with pytest.raises(ValueError):
            SafeExpressionEvaluator.evaluate("invalid expression")

        with pytest.raises(ValueError):
            SafeExpressionEvaluator.evaluate("import os")  # Not allowed

        with pytest.raises(ValueError):
            SafeExpressionEvaluator.evaluate("5 + ")  # Incomplete

    def test_chained_comparisons_not_supported(self):
        """Test that chained comparisons raise an error."""
        with pytest.raises(ValueError, match="Chained comparisons not supported"):
            SafeExpressionEvaluator.evaluate("5 < 10 < 15")

    def test_unsupported_operations(self):
        """Test that unsupported operations raise errors."""
        # List literals not supported
        with pytest.raises(ValueError):
            SafeExpressionEvaluator.evaluate("[1, 2, 3]")

        # Dictionary literals not supported
        with pytest.raises(ValueError):
            SafeExpressionEvaluator.evaluate("{'key': 'value'}")

        # Function calls not supported
        with pytest.raises(ValueError):
            SafeExpressionEvaluator.evaluate("func()")

    def test_division_by_zero(self):
        """Test division by zero raises error."""
        with pytest.raises(Exception):  # ZeroDivisionError wrapped in ValueError
            SafeExpressionEvaluator.evaluate("10 / 0")

    def test_boolean_constants(self):
        """Test True/False/None constants."""
        assert SafeExpressionEvaluator.evaluate("True") is True
        assert SafeExpressionEvaluator.evaluate("False") is False
        assert SafeExpressionEvaluator.evaluate("None") is None

    def test_operator_precedence(self):
        """Test operator precedence is correct."""
        assert SafeExpressionEvaluator.evaluate("2 + 3 * 4") == 14
        assert SafeExpressionEvaluator.evaluate("2 * 3 + 4") == 10
        assert SafeExpressionEvaluator.evaluate("2 ** 3 ** 2") == 512  # Right-associative
        assert SafeExpressionEvaluator.evaluate("10 - 5 - 2") == 3  # Left-associative

    def test_negative_numbers(self):
        """Test negative number handling."""
        assert SafeExpressionEvaluator.evaluate("-10 + 5") == -5
        assert SafeExpressionEvaluator.evaluate("5 * -2") == -10
        assert SafeExpressionEvaluator.evaluate("-3 ** 2") == -9  # Unary minus has lower precedence

    def test_zero_operations(self):
        """Test operations with zero."""
        assert SafeExpressionEvaluator.evaluate("0 + 5") == 5
        assert SafeExpressionEvaluator.evaluate("5 * 0") == 0
        assert SafeExpressionEvaluator.evaluate("0 ** 5") == 0
        assert SafeExpressionEvaluator.evaluate("5 - 0") == 5
