"""Spreadsheet widget with formula engine."""

import json
import re
import ast
import operator
import math
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QListWidget, QSplitter, QInputDialog,
    QMessageBox, QHeaderView, QMenu, QAbstractItemView, QLabel
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QKeyEvent, QFont
from typing import Dict, Any, Optional


class SafeExpressionEvaluator:
    """Safe expression evaluator using AST parsing instead of eval()."""

    # Allowed operators
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Allowed comparison operators
    COMPARISONS = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
    }

    # Allowed boolean operators
    BOOL_OPS = {
        ast.And: lambda x, y: x and y,
        ast.Or: lambda x, y: x or y,
    }

    # Allowed math functions (for direct evaluation in expressions)
    MATH_FUNCTIONS = {
        'abs': abs,
        'round': round,
        'floor': math.floor,
        'ceil': math.ceil,
        'trunc': math.trunc,
        'sqrt': math.sqrt,
        'pow': pow,
        'exp': math.exp,
        'log': math.log,
        'log10': math.log10,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'degrees': math.degrees,
        'radians': math.radians,
        'min': min,
        'max': max,
    }

    # Math constants
    MATH_CONSTANTS = {
        'pi': math.pi,
        'e': math.e,
        'tau': math.tau,
    }

    @staticmethod
    def evaluate(expr: str) -> Any:
        """Safely evaluate a mathematical expression."""
        try:
            node = ast.parse(expr, mode='eval').body
            return SafeExpressionEvaluator._eval_node(node)
        except Exception as e:
            raise ValueError(f"Invalid expression: {str(e)}")

    @staticmethod
    def _eval_node(node):
        """Recursively evaluate AST nodes."""
        if isinstance(node, ast.Constant):  # Python 3.8+
            return node.value
        elif isinstance(node, ast.Num):  # Legacy support
            return node.n
        elif isinstance(node, ast.Str):  # Legacy support
            return node.s
        elif isinstance(node, ast.UnaryOp):
            op = SafeExpressionEvaluator.OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            operand = SafeExpressionEvaluator._eval_node(node.operand)
            return op(operand)
        elif isinstance(node, ast.BinOp):
            op = SafeExpressionEvaluator.OPERATORS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
            left = SafeExpressionEvaluator._eval_node(node.left)
            right = SafeExpressionEvaluator._eval_node(node.right)
            return op(left, right)
        elif isinstance(node, ast.Compare):
            if len(node.ops) != 1:
                raise ValueError("Chained comparisons not supported")
            op = SafeExpressionEvaluator.COMPARISONS.get(type(node.ops[0]))
            if op is None:
                raise ValueError(f"Unsupported comparison: {type(node.ops[0]).__name__}")
            left = SafeExpressionEvaluator._eval_node(node.left)
            right = SafeExpressionEvaluator._eval_node(node.comparators[0])
            return op(left, right)
        elif isinstance(node, ast.BoolOp):
            op = SafeExpressionEvaluator.BOOL_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported boolean operator: {type(node.op).__name__}")
            values = [SafeExpressionEvaluator._eval_node(v) for v in node.values]
            result = values[0]
            for val in values[1:]:
                result = op(result, val)
            return result
        elif isinstance(node, ast.NameConstant):  # True, False, None (Python 3.7)
            return node.value
        elif isinstance(node, ast.Call):
            # Handle function calls
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in SafeExpressionEvaluator.MATH_FUNCTIONS:
                    func = SafeExpressionEvaluator.MATH_FUNCTIONS[func_name]
                    args = [SafeExpressionEvaluator._eval_node(arg) for arg in node.args]
                    return func(*args)
                else:
                    raise ValueError(f"Unknown or unsafe function: {func_name}")
            else:
                raise ValueError(f"Unsupported function call type: {type(node.func).__name__}")
        elif isinstance(node, ast.Name):
            # Handle named constants
            if node.id in SafeExpressionEvaluator.MATH_CONSTANTS:
                return SafeExpressionEvaluator.MATH_CONSTANTS[node.id]
            else:
                raise ValueError(f"Unknown constant or variable: {node.id}")
        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")


class FormulaEngine:
    """Simple formula engine for spreadsheet calculations."""

    def __init__(self, cells: Dict[str, Any]):
        self.cells = cells

    def evaluate(self, formula: str) -> Any:
        """Evaluate a formula."""
        if not formula.startswith('='):
            return formula

        formula = formula[1:].strip()

        # Normalize single = to == for equality comparisons
        # (but not in cell ranges or function calls)
        formula = self.normalize_equality_operator(formula)

        # Handle functions first (preserves cell references in function arguments)
        formula = self.handle_functions(formula)

        # Replace cell references with values after function handling
        formula = self.replace_cell_references(formula)

        try:
            result = SafeExpressionEvaluator.evaluate(formula)
            return result
        except Exception as e:
            return f"#ERROR: {str(e)}"

    def normalize_equality_operator(self, formula: str) -> str:
        """
        Convert single = to == for equality comparisons.
        This allows users to write formulas like IF(A1=5,10,20) instead of IF(A1==5,10,20).

        Strategy: Replace = with == only when it's not already ==, !=, <=, or >=
        """
        # Replace = with == but skip ==, !=, <=, >=
        # Use negative lookbehind and negative lookahead to avoid double replacement
        normalized = re.sub(
            r'(?<![=!<>])=(?!=)',  # Match = not preceded by =!<> and not followed by =
            '==',
            formula
        )

        # Also convert ^ to ** for exponentiation (Excel-style)
        normalized = normalized.replace('^', '**')

        return normalized

    def replace_cell_references(self, formula: str) -> str:
        """Replace cell references (A1, B2, etc.) with their values."""
        pattern = r'\b([A-Z]+)(\d+)\b'

        def replace(match):
            cell_ref = match.group(0)
            value = self.cells.get(cell_ref, 0)
            if isinstance(value, str) and value.startswith('='):
                value = self.evaluate(value)

            # Try to convert to float first
            try:
                return str(float(value))
            except (ValueError, TypeError):
                # Check if it's a date string (YYYY-MM-DD format)
                if isinstance(value, str):
                    try:
                        # Try parsing as date
                        date_obj = datetime.strptime(value, "%Y-%m-%d")
                        # Convert to timestamp (days since epoch)
                        timestamp = date_obj.timestamp() / 86400
                        return str(timestamp)
                    except ValueError:
                        pass
                return '0'

        return re.sub(pattern, replace, formula)

    def handle_functions(self, formula: str) -> str:
        """Handle spreadsheet functions."""
        # Process in multiple passes to handle nested functions properly

        # First pass: Replace constants and zero-argument functions
        # PI constant
        formula = re.sub(r'\bPI\(\)', str(math.pi), formula, flags=re.IGNORECASE)
        formula = re.sub(r'\bPI\b', str(math.pi), formula, flags=re.IGNORECASE)

        # E constant
        formula = re.sub(r'\bE\(\)', str(math.e), formula, flags=re.IGNORECASE)
        formula = re.sub(r'\bE\b', str(math.e), formula, flags=re.IGNORECASE)

        # TODAY function - returns numeric timestamp (days since epoch)
        today_timestamp = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() / 86400
        formula = re.sub(r'TODAY\(\)', str(today_timestamp), formula, flags=re.IGNORECASE)

        # NOW function - returns numeric timestamp (days since epoch with fractional part for time)
        now_timestamp = datetime.now().timestamp() / 86400
        formula = re.sub(r'NOW\(\)', str(now_timestamp), formula, flags=re.IGNORECASE)

        # Second pass: Process other functions that may use TODAY/NOW results
        # SUM function
        formula = re.sub(
            r'SUM\((.*?)\)',
            lambda m: str(self.func_sum(m.group(1))),
            formula,
            flags=re.IGNORECASE
        )

        # AVERAGE function
        formula = re.sub(
            r'AVERAGE\((.*?)\)',
            lambda m: str(self.func_average(m.group(1))),
            formula,
            flags=re.IGNORECASE
        )

        # IF function
        formula = re.sub(
            r'IF\((.*?),(.*?),(.*?)\)',
            lambda m: self.func_if(m.group(1), m.group(2), m.group(3)),
            formula,
            flags=re.IGNORECASE
        )

        # DATE function - converts a numeric timestamp back to date string
        # Process this last so it can work with results from other functions
        formula = re.sub(
            r'DATE\((.*?)\)',
            lambda m: self.func_date(m.group(1)),
            formula,
            flags=re.IGNORECASE
        )

        # TIME function - converts a numeric timestamp to time string (HH:MM:SS)
        formula = re.sub(
            r'TIME\((.*?)\)',
            lambda m: self.func_time(m.group(1)),
            formula,
            flags=re.IGNORECASE
        )

        # MIN function
        formula = re.sub(
            r'MIN\((.*?)\)',
            lambda m: str(self.func_min(m.group(1))),
            formula,
            flags=re.IGNORECASE
        )

        # MAX function
        formula = re.sub(
            r'MAX\((.*?)\)',
            lambda m: str(self.func_max(m.group(1))),
            formula,
            flags=re.IGNORECASE
        )

        # COUNT function
        formula = re.sub(
            r'COUNT\((.*?)\)',
            lambda m: str(self.func_count(m.group(1))),
            formula,
            flags=re.IGNORECASE
        )

        # MEDIAN function
        formula = re.sub(
            r'MEDIAN\((.*?)\)',
            lambda m: str(self.func_median(m.group(1))),
            formula,
            flags=re.IGNORECASE
        )

        # MOD function (modulo operation)
        formula = re.sub(
            r'MOD\((.*?),(.*?)\)',
            lambda m: f'({m.group(1)} % {m.group(2)})',
            formula,
            flags=re.IGNORECASE
        )

        # FLOOR function (spreadsheet-style, converts to lowercase for Python)
        formula = re.sub(
            r'FLOOR\((.*?)\)',
            lambda m: f'floor({m.group(1)})',
            formula,
            flags=re.IGNORECASE
        )

        # CEILING/CEIL function (spreadsheet-style, converts to lowercase for Python)
        formula = re.sub(
            r'CEILING\((.*?)\)',
            lambda m: f'ceil({m.group(1)})',
            formula,
            flags=re.IGNORECASE
        )
        formula = re.sub(
            r'CEIL\((.*?)\)',
            lambda m: f'ceil({m.group(1)})',
            formula,
            flags=re.IGNORECASE
        )

        # ABS function (spreadsheet-style, converts to lowercase for Python)
        formula = re.sub(
            r'ABS\((.*?)\)',
            lambda m: f'abs({m.group(1)})',
            formula,
            flags=re.IGNORECASE
        )

        # ROUND function (spreadsheet-style, converts to lowercase for Python)
        formula = re.sub(
            r'ROUND\((.*?)\)',
            lambda m: f'round({m.group(1)})',
            formula,
            flags=re.IGNORECASE
        )

        # SQRT function (spreadsheet-style, converts to lowercase for Python)
        formula = re.sub(
            r'SQRT\((.*?)\)',
            lambda m: f'sqrt({m.group(1)})',
            formula,
            flags=re.IGNORECASE
        )

        # POWER/POW function (spreadsheet-style, converts to lowercase for Python)
        formula = re.sub(
            r'POWER\((.*?)\)',
            lambda m: f'pow({m.group(1)})',
            formula,
            flags=re.IGNORECASE
        )
        formula = re.sub(
            r'POW\((.*?)\)',
            lambda m: f'pow({m.group(1)})',
            formula,
            flags=re.IGNORECASE
        )

        # Boolean functions - AND, OR, NOT
        # These need special handling because they can have variable numbers of arguments

        # NOT function (single argument)
        formula = re.sub(
            r'\bNOT\((.*?)\)',
            lambda m: self.func_not(m.group(1)),
            formula,
            flags=re.IGNORECASE
        )

        # AND function (variable arguments) - use a custom parser
        def process_and(match):
            args = match.group(1)
            # Split by commas but respect nested parentheses
            conditions = self._split_function_args(args)
            return self.func_and(*conditions)

        formula = re.sub(
            r'\bAND\((.*?)\)',
            process_and,
            formula,
            flags=re.IGNORECASE
        )

        # OR function (variable arguments) - use a custom parser
        def process_or(match):
            args = match.group(1)
            # Split by commas but respect nested parentheses
            conditions = self._split_function_args(args)
            return self.func_or(*conditions)

        formula = re.sub(
            r'\bOR\((.*?)\)',
            process_or,
            formula,
            flags=re.IGNORECASE
        )

        return formula

    def func_sum(self, args: str) -> float:
        """SUM function implementation."""
        values = self._parse_function_args(args)
        return sum(values)

    def func_average(self, args: str) -> float:
        """AVERAGE function implementation."""
        values = self._parse_function_args(args)
        return sum(values) / len(values) if values else 0

    def func_min(self, args: str) -> float:
        """MIN function implementation."""
        values = self._parse_function_args(args)
        return min(values) if values else 0

    def func_max(self, args: str) -> float:
        """MAX function implementation."""
        values = self._parse_function_args(args)
        return max(values) if values else 0

    def func_count(self, args: str) -> int:
        """COUNT function implementation."""
        values = self._parse_function_args(args)
        return len(values)

    def func_median(self, args: str) -> float:
        """MEDIAN function implementation."""
        values = self._parse_function_args(args)
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            # Even number of values - average the two middle ones
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
        else:
            # Odd number of values - return the middle one
            return sorted_values[n // 2]

    def _split_function_args(self, args: str) -> list:
        """Split function arguments by commas while respecting nested parentheses."""
        parts = []
        current = []
        depth = 0

        for char in args:
            if char == ',' and depth == 0:
                parts.append(''.join(current).strip())
                current = []
            else:
                if char == '(':
                    depth += 1
                elif char == ')':
                    depth -= 1
                current.append(char)

        # Add the last part
        if current:
            parts.append(''.join(current).strip())

        return parts

    def _parse_function_args(self, args: str) -> list:
        """Parse function arguments including cell references and ranges."""
        values = []
        parts = [p.strip() for p in args.split(',')]

        for part in parts:
            # Check if it's a range (e.g., B3:B4)
            if ':' in part:
                values.extend(self._expand_range(part))
            # Check if it's a cell reference (e.g., B3)
            elif re.match(r'^[A-Z]+\d+$', part):
                cell_value = self.cells.get(part, 0)
                # If cell contains a formula, evaluate it
                if isinstance(cell_value, str) and cell_value.startswith('='):
                    cell_value = self.evaluate(cell_value)
                try:
                    values.append(float(cell_value))
                except (ValueError, TypeError):
                    values.append(0)
            # Otherwise, it's a literal number
            else:
                try:
                    values.append(float(part))
                except (ValueError, TypeError):
                    pass

        return values

    def _expand_range(self, range_str: str) -> list:
        """Expand a cell range (e.g., B3:B4) into individual values."""
        match = re.match(r'([A-Z]+)(\d+):([A-Z]+)(\d+)', range_str)
        if not match:
            return []

        start_col, start_row, end_col, end_row = match.groups()
        start_row, end_row = int(start_row), int(end_row)

        values = []
        # Handle single column range (most common, e.g., B3:B4)
        if start_col == end_col:
            for row in range(start_row, end_row + 1):
                cell_ref = f"{start_col}{row}"
                cell_value = self.cells.get(cell_ref, 0)
                # If cell contains a formula, evaluate it
                if isinstance(cell_value, str) and cell_value.startswith('='):
                    cell_value = self.evaluate(cell_value)
                try:
                    values.append(float(cell_value))
                except (ValueError, TypeError):
                    values.append(0)
        else:
            # Handle multi-column ranges (e.g., A1:B2)
            start_col_idx = sum((ord(c) - 65) * (26 ** i) for i, c in enumerate(reversed(start_col)))
            end_col_idx = sum((ord(c) - 65) * (26 ** i) for i, c in enumerate(reversed(end_col)))

            for row in range(start_row, end_row + 1):
                for col_idx in range(start_col_idx, end_col_idx + 1):
                    # Convert column index back to letter
                    col_name = ""
                    temp_idx = col_idx
                    while temp_idx >= 0:
                        col_name = chr(65 + (temp_idx % 26)) + col_name
                        temp_idx = temp_idx // 26 - 1

                    cell_ref = f"{col_name}{row}"
                    cell_value = self.cells.get(cell_ref, 0)
                    # If cell contains a formula, evaluate it
                    if isinstance(cell_value, str) and cell_value.startswith('='):
                        cell_value = self.evaluate(cell_value)
                    try:
                        values.append(float(cell_value))
                    except (ValueError, TypeError):
                        values.append(0)

        return values

    def func_if(self, condition: str, true_val: str, false_val: str) -> str:
        """IF function implementation."""
        try:
            # Replace cell references in condition
            condition = self.replace_cell_references(condition)
            result = SafeExpressionEvaluator.evaluate(condition)
            return true_val if result else false_val
        except Exception as e:
            # Return false value if condition evaluation fails
            return false_val

    def func_and(self, *conditions: str) -> str:
        """AND function - returns True if all conditions are true."""
        try:
            for condition in conditions:
                # Replace cell references in each condition
                condition_resolved = self.replace_cell_references(condition.strip())
                result = SafeExpressionEvaluator.evaluate(condition_resolved)
                if not result:
                    return 'False'
            return 'True'
        except Exception as e:
            return 'False'

    def func_or(self, *conditions: str) -> str:
        """OR function - returns True if any condition is true."""
        try:
            for condition in conditions:
                # Replace cell references in each condition
                condition_resolved = self.replace_cell_references(condition.strip())
                result = SafeExpressionEvaluator.evaluate(condition_resolved)
                if result:
                    return 'True'
            return 'False'
        except Exception as e:
            return 'False'

    def func_not(self, condition: str) -> str:
        """NOT function - returns the opposite boolean value."""
        try:
            # Replace cell references in condition
            condition_resolved = self.replace_cell_references(condition.strip())
            result = SafeExpressionEvaluator.evaluate(condition_resolved)
            return 'False' if result else 'True'
        except Exception as e:
            return 'True'

    def func_date(self, args: str) -> str:
        """DATE function - converts numeric timestamp (days since epoch) back to date string."""
        args = args.strip()

        # First, replace any cell references in the argument
        args = self.replace_cell_references(args)

        try:
            # Evaluate the expression to get the numeric value
            timestamp = SafeExpressionEvaluator.evaluate(args)
            # Convert from days to seconds and create datetime
            date_obj = datetime.fromtimestamp(float(timestamp) * 86400)
            # Return formatted date string in quotes (so it's treated as a string in the formula)
            return f'"{date_obj.strftime("%Y-%m-%d")}"'
        except Exception as e:
            return f'"#ERROR: {str(e)}"'

    def func_time(self, args: str) -> str:
        """TIME function - converts numeric timestamp to time string (HH:MM:SS format)."""
        args = args.strip()

        # First, replace any cell references in the argument
        args = self.replace_cell_references(args)

        try:
            # Evaluate the expression to get the numeric value
            timestamp = SafeExpressionEvaluator.evaluate(args)
            # Convert from days to seconds and create datetime
            time_obj = datetime.fromtimestamp(float(timestamp) * 86400)
            # Return formatted time string in quotes (24-hour format: HH:MM:SS)
            return f'"{time_obj.strftime("%H:%M:%S")}"'
        except Exception as e:
            return f'"#ERROR: {str(e)}"'


class SpreadsheetTableWidget(QTableWidget):
    """Custom table widget with Enter key navigation."""

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Check if we're currently editing a cell
            if self.state() != QAbstractItemView.State.EditingState:
                # Not editing - move to cell below
                current_row = self.currentRow()
                current_col = self.currentColumn()
                if current_row < self.rowCount() - 1:
                    self.setCurrentCell(current_row + 1, current_col)
                return
        elif event.key() == Qt.Key.Key_Delete:
            # Delete key - clear the current cell
            if self.state() != QAbstractItemView.State.EditingState:
                current_row = self.currentRow()
                current_col = self.currentColumn()
                if current_row >= 0 and current_col >= 0:
                    # Clear the cell content
                    item = self.item(current_row, current_col)
                    if item:
                        item.setText("")
                return
        # For all other keys or when editing, use default behavior
        super().keyPressEvent(event)


class SpreadsheetWidget(QWidget):
    """Widget for managing spreadsheets."""

    sheet_modified = pyqtSignal()

    def __init__(self, database, config, parent=None):
        super().__init__(parent)
        self.database = database
        self.config = config
        self.current_sheet_id = None
        self.current_sheet_name = None  # Track current sheet name separately
        self.is_modified = False
        self.undo_stack = []
        self.redo_stack = []
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)

        self.init_ui()
        self.load_sheets()

        # Start autosave timer
        if self.config.get('autosave_enabled', True):
            interval = self.config.get('autosave_interval_seconds', 300) * 1000
            self.autosave_timer.start(interval)

    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)

        # Left panel: Sheet list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.sheet_list = QListWidget()
        self.sheet_list.itemClicked.connect(self.on_sheet_selected)
        self.sheet_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sheet_list.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.sheet_list)

        # Buttons
        button_layout = QVBoxLayout()
        self.btn_add = QPushButton("New Sheet")
        self.btn_add.clicked.connect(self.add_sheet)
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_sheet)
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_delete)
        left_layout.addLayout(button_layout)

        # Right panel: Spreadsheet
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Formula bar
        formula_layout = QHBoxLayout()
        self.formula_bar = QLineEdit()
        self.formula_bar.setPlaceholderText("Formula bar (enter formula or value)")
        self.formula_bar.returnPressed.connect(self.on_formula_enter)
        formula_layout.addWidget(self.formula_bar)

        self.btn_recalc = QPushButton("Recalculate")
        self.btn_recalc.clicked.connect(self.recalculate)
        formula_layout.addWidget(self.btn_recalc)
        right_layout.addLayout(formula_layout)

        # Formatting toolbar
        format_layout = QHBoxLayout()
        self.btn_bold = QPushButton("B")
        self.btn_bold.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_bold.setCheckable(True)
        self.btn_bold.setMaximumWidth(40)
        self.btn_bold.clicked.connect(self.toggle_bold)
        self.btn_bold.setToolTip("Bold (Ctrl+B)")

        self.btn_italic = QPushButton("I")
        italic_font = QFont("Arial", 10)
        italic_font.setItalic(True)
        self.btn_italic.setFont(italic_font)
        self.btn_italic.setCheckable(True)
        self.btn_italic.setMaximumWidth(40)
        self.btn_italic.clicked.connect(self.toggle_italic)
        self.btn_italic.setToolTip("Italic (Ctrl+I)")

        self.btn_underline = QPushButton("U")
        underline_font = QFont("Arial", 10)
        underline_font.setUnderline(True)
        self.btn_underline.setFont(underline_font)
        self.btn_underline.setCheckable(True)
        self.btn_underline.setMaximumWidth(40)
        self.btn_underline.clicked.connect(self.toggle_underline)
        self.btn_underline.setToolTip("Underline (Ctrl+U)")

        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(self.btn_bold)
        format_layout.addWidget(self.btn_italic)
        format_layout.addWidget(self.btn_underline)
        format_layout.addStretch()
        right_layout.addLayout(format_layout)

        # Table
        self.table = SpreadsheetTableWidget(100, 26)
        self.table.setHorizontalHeaderLabels([self.col_name(i) for i in range(26)])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.currentCellChanged.connect(self.on_cell_selected)
        self.table.itemChanged.connect(self.on_cell_changed)

        # Connect header resize events to mark sheet as modified
        self.table.horizontalHeader().sectionResized.connect(self.on_header_resized)
        self.table.verticalHeader().sectionResized.connect(self.on_header_resized)

        right_layout.addWidget(self.table)

        # Undo/Redo buttons
        undo_layout = QHBoxLayout()
        self.btn_undo = QPushButton("Undo")
        self.btn_undo.clicked.connect(self.undo)
        self.btn_redo = QPushButton("Redo")
        self.btn_redo.clicked.connect(self.redo)
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_current_sheet)
        undo_layout.addWidget(self.btn_undo)
        undo_layout.addWidget(self.btn_redo)
        undo_layout.addWidget(self.btn_save)
        right_layout.addLayout(undo_layout)

        # Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 4)

        # Add toggle button for sidebar
        toggle_button_layout = QHBoxLayout()
        self.btn_toggle_sidebar = QPushButton("<<")
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        self.btn_toggle_sidebar.setMaximumWidth(40)
        self.btn_toggle_sidebar.setToolTip("Hide Sidebar")
        toggle_button_layout.addWidget(self.btn_toggle_sidebar)
        toggle_button_layout.addStretch()
        right_layout.insertLayout(0, toggle_button_layout)

        # Store left panel reference for toggling
        self.left_panel = left_panel
        self.sidebar_visible = True

        layout.addWidget(self.splitter)

    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        if self.sidebar_visible:
            # Hide sidebar
            self.left_panel.hide()
            self.btn_toggle_sidebar.setText("Show Sidebar")
            self.btn_toggle_sidebar.setMaximumWidth(150)
            self.btn_toggle_sidebar.setToolTip("Show Sidebar")
            self.sidebar_visible = False
        else:
            # Show sidebar
            self.left_panel.show()
            self.btn_toggle_sidebar.setText("<<")
            self.btn_toggle_sidebar.setMaximumWidth(40)
            self.btn_toggle_sidebar.setToolTip("Hide Sidebar")
            self.sidebar_visible = True

    def col_name(self, index: int) -> str:
        """Convert column index to letter (0->A, 1->B, etc.)."""
        name = ""
        while index >= 0:
            name = chr(65 + (index % 26)) + name
            index = index // 26 - 1
        return name

    def cell_ref(self, row: int, col: int) -> str:
        """Get cell reference (e.g., A1)."""
        return f"{self.col_name(col)}{row + 1}"

    def load_sheets(self):
        """Load spreadsheets into the list."""
        self.sheet_list.clear()
        sheets = self.database.get_all_spreadsheets()
        for sheet in sheets:
            self.sheet_list.addItem(sheet['name'])
            # Get the item that was just added
            item = self.sheet_list.item(self.sheet_list.count() - 1)
            item.setData(Qt.ItemDataRole.UserRole, sheet['id'])

    def on_sheet_selected(self, item):
        """Handle sheet selection."""
        if self.is_modified:
            self.save_current_sheet()

        sheet_id = item.data(Qt.ItemDataRole.UserRole)
        sheet = self.database.get_spreadsheet(sheet_id)

        if sheet:
            self.current_sheet_id = sheet_id
            self.current_sheet_name = sheet['name']  # Store the name
            self.load_sheet_data(sheet['data'])
            self.is_modified = False

    def load_sheet_data(self, data: str):
        """Load sheet data into the table."""
        self.table.blockSignals(True)
        self.table.clearContents()

        try:
            sheet_data = json.loads(data) if data else {}

            # Load cell data (backward compatible with old format)
            cells = sheet_data if isinstance(sheet_data, dict) and 'cells' not in sheet_data else sheet_data.get('cells', {})

            for cell_ref, value in cells.items():
                row, col = self.parse_cell_ref(cell_ref)
                if row < self.table.rowCount() and col < self.table.columnCount():
                    item = QTableWidgetItem(str(value))
                    # If value is a formula, store it in UserRole
                    if str(value).startswith('='):
                        item.setData(Qt.ItemDataRole.UserRole, str(value))
                    self.table.setItem(row, col, item)

            # Load cell formatting if available
            if isinstance(sheet_data, dict) and 'cell_formatting' in sheet_data:
                for cell_ref, formatting in sheet_data['cell_formatting'].items():
                    row, col = self.parse_cell_ref(cell_ref)
                    if row < self.table.rowCount() and col < self.table.columnCount():
                        item = self.table.item(row, col)
                        if item:
                            font = item.font()
                            if formatting.get('bold'):
                                font.setBold(True)
                            if formatting.get('italic'):
                                font.setItalic(True)
                            if formatting.get('underline'):
                                font.setUnderline(True)
                            item.setFont(font)

            # Load column widths if available
            if isinstance(sheet_data, dict) and 'column_widths' in sheet_data:
                for col_idx, width in sheet_data['column_widths'].items():
                    self.table.setColumnWidth(int(col_idx), width)

            # Load row heights if available
            if isinstance(sheet_data, dict) and 'row_heights' in sheet_data:
                for row_idx, height in sheet_data['row_heights'].items():
                    self.table.setRowHeight(int(row_idx), height)

        except json.JSONDecodeError:
            pass

        self.table.blockSignals(False)
        self.recalculate()

    def parse_cell_ref(self, cell_ref: str):
        """Parse cell reference (e.g., A1) to row, col."""
        match = re.match(r'([A-Z]+)(\d+)', cell_ref)
        if match:
            col_str, row_str = match.groups()
            col = sum((ord(c) - 65) * (26 ** i) for i, c in enumerate(reversed(col_str)))
            row = int(row_str) - 1
            return row, col
        return 0, 0

    def get_sheet_data(self) -> str:
        """Get current sheet data as JSON."""
        cells = {}
        cell_formatting = {}
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and (item.text() or item.data(Qt.ItemDataRole.UserRole)):
                    cell_ref = self.cell_ref(row, col)
                    # Save formula if present, otherwise save displayed value
                    formula = item.data(Qt.ItemDataRole.UserRole)
                    if formula and formula.startswith('='):
                        cells[cell_ref] = formula
                    elif item.text():
                        cells[cell_ref] = item.text()

                    # Save formatting if non-default
                    font = item.font()
                    formatting = {}
                    if font.bold():
                        formatting['bold'] = True
                    if font.italic():
                        formatting['italic'] = True
                    if font.underline():
                        formatting['underline'] = True

                    if formatting:
                        cell_formatting[cell_ref] = formatting

        # Save column widths (only non-default widths to save space)
        column_widths = {}
        for col in range(self.table.columnCount()):
            width = self.table.columnWidth(col)
            # Save if different from default (typically 100 pixels)
            if width != self.table.horizontalHeader().defaultSectionSize():
                column_widths[str(col)] = width

        # Save row heights (only non-default heights to save space)
        row_heights = {}
        for row in range(self.table.rowCount()):
            height = self.table.rowHeight(row)
            # Save if different from default (typically 30 pixels)
            if height != self.table.verticalHeader().defaultSectionSize():
                row_heights[str(row)] = height

        # Create complete data structure
        sheet_data = {
            'cells': cells,
            'column_widths': column_widths,
            'row_heights': row_heights,
            'cell_formatting': cell_formatting
        }

        return json.dumps(sheet_data)

    def on_cell_selected(self, row, col, prev_row, prev_col):
        """Handle cell selection."""
        item = self.table.item(row, col)
        if item:
            # Show formula if stored, otherwise show cell text
            formula = item.data(Qt.ItemDataRole.UserRole)
            if formula and formula.startswith('='):
                self.formula_bar.setText(formula)
            else:
                self.formula_bar.setText(item.text())
        else:
            self.formula_bar.clear()

        # Update formatting buttons to reflect current cell's formatting
        self.update_format_buttons()

    def on_header_resized(self, index, old_size, new_size):
        """Handle column/row header resize."""
        if old_size != new_size:
            self.is_modified = True

    def on_cell_changed(self, item):
        """Handle cell content change."""
        self.is_modified = True
        # Store for undo
        self.undo_stack.append(self.get_sheet_data())
        self.redo_stack.clear()

        # Handle formula storage
        if item:
            text = item.text()
            if text and text.startswith('='):
                # Store the formula in UserRole if not already stored
                stored_formula = item.data(Qt.ItemDataRole.UserRole)
                if stored_formula != text:
                    item.setData(Qt.ItemDataRole.UserRole, text)
            elif not text:
                # Cell was cleared
                item.setData(Qt.ItemDataRole.UserRole, None)
            # If text doesn't start with '=' and there's a stored formula, keep the formula
            # (this happens after recalculate replaces formula with result)

        # Recalculate formulas when cell content changes
        self.recalculate()

    def on_formula_enter(self):
        """Handle formula bar input."""
        current = self.table.currentItem()
        if current:
            text = self.formula_bar.text()
            # If it's a formula, store it in UserRole
            if text.startswith('='):
                current.setData(Qt.ItemDataRole.UserRole, text)
                current.setText(text)  # Temporarily show formula, will be replaced by result
            else:
                # Not a formula - clear UserRole and just set text
                current.setData(Qt.ItemDataRole.UserRole, None)
                current.setText(text)
            self.recalculate()

    def recalculate(self):
        """Recalculate all formulas."""
        self.table.blockSignals(True)

        # Get all cell values (use stored formulas where available)
        cells = {}
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    # Check if there's a stored formula in the data
                    formula = item.data(Qt.ItemDataRole.UserRole)
                    if formula and formula.startswith('='):
                        cells[self.cell_ref(row, col)] = formula
                    else:
                        cells[self.cell_ref(row, col)] = item.text()

        # Evaluate formulas
        engine = FormulaEngine(cells)
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    # Check for formula in UserRole data or in cell text
                    formula = item.data(Qt.ItemDataRole.UserRole)
                    if formula is None and item.text().startswith('='):
                        # First time seeing this formula - store it
                        formula = item.text()
                        item.setData(Qt.ItemDataRole.UserRole, formula)

                    if formula and formula.startswith('='):
                        result = engine.evaluate(formula)
                        item.setText(str(result))
                        item.setToolTip(f"Formula: {formula}")

        self.table.blockSignals(False)

    def add_sheet(self):
        """Add a new spreadsheet."""
        name, ok = QInputDialog.getText(self, "New Sheet", "Enter sheet name:")
        if ok and name:
            sheet_id = self.database.add_spreadsheet(name)
            self.load_sheets()
            self.sheet_modified.emit()

    def rename_sheet(self):
        """Rename the selected sheet."""
        current_item = self.sheet_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a sheet to rename.")
            return

        sheet_id = current_item.data(Qt.ItemDataRole.UserRole)
        old_name = current_item.text()

        new_name, ok = QInputDialog.getText(
            self, "Rename Sheet",
            "Enter new sheet name:",
            text=old_name
        )

        if ok and new_name and new_name != old_name:
            # Get the sheet from database
            sheet = self.database.get_spreadsheet(sheet_id)
            if sheet:
                # Update the sheet with new name
                self.database.update_spreadsheet(sheet_id, new_name, sheet['data'])

                # Update current_sheet_name if this is the current sheet
                if self.current_sheet_id == sheet_id:
                    self.current_sheet_name = new_name

                # Reload the sheet list
                self.load_sheets()

                # Reselect the renamed sheet
                for i in range(self.sheet_list.count()):
                    item = self.sheet_list.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == sheet_id:
                        self.sheet_list.setCurrentItem(item)
                        break

                self.sheet_modified.emit()

    def delete_sheet(self):
        """Delete the selected sheet."""
        current_item = self.sheet_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a sheet to delete.")
            return

        reply = QMessageBox.question(
            self, "Delete Sheet",
            "Are you sure you want to delete this sheet?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            sheet_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.database.delete_spreadsheet(sheet_id)
            self.load_sheets()
            self.table.clearContents()
            self.sheet_modified.emit()

    def save_current_sheet(self):
        """Save the current sheet."""
        if self.current_sheet_id and self.is_modified:
            # Use the stored name instead of the currently selected item
            data = self.get_sheet_data()
            self.database.update_spreadsheet(self.current_sheet_id, self.current_sheet_name, data)
            self.is_modified = False
            self.sheet_modified.emit()

    def autosave(self):
        """Autosave the current sheet if modified."""
        if self.is_modified and self.current_sheet_id:
            self.save_current_sheet()

    def undo(self):
        """Undo last change."""
        if self.undo_stack:
            current_state = self.get_sheet_data()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack.pop()
            self.load_sheet_data(previous_state)

    def redo(self):
        """Redo last undone change."""
        if self.redo_stack:
            current_state = self.get_sheet_data()
            self.undo_stack.append(current_state)
            next_state = self.redo_stack.pop()
            self.load_sheet_data(next_state)

    def toggle_bold(self):
        """Toggle bold formatting for selected cell(s)."""
        self.apply_formatting('bold', self.btn_bold.isChecked())

    def toggle_italic(self):
        """Toggle italic formatting for selected cell(s)."""
        self.apply_formatting('italic', self.btn_italic.isChecked())

    def toggle_underline(self):
        """Toggle underline formatting for selected cell(s)."""
        self.apply_formatting('underline', self.btn_underline.isChecked())

    def apply_formatting(self, format_type: str, enabled: bool):
        """Apply formatting to selected cells."""
        selected_ranges = self.table.selectedRanges()

        if not selected_ranges:
            # If no selection, format current cell
            current = self.table.currentItem()
            if current:
                self._apply_cell_formatting(current, format_type, enabled)
            return

        # Apply to all selected cells
        for selected_range in selected_ranges:
            for row in range(selected_range.topRow(), selected_range.bottomRow() + 1):
                for col in range(selected_range.leftColumn(), selected_range.rightColumn() + 1):
                    item = self.table.item(row, col)
                    if not item:
                        item = QTableWidgetItem()
                        self.table.setItem(row, col, item)
                    self._apply_cell_formatting(item, format_type, enabled)

        self.is_modified = True
        self.sheet_modified.emit()

    def _apply_cell_formatting(self, item: QTableWidgetItem, format_type: str, enabled: bool):
        """Apply specific formatting to a cell item."""
        font = item.font()

        if format_type == 'bold':
            font.setBold(enabled)
        elif format_type == 'italic':
            font.setItalic(enabled)
        elif format_type == 'underline':
            font.setUnderline(enabled)

        item.setFont(font)

    def update_format_buttons(self):
        """Update format button states based on current cell formatting."""
        current = self.table.currentItem()

        if current:
            font = current.font()
            self.btn_bold.setChecked(font.bold())
            self.btn_italic.setChecked(font.italic())
            self.btn_underline.setChecked(font.underline())
        else:
            # No cell selected, reset buttons
            self.btn_bold.setChecked(False)
            self.btn_italic.setChecked(False)
            self.btn_underline.setChecked(False)

    def show_context_menu(self, position):
        """Show context menu for the sheet list."""
        menu = QMenu()

        # Add Sheet action (always available)
        add_action = QAction("New Sheet", self)
        add_action.triggered.connect(self.add_sheet)
        menu.addAction(add_action)

        # Actions that require a selection
        current_item = self.sheet_list.currentItem()
        if current_item:
            menu.addSeparator()

            rename_action = QAction("Rename Sheet", self)
            rename_action.triggered.connect(self.rename_sheet)
            menu.addAction(rename_action)

            save_action = QAction("Save Sheet", self)
            save_action.triggered.connect(self.save_current_sheet)
            menu.addAction(save_action)

            menu.addSeparator()

            delete_action = QAction("Delete Sheet", self)
            delete_action.triggered.connect(self.delete_sheet)
            menu.addAction(delete_action)

        menu.exec(self.sheet_list.viewport().mapToGlobal(position))
