# SPARK Personal - Installation Guide

Complete installation instructions for all platforms.

## System Requirements

### Minimum Requirements
- **OS**: Linux, Windows 10+, macOS 10.14+
- **Python**: 3.8 or higher
- **RAM**: 512 MB
- **Storage**: 50 MB (plus space for your data)
- **Display**: 1024x768 or higher

### Recommended
- **Python**: 3.11 or higher
- **RAM**: 1 GB or more
- **Storage**: 100 MB or more
- **Display**: 1920x1080 or higher

## Installation Methods

### Method 1: Automatic Install (Recommended) ⭐

**The easiest way!** Just run the launcher script - it handles everything automatically:

**Linux/macOS:**
```bash
cd /path/to/spark
chmod +x run.sh  # Make executable (only needed once)
./run.sh
```

**Windows:**
```batch
cd C:\path\to\spark
run.bat
```

**What the launcher does automatically:**
1. Creates a Python virtual environment (`venv/`)
2. Installs all dependencies inside the virtual environment
3. Launches SPARK Personal

**No manual pip install needed!** Everything is isolated from your system Python.

On subsequent runs, the script just activates the existing virtual environment and starts the app.

---

### Method 2: Manual Virtual Environment Install

If you prefer manual control:

```bash
# 1. Navigate to project
cd /path/to/spark

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python -m spark.main

# When done, deactivate
deactivate
```

---

### Method 3: System-Wide Install (Not Recommended)

Only use this if you need SPARK installed globally:

```bash
# Install for all users (requires sudo/admin)
pip install .

# Or install for current user only
pip install --user .

# Run from anywhere
spark
```

**Note:** System-wide installation can cause dependency conflicts. We recommend using the virtual environment approach (Method 1 or 2).

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip

# Install PyQt6 dependencies
sudo apt install python3-pyqt6

# Navigate to project directory
cd /home/user/code/spark

# Install SPARK Personal
pip install -r requirements.txt

# Run the application
python3 -m spark.main
```

### Linux (Fedora/RHEL)

```bash
# Install Python and pip
sudo dnf install python3 python3-pip

# Install dependencies
pip3 install -r requirements.txt

# Run the application
python3 -m spark.main
```

### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Navigate to project directory
cd /path/to/spark

# Install dependencies
pip3 install -r requirements.txt

# Run the application
python3 -m spark.main
```

### Windows

#### Option A: Using Command Prompt

```batch
REM Ensure Python is installed (download from python.org)
python --version

REM Navigate to project directory
cd C:\path\to\spark

REM Install dependencies
pip install -r requirements.txt

REM Run the application
python -m spark.main

REM Or use the batch file
run.bat
```

#### Option B: Using PowerShell

```powershell
# Check Python installation
python --version

# Navigate to project directory
Set-Location C:\path\to\spark

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m spark.main
```

## Virtual Environment Setup (Recommended)

Using a virtual environment keeps SPARK Personal's dependencies isolated:

### Linux/macOS

```bash
# Create virtual environment
python3 -m venv spark-env

# Activate it
source spark-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run SPARK Personal
python -m spark.main

# When done, deactivate
deactivate
```

### Windows

```batch
REM Create virtual environment
python -m venv spark-env

REM Activate it
spark-env\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Run SPARK Personal
python -m spark.main

REM When done, deactivate
deactivate
```

## Verification

After installation, verify everything works:

```bash
# Run verification script
python verify_install.py

# Expected output:
# ✅ Python 3.x.x
# ✅ PyQt6: x.x.x
# ✅ PyYAML: x.x.x
# ✅ Pygments: x.x.x
# ✅ Markdown: x.x.x
# ... (all files present)
# ✅ All checks passed!
```

## Troubleshooting

### Issue: "No module named 'PyQt6'"

**Solution:**
```bash
pip install PyQt6
```

### Issue: "Python version too old"

**Solution:**
- Install Python 3.8 or higher
- On Linux: `sudo apt install python3.10`
- On macOS: `brew install python@3.10`
- On Windows: Download from python.org

### Issue: "Permission denied"

**Solution:**
```bash
# On Linux/macOS, use --user flag
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

### Issue: "PyQt6 installation fails"

**Solution (Linux):**
```bash
# Install system dependencies first
sudo apt install python3-dev python3-pyqt6
# Then try pip again
pip install PyQt6
```

### Issue: "Application won't start"

**Solution:**
1. Check Python version: `python --version`
2. Verify dependencies: `python verify_install.py`
3. Check for errors: `python -m spark.main 2>&1 | tee error.log`
4. Review error.log for specific issues

### Issue: "Database locked" or "Permission denied"

**Solution:**
```bash
# Check permissions on data directory
ls -la ~/.spark_personal/

# Fix permissions if needed (Linux/macOS)
chmod 755 ~/.spark_personal/
chmod 644 ~/.spark_personal/*
```

## Uninstallation

### Remove SPARK Personal

```bash
# If installed with pip
pip uninstall spark-personal

# Remove data directory (CAUTION: This deletes all your notes!)
rm -rf ~/.spark_personal/  # Linux/macOS
# Or on Windows: rmdir /s %USERPROFILE%\.spark_personal
```

### Keep Data, Remove Application Only

```bash
# Just uninstall the package
pip uninstall spark-personal

# Your data remains in ~/.spark_personal/
```

## Upgrading

### From pip install

```bash
# Pull latest changes
git pull

# Reinstall
pip install --upgrade .
```

### From source

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Run
python -m spark.main
```

## Data Backup Before Upgrade

Always backup your data before upgrading:

```bash
# Backup data directory
cp -r ~/.spark_personal ~/.spark_personal.backup

# Or use SPARK's built-in backup
# File → Backup Manager → Create Backup
```

## Post-Installation

### First Run Setup

1. Launch SPARK Personal
2. Demo data will be created automatically
3. Explore the demo notes, spreadsheets, and snippets
4. Configure settings: File → Settings
5. Set up backups: File → Backup Manager

### Recommended Configuration

```yaml
# ~/.spark_personal/config.yaml

theme: Dark  # or Light, Solarized Light/Dark, Gruvbox
font_family: Consolas  # or Monaco, Courier New, etc.
font_size: 10
backup_enabled: true
backup_interval_hours: 24
autosave_enabled: true
autosave_interval_seconds: 300
```

## Getting Help

- **Quick Start**: Read [QUICKSTART.md](QUICKSTART.md)
- **User Guide**: Read [README.md](README.md)
- **Issues**: Check GitHub Issues
- **Community**: Join Discussions

## Next Steps

After installation:

1. ✅ Read [QUICKSTART.md](QUICKSTART.md) for a 5-minute tour
2. ✅ Explore the demo data
3. ✅ Create your first note
4. ✅ Configure your preferred theme
5. ✅ Set up automatic backups
6. ✅ Start organizing your knowledge!

---

**Installation complete!** Enjoy using SPARK Personal! ⚡
