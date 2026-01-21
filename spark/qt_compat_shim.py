"""
Qt Compatibility Shim - PyQt6 to PySide6
==========================================
This module allows seamless switching between PyQt6 and PySide6.
Set environment variable USE_PYSIDE6=1 to force PySide6.

Usage: Import this BEFORE importing from PyQt6 in your modules.
"""

import sys
import os

# Determine which Qt binding to use
USE_PYSIDE6 = os.environ.get('USE_PYSIDE6', '0') == '1' or \
              os.environ.get('ANDROID_ARGUMENT') or \
              hasattr(sys, 'getandroidapilevel')

if USE_PYSIDE6:
    print("🔄 Qt Compatibility Shim: Using PySide6")

    # Install PySide6 modules as PyQt6 aliases
    import PySide6.QtCore
    import PySide6.QtGui
    import PySide6.QtWidgets

    # Create PyQt6 module aliases
    sys.modules['PyQt6'] = type(sys)('PyQt6')
    sys.modules['PyQt6.QtCore'] = PySide6.QtCore
    sys.modules['PyQt6.QtGui'] = PySide6.QtGui
    sys.modules['PyQt6.QtWidgets'] = PySide6.QtWidgets

    # PySide6 uses different signal names
    # PyQt6: pyqtSignal -> PySide6: Signal
    PySide6.QtCore.pyqtSignal = PySide6.QtCore.Signal

    # Expose through the alias
    sys.modules['PyQt6'].QtCore = PySide6.QtCore
    sys.modules['PyQt6'].QtGui = PySide6.QtGui
    sys.modules['PyQt6'].QtWidgets = PySide6.QtWidgets

else:
    print("✓ Qt Compatibility Shim: Using PyQt6 (native)")
