# Virtual Environment Setup for SPARK Personal

## Why Use a Virtual Environment?

A virtual environment keeps SPARK Personal's dependencies isolated from your system Python installation. This prevents:
- Dependency conflicts with other Python projects
- Version mismatches
- Polluting your global Python environment
- Permission issues when installing packages

## Automatic Setup (Easiest!)

SPARK Personal includes launcher scripts that **automatically** create and manage a virtual environment for you.

### Linux/macOS

```bash
./run.sh
```

### Windows

```batch
run.bat
```

**First run:**
- Creates `venv/` directory
- Installs all dependencies automatically
- Launches SPARK Personal

**Subsequent runs:**
- Activates existing virtual environment
- Launches SPARK Personal immediately

**That's it!** You never need to manually manage the virtual environment.

## Manual Setup (For Advanced Users)

If you prefer to manage the virtual environment yourself:

### 1. Create Virtual Environment

```bash
# Linux/macOS
python3 -m venv venv

# Windows
python -m venv venv
```

This creates a `venv/` directory containing:
- Python interpreter
- pip package manager
- Isolated package installation directory

### 2. Activate Virtual Environment

**Every time** you want to run SPARK Personal, activate the environment first:

```bash
# Linux/macOS
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

You'll see `(venv)` in your terminal prompt, indicating the environment is active.

### 3. Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs packages **only** in the virtual environment, not globally.

### 4. Run SPARK Personal

```bash
python -m spark.main
```

### 5. Deactivate When Done

When you're finished using SPARK Personal:

```bash
deactivate
```

This returns you to your normal system Python environment.

## Directory Structure

After running the launcher script, you'll have:

```
spark/
├── venv/                    # Virtual environment (isolated)
│   ├── bin/                 # Scripts (Linux/macOS)
│   ├── Scripts/             # Scripts (Windows)
│   ├── lib/                 # Installed packages
│   └── pyvenv.cfg           # Environment config
├── spark/                   # Application code
├── run.sh                   # Launcher script
├── run.bat                  # Launcher script (Windows)
└── requirements.txt         # Dependencies
```

## Benefits of the Launcher Scripts

Our `run.sh` and `run.bat` scripts provide:

✅ **Zero Configuration** - Just run and go
✅ **Automatic Setup** - Creates venv on first run
✅ **Automatic Updates** - Installs dependencies if missing
✅ **Error Handling** - Clear error messages
✅ **Cross-Platform** - Works on Linux, macOS, Windows

## Managing the Virtual Environment

### Update Dependencies

If dependencies change in `requirements.txt`:

```bash
# Activate environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Update packages
pip install -r requirements.txt --upgrade

# Deactivate
deactivate
```

Or just delete `venv/` and run the launcher again - it will recreate everything.

### Delete Virtual Environment

To completely remove the virtual environment:

```bash
# Linux/macOS
rm -rf venv/

# Windows
rmdir /s venv
```

Then run `./run.sh` or `run.bat` to recreate it.

### Check Installed Packages

```bash
# Activate environment first
source venv/bin/activate

# List installed packages
pip list

# Show specific package
pip show PyQt6

# Deactivate
deactivate
```

## Troubleshooting

### "Permission denied" when running run.sh

Make the script executable:
```bash
chmod +x run.sh
```

### PowerShell execution policy error (Windows)

If you get an error about execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or use Command Prompt instead of PowerShell.

### Virtual environment creation fails

Ensure Python is in your PATH:
```bash
# Check Python version
python --version  # Windows
python3 --version # Linux/macOS

# Should show Python 3.8 or higher
```

### "No module named 'venv'"

Install the venv module:
```bash
# Ubuntu/Debian
sudo apt install python3-venv

# Fedora
sudo dnf install python3-venv
```

### Dependencies won't install

Try upgrading pip first:
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

## Comparison: Global vs Virtual Environment

| Aspect | Global Install | Virtual Environment |
|--------|---------------|---------------------|
| Isolation | ❌ Affects system | ✅ Isolated |
| Conflicts | ❌ Possible | ✅ None |
| Permissions | ⚠️ May need sudo | ✅ User-level |
| Cleanup | ❌ Difficult | ✅ Delete `venv/` |
| Portability | ❌ System-dependent | ✅ Project-specific |
| **Recommended** | ❌ No | ✅ **Yes** |

## Best Practices

1. **Always use virtual environments** for Python projects
2. **Never commit `venv/`** to git (it's in `.gitignore`)
3. **Use the launcher scripts** for simplicity
4. **Update `requirements.txt`** when adding dependencies
5. **Document** any special setup in README

## Quick Reference

```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate          # Linux/macOS
venv\Scripts\activate             # Windows

# Install dependencies
pip install -r requirements.txt

# Run SPARK
python -m spark.main

# Deactivate
deactivate

# Or just use the launcher!
./run.sh    # Linux/macOS
run.bat     # Windows
```

## Conclusion

The launcher scripts (`run.sh` and `run.bat`) make virtual environment management **completely automatic**. You don't need to think about it - just run the script and start using SPARK Personal!

For manual control, follow the manual setup steps. Either way, virtual environments keep your Python installation clean and SPARK Personal's dependencies isolated.

---

**Recommended Approach:** Use `./run.sh` or `run.bat` and let it handle everything automatically! 🚀
