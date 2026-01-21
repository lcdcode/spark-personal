"""Unit tests for FormulaEngine class."""

import pytest
from datetime import datetime
from spark.spreadsheet_widget import FormulaEngine


class TestFormulaEngine:
    """Test cases for FormulaEngine class."""

    @pytest.fixture
    def empty_cells(self):
        """Empty cell dictionary for testing."""
        return {}

    @pytest.fixture
    def sample_cells(self):
        """Sample cell dictionary for testing."""
        return {
            "A1": "10",
            "A2": "20",
            "A3": "30",
            "B1": "5",
            "B2": "15",
            "B3": "25",
            "C1": "=A1+B1",
        }

    def test_non_formula_passthrough(self, empty_cells):
        """Test that non-formula values pass through unchanged."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("Hello") == "Hello"
        assert engine.evaluate("123") == "123"
        assert engine.evaluate("text") == "text"

    def test_basic_arithmetic_formulas(self, empty_cells):
        """Test basic arithmetic in formulas."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("=2+3") == 5
        assert engine.evaluate("=10-4") == 6
        assert engine.evaluate("=5*6") == 30
        assert engine.evaluate("=20/4") == 5

    def test_equality_operator_normalization(self, empty_cells):
        """Test that single = is converted to == in comparisons."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("=5=5") is True
        assert engine.evaluate("=5=6") is False
        assert engine.evaluate("=10==10") is True

    def test_exponentiation_operator_normalization(self, empty_cells):
        """Test that ^ is converted to ** for exponentiation."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("=2^8") == 256
        assert engine.evaluate("=3^3") == 27

    def test_cell_references(self, sample_cells):
        """Test cell reference substitution."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=A1") == 10.0
        assert engine.evaluate("=B2") == 15.0
        assert engine.evaluate("=A1+B1") == 15.0
        assert engine.evaluate("=A2-B1") == 15.0

    def test_cell_reference_in_formula(self, sample_cells):
        """Test formulas with cell references."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=A1*2") == 20.0
        assert engine.evaluate("=A1+A2+A3") == 60.0
        assert engine.evaluate("=(A1+B1)*2") == 30.0

    def test_recursive_formula_evaluation(self, sample_cells):
        """Test that formulas in cells are evaluated recursively."""
        engine = FormulaEngine(sample_cells)
        # C1 contains "=A1+B1", which should evaluate to 15
        assert engine.evaluate("=C1*2") == 30.0

    def test_sum_function(self, sample_cells):
        """Test SUM function."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=SUM(10,20,30)") == 60
        assert engine.evaluate("=SUM(A1,A2)") == 30
        assert engine.evaluate("=sum(5,10)") == 15  # Case insensitive

    def test_sum_function_with_range(self, sample_cells):
        """Test SUM function with cell ranges."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=SUM(A1:A3)") == 60
        assert engine.evaluate("=SUM(B1:B3)") == 45

    def test_average_function(self, sample_cells):
        """Test AVERAGE function."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=AVERAGE(10,20,30)") == 20
        assert engine.evaluate("=AVERAGE(A1,A2,A3)") == 20
        assert engine.evaluate("=average(5,15)") == 10  # Case insensitive

    def test_average_function_with_range(self, sample_cells):
        """Test AVERAGE function with cell ranges."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=AVERAGE(A1:A3)") == 20
        assert engine.evaluate("=AVERAGE(B1:B3)") == 15

    def test_if_function(self, sample_cells):
        """Test IF function."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=IF(5>3,10,20)") == 10
        assert engine.evaluate("=IF(5<3,10,20)") == 20
        assert engine.evaluate("=IF(A1>5,100,200)") == 100
        assert engine.evaluate("=IF(B1>10,100,200)") == 200

    def test_if_function_with_cell_reference(self, sample_cells):
        """Test IF function with cell references in condition."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=IF(A1=10,A2,B2)") == 20.0
        assert engine.evaluate("=IF(A1>B1,A1,B1)") == 10.0

    def test_if_function_case_insensitive(self, sample_cells):
        """Test IF function is case insensitive."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=if(5>3,10,20)") == 10

    def test_today_function(self, empty_cells):
        """Test TODAY function returns a numeric timestamp."""
        engine = FormulaEngine(empty_cells)
        result = engine.evaluate("=TODAY()")
        # Should return a numeric value (days since epoch)
        assert isinstance(result, (int, float))
        assert result > 0

    def test_now_function(self, empty_cells):
        """Test NOW function returns a numeric timestamp."""
        engine = FormulaEngine(empty_cells)
        result = engine.evaluate("=NOW()")
        # Should return a numeric value (days since epoch with fractional part)
        assert isinstance(result, (int, float))
        assert result > 0

    def test_today_and_now_difference(self, empty_cells):
        """Test that NOW is greater than TODAY (same day but includes time)."""
        engine = FormulaEngine(empty_cells)
        today = engine.evaluate("=TODAY()")
        now = engine.evaluate("=NOW()")
        # NOW should be >= TODAY (could be equal at exactly midnight)
        assert now >= today

    def test_date_function(self, empty_cells):
        """Test DATE function converts timestamp to date string."""
        engine = FormulaEngine(empty_cells)
        # Use a known timestamp (days since epoch)
        # Jan 1, 1970 = 0 days
        result = engine.evaluate("=DATE(0)")
        assert isinstance(result, str)
        assert "1970-01-01" in result or "1969-12-31" in result  # Timezone dependent

    def test_date_function_with_today(self, empty_cells):
        """Test DATE function with TODAY()."""
        engine = FormulaEngine(empty_cells)
        result = engine.evaluate("=DATE(TODAY())")
        # Should return today's date as a string
        assert isinstance(result, str)
        today_str = datetime.now().strftime("%Y-%m-%d")
        assert today_str in result

    def test_date_arithmetic(self, empty_cells):
        """Test date arithmetic with TODAY."""
        engine = FormulaEngine(empty_cells)
        # Adding days to today
        result = engine.evaluate("=DATE(TODAY()+7)")
        assert isinstance(result, str)
        # Should be a valid date string
        assert "-" in result

    def test_boolean_functions(self, empty_cells):
        """Test boolean functions (AND, OR, NOT)."""
        engine = FormulaEngine(empty_cells)
        # Note: The boolean functions are hardcoded replacements
        # They work with literal True/False values
        assert engine.evaluate("=AND(True,True)") is True
        assert engine.evaluate("=OR(False,False)") is False
        assert engine.evaluate("=NOT(True)") is False
        assert engine.evaluate("=NOT(False)") is True

    def test_complex_formula(self, sample_cells):
        """Test complex formulas with multiple operations."""
        engine = FormulaEngine(sample_cells)
        # (A1 + A2) * B1 / 2 = (10 + 20) * 5 / 2 = 75
        assert engine.evaluate("=(A1+A2)*B1/2") == 75.0

    def test_nested_functions(self, sample_cells):
        """Test nested functions with cell ranges."""
        engine = FormulaEngine(sample_cells)
        # Test SUM with multiple ranges
        result = engine.evaluate("=SUM(A1:A2,B1:B2)")
        # A1=10, A2=20, B1=5, B2=15 -> SUM=50
        assert result == 50

    def test_cell_range_expansion(self):
        """Test cell range expansion."""
        cells = {
            "A1": "1",
            "A2": "2",
            "A3": "3",
            "A4": "4",
            "A5": "5",
        }
        engine = FormulaEngine(cells)
        assert engine.evaluate("=SUM(A1:A5)") == 15

    def test_multi_column_range(self):
        """Test multi-column cell range."""
        cells = {
            "A1": "1", "B1": "2",
            "A2": "3", "B2": "4",
        }
        engine = FormulaEngine(cells)
        assert engine.evaluate("=SUM(A1:B2)") == 10

    def test_empty_cell_references(self, empty_cells):
        """Test that empty cell references default to 0."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("=A1+5") == 5.0
        assert engine.evaluate("=SUM(A1,A2,A3)") == 0

    def test_formula_with_spaces(self, sample_cells):
        """Test formulas with spaces."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("= A1 + B1 ") == 15.0
        assert engine.evaluate("=  SUM( A1 , A2 )  ") == 30

    def test_error_handling(self, empty_cells):
        """Test error handling for invalid formulas."""
        engine = FormulaEngine(empty_cells)
        result = engine.evaluate("=invalid formula")
        assert "#ERROR" in str(result)

        result = engine.evaluate("=1/0")
        assert "#ERROR" in str(result)

    def test_comparison_in_formula(self, sample_cells):
        """Test comparison operators in formulas."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=A1>B1") is True
        assert engine.evaluate("=A1<B1") is False
        assert engine.evaluate("=A1>=10") is True
        assert engine.evaluate("=B1<=5") is True

    def test_boolean_logic_in_formula(self, sample_cells):
        """Test boolean logic in formulas."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=A1>5 and B1<10") is True
        assert engine.evaluate("=A1<5 or B1<10") is True
        assert engine.evaluate("=A1<5 and B1>10") is False

    def test_sum_with_mixed_arguments(self, sample_cells):
        """Test SUM with both cell references and literals."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=SUM(A1,10,20)") == 40
        assert engine.evaluate("=SUM(5,B1,15)") == 25

    def test_average_empty_values(self, empty_cells):
        """Test AVERAGE with no values returns 0."""
        engine = FormulaEngine(empty_cells)
        result = engine.evaluate("=AVERAGE(A1,A2)")
        assert result == 0

    def test_non_numeric_cell_values(self):
        """Test handling of non-numeric cell values."""
        cells = {"A1": "text", "B1": "10"}
        engine = FormulaEngine(cells)
        # Non-numeric values should default to 0
        assert engine.evaluate("=A1+B1") == 10.0

    def test_formula_with_parentheses(self, sample_cells):
        """Test formulas with multiple levels of parentheses."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=((A1+A2)*B1)/3") == 50.0
        assert engine.evaluate("=(A1+(A2*B1))/2") == 55.0

    def test_whitespace_handling(self, sample_cells):
        """Test that formulas handle whitespace correctly."""
        engine = FormulaEngine(sample_cells)
        # Whitespace in cell ranges is not supported in the current implementation
        # but whitespace around operators works fine
        assert engine.evaluate("= A1 + B1 ") == 15.0
        assert engine.evaluate("=  SUM( A1 , A2 )  ") == 30
