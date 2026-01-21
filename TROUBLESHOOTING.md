# SPARK Personal - Troubleshooting Guide

Quick solutions for common issues.

## Quick Fixes

### "Could not load the Qt platform plugin 'xcb'" (Linux)

**Error message:**
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
qt.qpa.plugin: From 6.5.0, xcb-cursor0 or libxcb-cursor0 is needed
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0

# Fedora/RHEL
sudo dnf install -y xcb-util-cursor libxkbcommon-x11

# Then run again
./run.sh
```

**See:** [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md) for complete list.

---

### "Permission denied" when running ./run.sh

**Solution:**
```bash
chmod +x run.sh
./run.sh
```

---

### "python3: command not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3 python3-pip

# macOS
brew install python@3.11
```

---

### "Failed to create virtual environment"

**Possible causes:**
1. Python too old (need 3.8+)
2. venv module not installed
3. Insufficient permissions

**Solution:**
```bash
# Check Python version
python3 --version  # Should be 3.8 or higher

# Install venv module (Ubuntu/Debian)
sudo apt install python3-venv

# Install venv module (Fedora/RHEL)
sudo dnf install python3-virtualenv

# Clear and retry
rm -rf venv
./run.sh
```

---

### "Failed to install dependencies"

**Solution:**
```bash
# Upgrade pip and try again
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

---

### Virtual environment activated but app won't start

**Solution:**
```bash
# Make sure you're in the right directory
cd /path/to/spark

# Activate venv
source venv/bin/activate

# Try running directly
python -m spark.main

# Check for errors
python -m spark.main 2>&1 | tee error.log
cat error.log
```

---

### "ModuleNotFoundError: No module named 'PyQt6'"

**This means dependencies aren't installed in the virtual environment.**

**Solution:**
```bash
# Delete venv and recreate
rm -rf venv
./run.sh  # Will recreate and reinstall everything
```

---

### Application crashes on startup

**Check system dependencies:**
```bash
# Verify Qt works
python3 -c "from PyQt6.QtWidgets import QApplication; print('Qt OK')"

# If it fails, install system deps
# See SYSTEM_DEPENDENCIES.md for your distribution
```

---

### Database errors or corruption

**Solution:**
```bash
# Your data is in ~/.spark_personal/
ls -la ~/.spark_personal/

# Restore from backup
# File → Backup Manager → Restore Selected

# Or start fresh (CAUTION: deletes all data)
rm -rf ~/.spark_personal/
./run.sh  # Creates new database with demo data
```

---

### Backup restore fails

**Solution:**
1. Make sure SPARK is closed
2. Manually copy backup:
```bash
cp ~/.spark_personal/backups/spark_backup_YYYYMMDD_HHMMSS.db ~/.spark_personal/spark.db
```
3. Restart SPARK

---

### Theme not applying

**Solution:**
1. File → Settings → Select theme
2. Click Save
3. **Restart SPARK Personal**
4. Theme changes require app restart

---

### Autosave not working

**Check settings:**
```bash
# View config
cat ~/.spark_personal/config.yaml | grep autosave

# Should show:
# autosave_enabled: true
# autosave_interval_seconds: 300
```

**Fix:**
1. File → Settings
2. Check autosave interval
3. Save and restart

---

### Notes/Snippets not saving

**Solution:**
1. Check if file is writable:
```bash
ls -la ~/.spark_personal/spark.db
```
2. Press Ctrl+S to manually save
3. Check autosave is enabled (File → Settings)
4. Restart application

---

### Search not finding anything

**Possible causes:**
1. Search only works in current tab (Notes or Snippets)
2. Search is case-sensitive by default

**Solution:**
1. Make sure you're in the right tab (Notes or Code Snippets)
2. Try searching for a single word
3. Check spelling

---

### Spreadsheet formulas not calculating

**Solution:**
1. Click the **Recalculate** button
2. Check formula syntax: `=SUM(10,20)` not `SUM(10,20)`
3. Formulas must start with `=`

---

### Windows: PowerShell execution policy error

**Error:**
```
run.bat cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
# Use Command Prompt instead of PowerShell
# Press Win+R, type 'cmd', press Enter
cd C:\path\to\spark
run.bat

# Or fix PowerShell policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### macOS: "python3 command not found"

**Solution:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Verify
python3 --version
```

---

### Data directory permissions error

**Solution:**
```bash
# Fix permissions
chmod 755 ~/.spark_personal
chmod 644 ~/.spark_personal/*

# Verify
ls -la ~/.spark_personal
```

---

## Still Having Issues?

### Enable Debug Mode

```bash
# Set environment variables for debugging
export QT_DEBUG_PLUGINS=1
export QT_LOGGING_RULES="qt.qpa.*=true"

# Run with debug output
./run.sh 2>&1 | tee debug.log

# Review debug.log for detailed errors
```

### Get Help

1. **Check documentation:**
   - [INSTALL.md](INSTALL.md) - Installation guide
   - [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md) - System library requirements
   - [README.md](README.md) - Feature documentation

2. **Search for similar issues:**
   - GitHub Issues
   - Stack Overflow (tag: pyqt6)

3. **Report a bug:**
   - Include: OS, Python version, error message
   - Attach: debug.log if available
   - Steps to reproduce

---

## System Information

To report issues, include this information:

```bash
# OS and version
uname -a

# Python version
python3 --version

# Installed packages in venv
source venv/bin/activate
pip list
deactivate

# Qt libraries (Linux)
ldconfig -p | grep -E 'libxcb|libxkbcommon'

# SPARK files
ls -la ~/.spark_personal/
```

---

## Emergency: Fresh Install

If all else fails, completely remove and reinstall:

```bash
# 1. Backup your data first!
cp -r ~/.spark_personal ~/spark_backup_$(date +%Y%m%d)

# 2. Remove everything
cd /path/to/spark
rm -rf venv .system_deps_checked

# 3. On Linux, verify system dependencies
# See SYSTEM_DEPENDENCIES.md

# 4. Reinstall
./run.sh

# 5. Restore data if needed
cp -r ~/spark_backup_YYYYMMDD/* ~/.spark_personal/
```

---

**Most issues are solved by installing system dependencies on Linux.**

Quick fix for 90% of Linux issues:
```bash
sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0
./run.sh
```
