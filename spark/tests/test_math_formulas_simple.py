#!/usr/bin/env python3
"""Test script for new math formulas - simplified version without PyQt6."""

import json
import re
import ast
import operator
import math
from datetime import datetime
from typing import Dict, Any

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


def test_formulas():
    """Test various math formulas."""

    print("Testing SafeExpressionEvaluator with new math functions:")
    print("-" * 80)

    test_cases = [
        # Basic math functions
        ('abs(-5.7)', 5.7, 'abs function'),
        ('floor(3.14159)', 3, 'floor function'),
        ('ceil(3.14159)', 4, 'ceil function'),
        ('round(3.14159)', 3, 'round function'),
        ('round(3.14159, 2)', 3.14, 'round with decimals'),

        # Aggregation functions
        ('min(10, 20, 30)', 10, 'min function'),
        ('max(10, 20, 30)', 30, 'max function'),

        # Mathematical operations
        ('sqrt(16)', 4, 'sqrt function'),
        ('pow(2, 3)', 8, 'pow function'),
        ('10 % 3', 1, 'modulo operator'),

        # Constants
        ('pi', 3.14159, 'pi constant'),
        ('2 * pi', 6.28318, 'pi in expression'),
        ('e', 2.71828, 'e constant'),

        # Complex expressions
        ('abs(-10) + sqrt(16)', 14, 'combined functions'),
        ('floor(pi * 2)', 6, 'floor with pi'),
        ('max(abs(-5), sqrt(9))', 5, 'nested functions'),
    ]

    passed = 0
    failed = 0

    for expr, expected, description in test_cases:
        try:
            result = SafeExpressionEvaluator.evaluate(expr)

            # Handle floating point comparison
            if isinstance(expected, float):
                success = abs(float(result) - expected) < 0.001
            else:
                success = abs(float(result) - float(expected)) < 0.001

            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status} | {description:30} | {expr:25} = {result:.5f} (expected {expected})")

            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ FAIL | {description:30} | {expr:25} - Error: {e}")
            failed += 1

    print("-" * 80)
    print(f"Results: {passed} passed, {failed} failed")

    return failed == 0

if __name__ == '__main__':
    import sys
    success = test_formulas()
    sys.exit(0 if success else 1)
