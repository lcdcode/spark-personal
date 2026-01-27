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

    def test_min_function(self, sample_cells):
        """Test MIN function."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=MIN(10,20,30)") == 10
        assert engine.evaluate("=MIN(A1,A2,A3)") == 10
        assert engine.evaluate("=min(5,3,8)") == 3  # Case insensitive

    def test_min_function_with_range(self, sample_cells):
        """Test MIN function with cell ranges."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=MIN(A1:A3)") == 10
        assert engine.evaluate("=MIN(B1:B3)") == 5

    def test_max_function(self, sample_cells):
        """Test MAX function."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=MAX(10,20,30)") == 30
        assert engine.evaluate("=MAX(A1,A2,A3)") == 30
        assert engine.evaluate("=max(5,3,8)") == 8  # Case insensitive

    def test_max_function_with_range(self, sample_cells):
        """Test MAX function with cell ranges."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=MAX(A1:A3)") == 30
        assert engine.evaluate("=MAX(B1:B3)") == 25

    def test_count_function(self, sample_cells):
        """Test COUNT function."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=COUNT(10,20,30)") == 3
        assert engine.evaluate("=COUNT(A1,A2,A3)") == 3
        assert engine.evaluate("=count(5,3,8,2)") == 4  # Case insensitive

    def test_count_function_with_range(self, sample_cells):
        """Test COUNT function with cell ranges."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=COUNT(A1:A3)") == 3
        assert engine.evaluate("=COUNT(B1:B3)") == 3

    def test_median_function(self, sample_cells):
        """Test MEDIAN function."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=MEDIAN(10,20,30)") == 20
        assert engine.evaluate("=MEDIAN(A1,A2,A3)") == 20
        assert engine.evaluate("=median(1,2,3,4)") == 2.5  # Even count
        assert engine.evaluate("=median(1,2,3)") == 2  # Odd count

    def test_median_function_with_range(self, sample_cells):
        """Test MEDIAN function with cell ranges."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=MEDIAN(A1:A3)") == 20
        assert engine.evaluate("=MEDIAN(B1:B3)") == 15

    def test_abs_function_in_formula(self, sample_cells):
        """Test ABS function in formulas."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=ABS(-5)") == 5
        assert engine.evaluate("=ABS(5)") == 5
        assert engine.evaluate("=abs(-3.7)") == 3.7  # Case insensitive

    def test_floor_function_in_formula(self, empty_cells):
        """Test FLOOR function in formulas."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("=FLOOR(3.14159)") == 3
        assert engine.evaluate("=FLOOR(3.9)") == 3
        assert engine.evaluate("=floor(-2.5)") == -3  # Case insensitive

    def test_ceiling_function_in_formula(self, empty_cells):
        """Test CEILING/CEIL function in formulas."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("=CEILING(3.14159)") == 4
        assert engine.evaluate("=CEIL(3.1)") == 4
        assert engine.evaluate("=ceiling(3.9)") == 4  # Case insensitive

    def test_round_function_in_formula(self, empty_cells):
        """Test ROUND function in formulas."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("=ROUND(3.14159)") == 3
        assert engine.evaluate("=ROUND(3.6)") == 4
        assert engine.evaluate("=round(3.5)") == 4  # Case insensitive

    def test_sqrt_function_in_formula(self, empty_cells):
        """Test SQRT function in formulas."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("=SQRT(16)") == 4
        assert engine.evaluate("=SQRT(25)") == 5
        assert engine.evaluate("=sqrt(9)") == 3  # Case insensitive

    def test_power_function_in_formula(self, empty_cells):
        """Test POWER/POW function in formulas."""
        engine = FormulaEngine(empty_cells)
        assert engine.evaluate("=POWER(2,3)") == 8
        assert engine.evaluate("=POW(5,2)") == 25
        assert engine.evaluate("=power(10,0)") == 1  # Case insensitive

    def test_mod_function_in_formula(self, sample_cells):
        """Test MOD function in formulas."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=MOD(10,3)") == 1
        assert engine.evaluate("=MOD(A2,3)") == 2  # A2=20, 20 % 3 = 2
        assert engine.evaluate("=mod(17,5)") == 2  # Case insensitive

    def test_pi_constant(self, empty_cells):
        """Test PI constant in formulas."""
        engine = FormulaEngine(empty_cells)
        import math
        result = engine.evaluate("=PI()")
        assert result == pytest.approx(math.pi)
        result = engine.evaluate("=PI")
        assert result == pytest.approx(math.pi)
        result = engine.evaluate("=2*PI()")
        assert result == pytest.approx(2 * math.pi)

    def test_e_constant(self, empty_cells):
        """Test E constant in formulas."""
        engine = FormulaEngine(empty_cells)
        import math
        result = engine.evaluate("=E()")
        assert result == pytest.approx(math.e)
        result = engine.evaluate("=E")
        assert result == pytest.approx(math.e)

    def test_combined_math_functions(self, sample_cells):
        """Test combining multiple math functions."""
        engine = FormulaEngine(sample_cells)
        # ABS(A1 - A2) = ABS(10 - 20) = 10
        assert engine.evaluate("=ABS(A1-A2)") == 10
        # SQRT(MAX(A1:A3)) = SQRT(30) = 5.477...
        result = engine.evaluate("=SQRT(MAX(A1:A3))")
        assert result == pytest.approx(5.477, rel=0.01)
        # ROUND(AVERAGE(A1:A3)) = ROUND(20) = 20
        assert engine.evaluate("=ROUND(AVERAGE(A1:A3))") == 20

    def test_math_functions_with_cell_references(self, sample_cells):
        """Test math functions with cell references."""
        engine = FormulaEngine(sample_cells)
        assert engine.evaluate("=FLOOR(A2/3)") == 6  # FLOOR(20/3) = 6
        assert engine.evaluate("=CEIL(A1/3)") == 4  # CEIL(10/3) = 4
        assert engine.evaluate("=ABS(B1-A1)") == 5  # ABS(5-10) = 5
