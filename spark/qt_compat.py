"""
Qt Compatibility Layer
Allows code to work with PySide6, PyQt6, and PyQt5 with minimal changes.
Priority: PySide6 > PyQt6 > PyQt5
"""

import sys
import os

# Detect if we're running on Android
IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ or hasattr(sys, 'getandroidapilevel')

QT_BINDING = None
QT_VERSION = None

# Try PySide6 first (best Android support), then PyQt6 (desktop), fall back to PyQt5
try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *

    QT_VERSION = 6
    QT_BINDING = "PySide6"
    print("Using PySide6")

except ImportError:
    try:
        if IS_ANDROID:
            raise ImportError("Force PyQt5 on Android")

        from PyQt6 import QtWidgets, QtCore, QtGui
        from PyQt6.QtWidgets import *
        from PyQt6.QtCore import *
        from PyQt6.QtGui import *

        QT_VERSION = 6
        QT_BINDING = "PyQt6"
        print("Using PyQt6")

    except ImportError:
        try:
            from PyQt5 import QtWidgets, QtCore, QtGui
            from PyQt5.QtWidgets import *
            from PyQt5.QtCore import *
            from PyQt5.QtGui import *

            QT_VERSION = 5
            QT_BINDING = "PyQt5"
            print("Using PyQt5")

            # PyQt5/6 compatibility shims
            # In PyQt6/PySide6, exec() was renamed from exec_()
            if not hasattr(QApplication, 'exec'):
                QApplication.exec = QApplication.exec_
            if not hasattr(QDialog, 'exec'):
                QDialog.exec = QDialog.exec_
            if not hasattr(QMenu, 'exec'):
                QMenu.exec = QMenu.exec_

        except ImportError as e:
            print(f"ERROR: Neither PySide6, PyQt6 nor PyQt5 could be imported: {e}")
            sys.exit(1)


# Enum compatibility helpers
def get_item_data_role():
    """Get the correct UserRole enum for PyQt5/6."""
    if QT_VERSION == 6:
        return Qt.ItemDataRole.UserRole
    else:
        return Qt.UserRole


def get_orientation_horizontal():
    """Get the correct Horizontal orientation enum."""
    if QT_VERSION == 6:
        return Qt.Orientation.Horizontal
    else:
        return Qt.Horizontal


def get_orientation_vertical():
    """Get the correct Vertical orientation enum."""
    if QT_VERSION == 6:
        return Qt.Orientation.Vertical
    else:
        return Qt.Vertical


def get_context_menu_policy_custom():
    """Get the correct CustomContextMenu policy enum."""
    if QT_VERSION == 6:
        return Qt.ContextMenuPolicy.CustomContextMenu
    else:
        return Qt.CustomContextMenu


def get_key(key_name):
    """Get the correct Key enum."""
    if QT_VERSION == 6:
        return getattr(Qt.Key, f"Key_{key_name}")
    else:
        return getattr(Qt, f"Key_{key_name}")


def get_keyboard_modifier(modifier_name):
    """Get the correct KeyboardModifier enum."""
    if QT_VERSION == 6:
        return getattr(Qt.KeyboardModifier, modifier_name)
    else:
        return getattr(Qt, modifier_name)


def get_standard_button(button_name):
    """Get the correct StandardButton enum."""
    if QT_VERSION == 6:
        return getattr(QMessageBox.StandardButton, button_name)
    else:
        return getattr(QMessageBox, button_name)
