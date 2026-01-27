"""Spreadsheets screen for SPARK Mobile."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
import json
import re
import math
from datetime import datetime


class SpreadsheetsScreen(BoxLayout):
    """Spreadsheets list and grid viewer screen with formula support."""

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = 'vertical'

        # Top bar
        top_bar = BoxLayout(size_hint_y=0.1, padding=dp(10), spacing=dp(10))

        title = Label(text='Spreadsheets (View Only)', font_size='20sp')
        top_bar.add_widget(title)

        self.add_widget(top_bar)

        # Sheets list
        scroll = ScrollView(size_hint_y=0.9)
        self.sheets_list = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.sheets_list.bind(minimum_height=self.sheets_list.setter('height'))
        scroll.add_widget(self.sheets_list)
        self.add_widget(scroll)

        self.refresh_sheets()

    def refresh_sheets(self):
        """Refresh the spreadsheets list."""
        self.sheets_list.clear_widgets()

        sheets = self.db.get_all_spreadsheets()

        if not sheets:
            label = Label(
                text='No spreadsheets yet.\nTap "+ New Sheet" to create one.',
                size_hint_y=None,
                height=dp(100),
                color=(0.5, 0.5, 0.5, 1)
            )
            self.sheets_list.add_widget(label)
            return

        for sheet in sheets:
            # Parse data to show preview
            try:
                data = json.loads(sheet['data']) if sheet['data'] else {}
                cell_count = len(data)
                preview = f"{cell_count} cells"
            except:
                preview = "No data"

            sheet_btn = Button(
                text=f"{sheet['name']}\n{preview}",
                size_hint_y=None,
                height=dp(80),
                halign='left',
                valign='top',
                text_size=(None, None),
                background_normal='',
                background_color=(0.15, 0.15, 0.15, 1)
            )
            sheet_btn.bind(size=lambda btn, size: setattr(btn, 'text_size', (size[0] - dp(20), None)))
            sheet_btn.bind(on_press=lambda btn, sheet_id=sheet['id']: self.show_sheet_viewer(sheet_id))
            self.sheets_list.add_widget(sheet_btn)

    def show_add_sheet_dialog(self, instance):
        """Show dialog to add a new spreadsheet."""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        name_input = TextInput(
            hint_text='Spreadsheet name',
            multiline=False,
            size_hint_y=0.2
        )
        content.add_widget(name_input)

        info_label = Label(
            text='A basic 5x5 spreadsheet will be created.',
            size_hint_y=0.6,
            color=(0.7, 0.7, 0.7, 1)
        )
        content.add_widget(info_label)

        btn_layout = BoxLayout(size_hint_y=0.2, spacing=dp(10))

        save_btn = Button(text='Create', background_color=(0.2, 0.6, 0.8, 1))
        cancel_btn = Button(text='Cancel')

        popup = Popup(
            title='New Spreadsheet',
            content=content,
            size_hint=(0.9, 0.5)
        )

        def save_sheet(btn):
            if name_input.text.strip():
                # Create with empty 5x5 grid
                initial_data = json.dumps({})
                self.db.add_spreadsheet(name_input.text.strip(), initial_data)
                self.refresh_sheets()
                popup.dismiss()

        save_btn.bind(on_press=save_sheet)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup.open()

    def parse_cell_reference(self, ref):
        """Parse cell reference like 'A1' into (0, 0) coordinates."""
        match = re.match(r'([A-Z]+)(\d+)', ref.upper())
        if match:
            col_letters, row_num = match.groups()
            # Convert column letters to number (A=0, B=1, ..., Z=25, AA=26, etc.)
            col = 0
            for char in col_letters:
                col = col * 26 + (ord(char) - ord('A') + 1)
            col -= 1  # Make zero-indexed
            row = int(row_num) - 1  # Make zero-indexed
            return (row, col)
        return None

    def evaluate_formula(self, formula, data):
        """Evaluate a formula with full function support."""
        if not formula.startswith('='):
            return formula

        # Remove the = sign
        expr = formula[1:].strip()

        try:
            # Process functions first
            expr = self.process_functions(expr, data)

            # Replace cell references with their values
            expr = self.replace_cell_references(expr, data)

            # Normalize = to == for comparisons (for IF function)
            expr = self.normalize_equality(expr)

            # Evaluate the expression
            # For security, extract string literals first and validate the code structure
            string_literals = []
            def extract_strings(match):
                string_literals.append(match.group(0))
                return f'__STR_{len(string_literals)-1}__'

            # Extract quoted strings (both single and double quotes)
            expr_no_strings = re.sub(r'"[^"]*"|\'[^\']*\'', extract_strings, expr)

            # Validate the non-string parts
            # Allow math function names (abs, floor, ceil, sqrt, pow, round, trunc) and math. prefix
            allowed_chars = set('0123456789+-*/%.()<>=!&, mathceilflorabsqrtpowdun_ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            if all(c in allowed_chars or c.isspace() for c in expr_no_strings.replace('==', '').replace('!=', '').replace('<=', '').replace('>=', '')):
                # Expression structure is safe, now evaluate the original expression with strings
                # Provide math module and safe built-in functions to eval
                safe_globals = {
                    "__builtins__": {},
                    "math": math,
                    "abs": abs,
                    "round": round,
                    "pow": pow,
                    "min": min,
                    "max": max,
                    "True": True,
                    "False": False
                }
                result = eval(expr, safe_globals, {})
                if isinstance(result, bool):
                    return str(result)
                elif isinstance(result, (int, float)):
                    return str(round(result, 2))
                else:
                    return str(result)
            else:
                return '#ERROR'
        except Exception as e:
            return '#ERROR'

    def normalize_equality(self, expr):
        """Convert single = to == for equality comparisons."""
        # Replace = with == only when it's not already ==, !=, <=, or >=
        result = []
        i = 0
        while i < len(expr):
            if expr[i] == '=':
                # Check if already part of ==, !=, <=, >=
                if i > 0 and expr[i-1] in '!<>':
                    result.append('=')
                elif i + 1 < len(expr) and expr[i+1] == '=':
                    result.append('==')
                    i += 1
                else:
                    # Convert single = to ==
                    result.append('==')
            else:
                result.append(expr[i])
            i += 1
        return ''.join(result)

    def replace_cell_references(self, expr, data):
        """Replace cell references with their values."""
        cell_pattern = r'([A-Z]+\d+)'

        def replace_cell(match):
            cell_ref = match.group(1)
            value = data.get(cell_ref, '0')

            # If the referenced cell has a formula, evaluate it recursively
            if isinstance(value, str) and value.startswith('='):
                value = self.evaluate_formula(value, data)

            # Try to parse date string to numeric timestamp
            if isinstance(value, str) and re.match(r'\d{4}-\d{2}-\d{2}', value):
                try:
                    dt = datetime.strptime(value, '%Y-%m-%d')
                    # Convert to days since epoch
                    return str(dt.timestamp() / 86400)
                except:
                    pass

            # Return numeric value or 0
            try:
                return str(float(value)) if value else '0'
            except:
                return '0'

        return re.sub(cell_pattern, replace_cell, expr)

    def process_functions(self, expr, data):
        """Process spreadsheet functions."""
        # Constants - PI and E
        expr = re.sub(r'\bPI\(\)', str(math.pi), expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bPI\b', str(math.pi), expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bE\(\)', str(math.e), expr, flags=re.IGNORECASE)
        expr = re.sub(r'\bE\b', str(math.e), expr, flags=re.IGNORECASE)

        # TODAY() - returns numeric timestamp (days since epoch)
        today_timestamp = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() / 86400
        expr = re.sub(r'TODAY\(\)', str(today_timestamp), expr, flags=re.IGNORECASE)

        # NOW() - returns numeric timestamp with time
        now_timestamp = datetime.now().timestamp() / 86400
        expr = re.sub(r'NOW\(\)', str(now_timestamp), expr, flags=re.IGNORECASE)

        # SUM function
        expr = re.sub(
            r'SUM\(([^)]+)\)',
            lambda m: str(self.func_sum(m.group(1), data)),
            expr,
            flags=re.IGNORECASE
        )

        # AVERAGE function
        expr = re.sub(
            r'AVERAGE\(([^)]+)\)',
            lambda m: str(self.func_average(m.group(1), data)),
            expr,
            flags=re.IGNORECASE
        )

        # MIN function
        expr = re.sub(
            r'MIN\(([^)]+)\)',
            lambda m: str(self.func_min(m.group(1), data)),
            expr,
            flags=re.IGNORECASE
        )

        # MAX function
        expr = re.sub(
            r'MAX\(([^)]+)\)',
            lambda m: str(self.func_max(m.group(1), data)),
            expr,
            flags=re.IGNORECASE
        )

        # COUNT function
        expr = re.sub(
            r'COUNT\(([^)]+)\)',
            lambda m: str(self.func_count(m.group(1), data)),
            expr,
            flags=re.IGNORECASE
        )

        # MEDIAN function
        expr = re.sub(
            r'MEDIAN\(([^)]+)\)',
            lambda m: str(self.func_median(m.group(1), data)),
            expr,
            flags=re.IGNORECASE
        )

        # Simple math functions that can be converted to Python equivalents
        # ABS function
        expr = re.sub(r'ABS\(([^)]+)\)', r'abs(\1)', expr, flags=re.IGNORECASE)

        # FLOOR function
        expr = re.sub(r'FLOOR\(([^)]+)\)', lambda m: f'math.floor({m.group(1)})', expr, flags=re.IGNORECASE)

        # CEILING/CEIL function - process CEILING first, then CEIL but not if already has math. prefix
        expr = re.sub(r'\bCEILING\(([^)]+)\)', lambda m: f'math.ceil({m.group(1)})', expr, flags=re.IGNORECASE)
        # Only match CEIL if not preceded by "math." (negative lookbehind)
        expr = re.sub(r'(?<!math\.)\bCEIL\(([^)]+)\)', lambda m: f'math.ceil({m.group(1)})', expr, flags=re.IGNORECASE)

        # ROUND function - handle both single and two-argument forms
        expr = re.sub(r'ROUND\(([^)]+),([^)]+)\)', r'round(\1,\2)', expr, flags=re.IGNORECASE)
        expr = re.sub(r'ROUND\(([^)]+)\)', r'round(\1)', expr, flags=re.IGNORECASE)

        # SQRT function
        expr = re.sub(r'SQRT\(([^)]+)\)', lambda m: f'math.sqrt({m.group(1)})', expr, flags=re.IGNORECASE)

        # TRUNC function
        expr = re.sub(r'TRUNC\(([^)]+)\)', lambda m: f'math.trunc({m.group(1)})', expr, flags=re.IGNORECASE)

        # POWER/POW function - handle two arguments separated by comma
        expr = re.sub(r'POWER\(([^,]+),([^)]+)\)', r'pow(\1,\2)', expr, flags=re.IGNORECASE)
        expr = re.sub(r'POW\(([^,]+),([^)]+)\)', r'pow(\1,\2)', expr, flags=re.IGNORECASE)

        # MOD function (convert to % operator)
        expr = re.sub(r'MOD\(([^,]+),([^)]+)\)', r'(\1 % \2)', expr, flags=re.IGNORECASE)

        # Boolean functions - AND, OR, NOT
        expr = self.process_and_function(expr, data)
        expr = self.process_or_function(expr, data)
        expr = self.process_not_function(expr, data)

        # IF function - more complex, needs careful parsing
        expr = self.process_if_function(expr, data)

        # DATE function - converts numeric timestamp to date string
        expr = re.sub(
            r'DATE\(([^)]+)\)',
            lambda m: self.func_date(m.group(1), data),
            expr,
            flags=re.IGNORECASE
        )

        # TIME function - converts numeric timestamp to time string (HH:MM:SS)
        expr = re.sub(
            r'TIME\(([^)]+)\)',
            lambda m: self.func_time(m.group(1), data),
            expr,
            flags=re.IGNORECASE
        )

        return expr

    def func_sum(self, args, data):
        """SUM function implementation."""
        values = self.parse_function_args(args, data)
        return sum(values)

    def func_average(self, args, data):
        """AVERAGE function implementation."""
        values = self.parse_function_args(args, data)
        return sum(values) / len(values) if values else 0

    def func_min(self, args, data):
        """MIN function implementation."""
        values = self.parse_function_args(args, data)
        return min(values) if values else 0

    def func_max(self, args, data):
        """MAX function implementation."""
        values = self.parse_function_args(args, data)
        return max(values) if values else 0

    def func_count(self, args, data):
        """COUNT function implementation."""
        values = self.parse_function_args(args, data)
        return len(values)

    def func_median(self, args, data):
        """MEDIAN function implementation."""
        values = self.parse_function_args(args, data)
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

    def func_date(self, args, data):
        """DATE function - converts numeric timestamp to date string."""
        args = args.strip()
        # Replace cell references
        args = self.replace_cell_references(args, data)

        try:
            timestamp = float(eval(args))
            dt = datetime.fromtimestamp(timestamp * 86400)
            return f'"{dt.strftime("%Y-%m-%d")}"'
        except:
            return '"#ERROR"'

    def func_time(self, args, data):
        """TIME function - converts numeric timestamp to time string (HH:MM:SS format)."""
        args = args.strip()
        # Replace cell references
        args = self.replace_cell_references(args, data)

        try:
            timestamp = float(eval(args))
            time_obj = datetime.fromtimestamp(timestamp * 86400)
            return f'"{time_obj.strftime("%H:%M:%S")}"'
        except:
            return '"#ERROR"'

    def process_if_function(self, expr, data):
        """Process IF function with proper nested function support."""
        pattern = r'IF\(([^,]+),([^,]+),([^)]+)\)'

        def replace_if(match):
            condition = match.group(1).strip()
            true_val = match.group(2).strip()
            false_val = match.group(3).strip()

            # Replace cell references in condition
            condition = self.replace_cell_references(condition, data)
            condition = self.normalize_equality(condition)

            try:
                if eval(condition):
                    return true_val
                else:
                    return false_val
            except:
                return '"#ERROR"'

        return re.sub(pattern, replace_if, expr, flags=re.IGNORECASE)

    def process_and_function(self, expr, data):
        """Process AND function - returns True if all conditions are true."""
        # Simple pattern for AND with 2 arguments (can be extended)
        pattern = r'\bAND\(([^,]+),([^)]+)\)'

        def replace_and(match):
            conditions = [match.group(1).strip(), match.group(2).strip()]
            try:
                for condition in conditions:
                    condition = self.replace_cell_references(condition, data)
                    condition = self.normalize_equality(condition)
                    if not eval(condition):
                        return 'False'
                return 'True'
            except:
                return 'False'

        return re.sub(pattern, replace_and, expr, flags=re.IGNORECASE)

    def process_or_function(self, expr, data):
        """Process OR function - returns True if any condition is true."""
        # Simple pattern for OR with 2 arguments (can be extended)
        pattern = r'\bOR\(([^,]+),([^)]+)\)'

        def replace_or(match):
            conditions = [match.group(1).strip(), match.group(2).strip()]
            try:
                for condition in conditions:
                    condition = self.replace_cell_references(condition, data)
                    condition = self.normalize_equality(condition)
                    if eval(condition):
                        return 'True'
                return 'False'
            except:
                return 'False'

        return re.sub(pattern, replace_or, expr, flags=re.IGNORECASE)

    def process_not_function(self, expr, data):
        """Process NOT function - returns the opposite boolean value."""
        pattern = r'\bNOT\(([^)]+)\)'

        def replace_not(match):
            condition = match.group(1).strip()
            try:
                condition = self.replace_cell_references(condition, data)
                condition = self.normalize_equality(condition)
                result = eval(condition)
                return 'False' if result else 'True'
            except:
                return 'True'

        return re.sub(pattern, replace_not, expr, flags=re.IGNORECASE)

    def parse_function_args(self, args, data):
        """Parse function arguments and return numeric values."""
        values = []
        parts = args.split(',')

        for part in parts:
            part = part.strip()

            # Check if it's a range like A1:A5
            if ':' in part:
                values.extend(self.parse_range(part, data))
            else:
                # Replace cell reference or evaluate expression
                part = self.replace_cell_references(part, data)
                try:
                    values.append(float(eval(part)))
                except:
                    pass

        return values

    def parse_range(self, range_str, data):
        """Parse cell range like A1:A5 and return values."""
        try:
            start, end = range_str.split(':')
            start_coords = self.parse_cell_reference(start.strip())
            end_coords = self.parse_cell_reference(end.strip())

            if not start_coords or not end_coords:
                return []

            values = []
            start_row, start_col = start_coords
            end_row, end_col = end_coords

            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    cell_ref = f"{self.col_to_letter(col)}{row + 1}"
                    value = data.get(cell_ref, '0')
                    if isinstance(value, str) and value.startswith('='):
                        value = self.evaluate_formula(value, data)
                    try:
                        values.append(float(value))
                    except:
                        pass

            return values
        except:
            return []

    def show_sheet_viewer(self, sheet_id):
        """Show grid viewer for a spreadsheet with formula support."""
        sheet = self.db.get_spreadsheet(sheet_id)
        if not sheet:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(5), padding=dp(5))

        # Parse data
        try:
            raw_data = json.loads(sheet['data']) if sheet['data'] else {}

            # Handle both old format (flat dict) and new format (with 'cells' key)
            if isinstance(raw_data, dict):
                if 'cells' in raw_data:
                    # New desktop format: {"cells": {...}, "column_widths": {...}, ...}
                    data = raw_data['cells']
                    print(f"SPARK: Loaded spreadsheet (desktop format) with {len(data)} cells")
                else:
                    # Old mobile format: {"A1": "value", ...}
                    data = raw_data
                    print(f"SPARK: Loaded spreadsheet (mobile format) with {len(data)} cells")
            else:
                data = {}
                print(f"SPARK: WARNING - unexpected data format: {type(raw_data)}")

            print(f"SPARK: Data keys: {list(data.keys())[:10]}")
            if len(data) > 0:
                # Print first few cells for debugging
                for i, (k, v) in enumerate(list(data.items())[:5]):
                    print(f"SPARK: Cell {k} = {v}")
        except Exception as e:
            print(f"SPARK: ERROR parsing spreadsheet data: {e}")
            print(f"SPARK: Raw data from DB: {sheet['data'][:200] if sheet['data'] else 'None'}")
            data = {}

        # Determine grid size from existing data
        max_row, max_col = 4, 4  # Default 5x5 (0-indexed)
        for cell_ref in data.keys():
            coords = self.parse_cell_reference(cell_ref)
            if coords:
                row, col = coords
                max_row = max(max_row, row)
                max_col = max(max_col, col)

        # Add a bit of extra space
        max_row = min(max_row + 2, 20)  # Limit to 20 rows
        max_col = min(max_col + 2, 10)  # Limit to 10 columns

        # Create scrollable grid
        scroll = ScrollView(size_hint_y=0.75, do_scroll_x=True, do_scroll_y=True)

        grid = GridLayout(
            cols=max_col + 2,  # +1 for row headers, +1 for extra column
            spacing=dp(1),
            size_hint=(None, None),
            padding=dp(2)
        )

        # Calculate grid size
        cell_width = dp(80)
        cell_height = dp(40)
        grid.width = (max_col + 2) * cell_width
        grid.height = (max_row + 2) * cell_height

        # Header row (column labels)
        grid.add_widget(Label(text='', size_hint=(None, None), size=(cell_width, cell_height)))
        for col in range(max_col + 1):
            col_label = self.col_to_letter(col)
            header = Label(
                text=col_label,
                size_hint=(None, None),
                size=(cell_width, cell_height),
                bold=True,
                color=(0.7, 0.9, 1, 1)
            )
            grid.add_widget(header)

        # Data rows
        for row in range(max_row + 1):
            # Row header
            row_header = Label(
                text=str(row + 1),
                size_hint=(None, None),
                size=(cell_width, cell_height),
                bold=True,
                color=(0.7, 0.9, 1, 1)
            )
            grid.add_widget(row_header)

            # Data cells
            for col in range(max_col + 1):
                cell_ref = f"{self.col_to_letter(col)}{row + 1}"
                cell_value = data.get(cell_ref, '')

                # Evaluate formula if present
                display_value = cell_value
                if isinstance(cell_value, str) and cell_value.startswith('='):
                    try:
                        display_value = self.evaluate_formula(cell_value, data)
                        print(f"SPARK: {cell_ref}={cell_value} -> {display_value}")
                    except Exception as e:
                        print(f"SPARK: Error evaluating {cell_ref}: {e}")
                        display_value = '#ERROR'

                # Ensure display_value is a string
                if display_value is None:
                    display_value = ''
                else:
                    display_value = str(display_value)

                cell_label = Label(
                    text=display_value,
                    size_hint=(None, None),
                    size=(cell_width, cell_height),
                    color=(1, 1, 1, 1) if display_value else (0.5, 0.5, 0.5, 1),
                    padding=(dp(5), dp(5))
                )
                grid.add_widget(cell_label)

        scroll.add_widget(grid)
        content.add_widget(scroll)

        # Info label
        info_label = Label(
            text='Formulas are evaluated (e.g., =A1+B1)\nView only - Edit on desktop',
            size_hint_y=0.15,
            color=(0.7, 0.7, 0.7, 1)
        )
        content.add_widget(info_label)

        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))

        delete_btn = Button(text='Delete', background_color=(0.8, 0.2, 0.2, 1))
        close_btn = Button(text='Close')

        popup = Popup(
            title=sheet['name'],
            content=content,
            size_hint=(0.95, 0.9)
        )

        def delete_sheet(btn):
            popup.dismiss()
            self.show_delete_confirmation(sheet_id, sheet['name'])

        delete_btn.bind(on_press=delete_sheet)
        close_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(delete_btn)
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)

        popup.open()

    def col_to_letter(self, col):
        """Convert column number to letter(s) (0='A', 25='Z', 26='AA', etc.)."""
        result = ''
        col += 1  # Make 1-indexed
        while col > 0:
            col -= 1
            result = chr(col % 26 + ord('A')) + result
            col //= 26
        return result

    def show_delete_confirmation(self, sheet_id, sheet_name):
        """Show confirmation dialog before deleting a spreadsheet."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        message = Label(
            text=f'Are you sure you want to delete this spreadsheet?\n\n"{sheet_name}"\n\nThis action cannot be undone.',
            size_hint_y=0.7
        )
        content.add_widget(message)

        btn_layout = BoxLayout(size_hint_y=0.3, spacing=dp(10))

        delete_btn = Button(text='Delete', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='Cancel')

        popup = Popup(
            title='Confirm Delete',
            content=content,
            size_hint=(0.8, 0.4)
        )

        def confirm_delete(btn):
            self.db.delete_spreadsheet(sheet_id)
            self.refresh_sheets()
            popup.dismiss()

        delete_btn.bind(on_press=confirm_delete)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        content.add_widget(btn_layout)

        popup.open()
