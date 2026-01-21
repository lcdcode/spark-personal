#!/usr/bin/env python3
"""Verification script for SPARK Personal installation."""

import sys
import importlib


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check if all required dependencies are installed."""
    dependencies = {
        'PyQt6': 'PyQt6',
        'yaml': 'PyYAML',
        'pygments': 'Pygments',
        'markdown': 'Markdown',
    }

    all_installed = True
    for module, package in dependencies.items():
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✅ {package}: {version}")
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
            all_installed = False

    return all_installed


def check_project_structure():
    """Check if all required project files exist."""
    from pathlib import Path

    files_to_check = [
        'spark/__init__.py',
        'spark/main.py',
        'spark/config.py',
        'spark/database.py',
        'spark/main_window.py',
        'spark/notes_widget.py',
        'spark/spreadsheet_widget.py',
        'spark/snippets_widget.py',
        'spark/backup_manager.py',
        'spark/themes.py',
        'spark/demo_data.py',
        'requirements.txt',
        'setup.py',
        'README.md',
    ]

    all_exist = True
    for file in files_to_check:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}: NOT FOUND")
            all_exist = False

    return all_exist


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("SPARK Personal - Installation Verification")
    print("=" * 70)

    print("\n📋 Checking Python version...")
    python_ok = check_python_version()

    print("\n📦 Checking dependencies...")
    deps_ok = check_dependencies()

    print("\n📁 Checking project structure...")
    structure_ok = check_project_structure()

    print("\n" + "=" * 70)

    if python_ok and deps_ok and structure_ok:
        print("✅ All checks passed! SPARK Personal is ready to run.")
        print("\nTo start the application, run:")
        print("  python -m spark.main")
        print("  or")
        print("  ./run.sh (Linux/Mac) or run.bat (Windows)")
        return 0
    else:
        print("❌ Some checks failed. Please review the errors above.")
        if not deps_ok:
            print("\nTo install dependencies:")
            print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
