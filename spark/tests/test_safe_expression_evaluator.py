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

    def test_string_concatenation(self):
        """Test string concatenation with + operator."""
        assert SafeExpressionEvaluator.evaluate('"hello" + " " + "world"') == "hello world"
        assert SafeExpressionEvaluator.evaluate('"foo" + "bar"') == "foobar"
        assert SafeExpressionEvaluator.evaluate('"test" + " " + "123"') == "test 123"
        # Mixed quotes
        assert SafeExpressionEvaluator.evaluate("'hello' + ' ' + 'world'") == "hello world"

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

    def test_abs_function(self):
        """Test abs() function."""
        assert SafeExpressionEvaluator.evaluate("abs(-5)") == 5
        assert SafeExpressionEvaluator.evaluate("abs(5)") == 5
        assert SafeExpressionEvaluator.evaluate("abs(-5.7)") == 5.7
        assert SafeExpressionEvaluator.evaluate("abs(0)") == 0

    def test_floor_function(self):
        """Test floor() function."""
        assert SafeExpressionEvaluator.evaluate("floor(3.14159)") == 3
        assert SafeExpressionEvaluator.evaluate("floor(3.9)") == 3
        assert SafeExpressionEvaluator.evaluate("floor(-2.5)") == -3
        assert SafeExpressionEvaluator.evaluate("floor(5)") == 5

    def test_ceil_function(self):
        """Test ceil() function."""
        assert SafeExpressionEvaluator.evaluate("ceil(3.14159)") == 4
        assert SafeExpressionEvaluator.evaluate("ceil(3.1)") == 4
        assert SafeExpressionEvaluator.evaluate("ceil(-2.5)") == -2
        assert SafeExpressionEvaluator.evaluate("ceil(5)") == 5

    def test_round_function(self):
        """Test round() function."""
        assert SafeExpressionEvaluator.evaluate("round(3.14159)") == 3
        assert SafeExpressionEvaluator.evaluate("round(3.6)") == 4
        assert SafeExpressionEvaluator.evaluate("round(3.14159, 2)") == pytest.approx(3.14)
        assert SafeExpressionEvaluator.evaluate("round(3.5)") == 4

    def test_sqrt_function(self):
        """Test sqrt() function."""
        assert SafeExpressionEvaluator.evaluate("sqrt(16)") == 4
        assert SafeExpressionEvaluator.evaluate("sqrt(25)") == 5
        assert SafeExpressionEvaluator.evaluate("sqrt(2)") == pytest.approx(1.41421, rel=1e-5)
        assert SafeExpressionEvaluator.evaluate("sqrt(0)") == 0

    def test_pow_function(self):
        """Test pow() function."""
        assert SafeExpressionEvaluator.evaluate("pow(2, 3)") == 8
        assert SafeExpressionEvaluator.evaluate("pow(5, 2)") == 25
        assert SafeExpressionEvaluator.evaluate("pow(10, 0)") == 1
        assert SafeExpressionEvaluator.evaluate("pow(2, -1)") == 0.5

    def test_min_max_functions(self):
        """Test min() and max() functions."""
        assert SafeExpressionEvaluator.evaluate("min(5, 10)") == 5
        assert SafeExpressionEvaluator.evaluate("min(10, 5)") == 5
        assert SafeExpressionEvaluator.evaluate("min(3, 1, 4, 1, 5, 9)") == 1
        assert SafeExpressionEvaluator.evaluate("max(5, 10)") == 10
        assert SafeExpressionEvaluator.evaluate("max(10, 5)") == 10
        assert SafeExpressionEvaluator.evaluate("max(3, 1, 4, 1, 5, 9)") == 9

    def test_trigonometric_functions(self):
        """Test trigonometric functions."""
        assert SafeExpressionEvaluator.evaluate("sin(0)") == 0
        assert SafeExpressionEvaluator.evaluate("cos(0)") == 1
        assert SafeExpressionEvaluator.evaluate("tan(0)") == 0
        # Test with pi
        import math
        assert SafeExpressionEvaluator.evaluate("sin(pi / 2)") == pytest.approx(1, rel=1e-10)
        assert SafeExpressionEvaluator.evaluate("cos(pi)") == pytest.approx(-1, rel=1e-10)

    def test_logarithmic_functions(self):
        """Test logarithmic functions."""
        import math
        assert SafeExpressionEvaluator.evaluate("log(e)") == pytest.approx(1, rel=1e-10)
        assert SafeExpressionEvaluator.evaluate("log10(100)") == 2
        assert SafeExpressionEvaluator.evaluate("log10(1000)") == 3
        assert SafeExpressionEvaluator.evaluate("exp(0)") == 1
        assert SafeExpressionEvaluator.evaluate("exp(1)") == pytest.approx(math.e, rel=1e-10)

    def test_math_constants(self):
        """Test math constants (pi, e, tau)."""
        import math
        assert SafeExpressionEvaluator.evaluate("pi") == pytest.approx(math.pi)
        assert SafeExpressionEvaluator.evaluate("e") == pytest.approx(math.e)
        assert SafeExpressionEvaluator.evaluate("tau") == pytest.approx(math.tau)
        # Test using constants in expressions
        assert SafeExpressionEvaluator.evaluate("2 * pi") == pytest.approx(2 * math.pi)
        assert SafeExpressionEvaluator.evaluate("pi / 2") == pytest.approx(math.pi / 2)

    def test_nested_math_functions(self):
        """Test nested math functions."""
        assert SafeExpressionEvaluator.evaluate("abs(floor(-3.7))") == 4
        assert SafeExpressionEvaluator.evaluate("sqrt(abs(-16))") == 4
        assert SafeExpressionEvaluator.evaluate("round(sqrt(50))") == 7
        assert SafeExpressionEvaluator.evaluate("max(abs(-5), sqrt(9))") == 5

    def test_math_functions_with_expressions(self):
        """Test math functions with complex expressions as arguments."""
        assert SafeExpressionEvaluator.evaluate("abs(5 - 10)") == 5
        assert SafeExpressionEvaluator.evaluate("sqrt(16 + 9)") == 5
        assert SafeExpressionEvaluator.evaluate("floor(pi * 2)") == 6
        assert SafeExpressionEvaluator.evaluate("max(2 + 3, 4 * 2)") == 8
