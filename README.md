# SPARK Personal 

(**S**nippet, **P**ersonal **A**rchive, and **R**eference **K**eeper)
A cross-platform personal knowledgebase and snippet manager for programmers, built with Python and Qt.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green)
![License](https://img.shields.io/badge/License-GPL3-yellow)

## Features

### 📝 Hierarchical Notes
- Organize notes in a tree structure
- Full Markdown support with Editor and Preview tabs
- Drag-and-drop and clipboard image support
- Full-text search across all notes
- Quick save (Ctrl+S) and autosave
- Defaults to Preview mode for existing notes
- Collapsible sidebar for distraction-free editing

### 📊 Spreadsheets
- Excel-like spreadsheet interface
- Built-in formula engine with common functions:
  - Mathematical: `SUM`, `AVERAGE`
  - Logical: `IF`, `AND`, `OR`, `NOT`
  - Date/Time: `TODAY`, `NOW`
- Cell formatting and styling
- Undo/redo functionality
- Formula bar for easy editing
- Autosave support
- Collapsible sidebar for focused work

### 💻 Code Snippets
- Store and organize code snippets
- Syntax highlighting for 25+ programming languages
- Tag-based organization
- Language filtering
- Quick copy-to-clipboard
- Full-text search
- Live preview with syntax highlighting
- Collapsible sidebar for maximum code viewing space

### 🔄 Backup Management
- Configurable backup location
- Scheduled automatic backups
- Manual backup creation
- Backup restore functionality
- Automatic cleanup of old backups

### 🎨 Themes and Customization
- Multiple built-in themes:
  - Light
  - Dark
  - Solarized-like Light
  - Solarized-like Dark
  - Gruvbox-like
- Customizable fonts and sizes
- Configurable window dimensions
- Adjustable autosave intervals

## Installation

### For Quick Start, see [QUICKSTART.md](QUICKSTART.md)

### Prerequisites
- Python 3.8 or higher
- **Linux only**: Qt system libraries (see below)

### Linux Users: Install System Dependencies First

Before running SPARK Personal on Linux, install the required Qt libraries:

```bash
# Ubuntu/Debian
sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1

# Fedora/RHEL
sudo dnf install -y xcb-util-cursor xcb-util-image xcb-util-keysyms libxkbcommon-x11

# For other distributions, see SYSTEM_DEPENDENCIES.md
```

**macOS and Windows users don't need this step** - proceed directly to Quick Install below.

> **Troubleshooting:** If you see errors like "Could not load the Qt platform plugin 'xcb'", you're missing system dependencies. See [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md) for detailed instructions.

### Quick Install (Recommended)

The easiest way to run SPARK Personal is using the provided launcher scripts, which automatically set up a virtual environment:

**Linux/macOS:**
```bash
./run.sh
```

**Windows:**
```batch
run.bat
```

On first run, the scripts will:
1. Create a Python virtual environment (`venv/`)
2. Install all dependencies automatically
3. Launch SPARK Personal

**Subsequent runs** will just activate the virtual environment and start the application.

### Manual Installation (Advanced)

If you prefer to install manually or need more control:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spark-personal.git
cd spark-personal
```

2. Create and activate virtual environment:
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python -m spark.main
```

### System-Wide Installation (Optional)

For system-wide access:
```bash
pip install -e .
spark
```

## Usage

### Running the application

**Easiest method** (uses virtual environment automatically):
```bash
./run.sh        # Linux/macOS
run.bat         # Windows
```

**Manual method** (if installed system-wide):
```bash
spark
```

**Or run directly with Python:**
```bash
python -m spark.main
```

### First Launch

On first launch, SPARK Personal will:
1. Create a configuration directory at `~/.spark_personal/`
2. Generate a default configuration file
3. Create a SQLite database
4. Populate demo data for onboarding

### Keyboard Shortcuts

- **Ctrl+S**: Save current note/snippet
- **Ctrl+F**: Focus search bar
- **Ctrl+Q**: Quit application
- **Ctrl+1**: Switch to Notes Tab
- **Ctrl+2**: Switch to Spreadsheets Tab
- **Ctro+3**: Switch to Snippets Tab

### Configuration

The configuration file is located at `~/.spark_personal/config.yaml`. You can edit it manually or use the Settings dialog (File → Settings).

Example configuration:
```yaml
theme: Dark
font_family: Consolas
font_size: 10
window_width: 1200
window_height: 800
database_location: ''  # Empty uses default location
backup_location: ''    # Empty uses default location
backup_enabled: true
backup_interval_hours: 24
backup_retention_count: 10
autosave_enabled: true
autosave_interval_seconds: 300
editor_tab_width: 4
```

## Updating

To Update SPARK to the latest version, simply pull the latest from Git.

Switch to the spark directory and run:

```bash
git pull origin master
```

## Features in Detail

### Notes

1. **Create a note**: Click "Add Note" to create a root-level note
2. **Create child note**: Select a note and click "Add Child"
3. **Edit note**: Select a note, edit in the Editor tab
4. **Preview**: Switch to Preview tab to see Markdown rendering
5. **Save**: Press Ctrl+S or click Save button
6. **Delete**: Select a note and click Delete (deletes children too)
7. **Search**: Use the search bar to find notes by title or content

### Spreadsheets

1. **Create sheet**: Click "New Sheet"
2. **Edit cells**: Click any cell and type a value or formula
3. **Formulas**: Start with `=` (e.g., `=SUM(10,20)`)
4. **Cell references**: Use column letter + row number (e.g., `A1`, `B5`)
5. **Recalculate**: Click "Recalculate" to update all formulas
6. **Save**: Click "Save" to persist changes

**Supported Functions:**
- `SUM(a,b,c,...)` - Add numbers
- `AVERAGE(a,b,c,...)` - Calculate average
- `IF(condition,true_val,false_val)` - Conditional logic
- `AND(True,True)` - Logical AND
- `OR(False,False)` - Logical OR
- `NOT(True)` - Logical NOT
- `TODAY()` - Current date
- `NOW()` - Current date and time
- `DATE(timestamp)` - Convert timestamp to date string

#### Spreadsheet Formula Reference

**Arithmetic Operators:**
- `+` - Addition (e.g., `=A1 + B1`)
- `-` - Subtraction (e.g., `=A1 - B1`)
- `*` - Multiplication (e.g., `=A1 * 2`)
- `/` - Division (e.g., `=A1 / B1`)
- `//` - Floor division (e.g., `=17 // 5` returns 3)
- `%` - Modulo/remainder (e.g., `=17 % 5` returns 2)
- `**` or `^` - Exponentiation (e.g., `=2^8` or `=2**8` returns 256)

**Comparison Operators:**
- `=` or `==` - Equality (e.g., `=A1 = 5`)
- `!=` - Not equal (e.g., `=A1 != 0`)
- `<` - Less than (e.g., `=A1 < 10`)
- `<=` - Less than or equal (e.g., `=A1 <= 10`)
- `>` - Greater than (e.g., `=A1 > 0`)
- `>=` - Greater than or equal (e.g., `=A1 >= 0`)

**Boolean Operators:**
- `and` - Logical AND (e.g., `=A1 > 5 and B1 < 10`)
- `or` - Logical OR (e.g., `=A1 = 0 or B1 = 0`)

**Formula Examples:**

Basic arithmetic:
```
=A1 + B1 * 2          # Addition and multiplication
=10^2                 # Exponentiation (100)
=(A1 + B1) / 2        # Average of two cells
```

Comparisons and logic:
```
=A1 = 5               # Check if A1 equals 5
=A1 > 0 and A1 < 100  # Check if A1 is between 0 and 100
=IF(A1 > 10, "High", "Low")  # Conditional text
```

Cell ranges and functions:
```
=SUM(A1:A10)          # Sum range A1 through A10
=AVERAGE(B1,B2,B3)    # Average of specific cells
=SUM(A1:A5,C1:C5)     # Sum multiple ranges
```

Date calculations:
```
=TODAY()              # Current date
=TODAY() + 7          # Date 7 days from now
=DATE(TODAY() + 30)   # Format date 30 days out
=IF(A1 < TODAY(), "Overdue", "Current")  # Date comparison
```

Complex formulas:
```
=IF(A1 = 0, 0, B1/A1)                    # Avoid division by zero
=SUM(A1:A10) / 10                        # Manual average
=IF(A1 > 0 and A1 < 100, A1 * 2, A1)   # Conditional calculation
```

**Notes:**
- All formulas must start with `=`
- Cell references are case-insensitive (A1 = a1)
- Supports both `=` and `==` for equality checks
- Supports both `^` and `**` for exponentiation (Excel-compatible)
- Date values are stored internally as numeric timestamps
- Chained comparisons (e.g., `5 < A1 < 10`) are not supported - use `and` instead

### Code Snippets

1. **Create snippet**: Click "Add Snippet"
2. **Select language**: Choose from 25+ languages
3. **Add tags**: Enter comma-separated tags
4. **Edit code**: Type or paste your code
5. **Preview**: See syntax-highlighted preview
6. **Copy**: Click "Copy to Clipboard" for quick access
7. **Filter**: Use language dropdown to filter snippets
8. **Search**: Search by title, code content, or tags

### Backup Manager

Access via File → Backup Manager

1. **Create backup**: Click "Create Backup"
2. **Restore backup**: Select a backup and click "Restore Selected"
3. **Delete backup**: Select a backup and click "Delete Selected"
4. **Change location**: Click "Change" to select a new backup directory
5. **Auto-backup**: Configure interval and enable/disable

## AI Assistance

SPARK Personal was developed with assistance from the following tools.
All code was manually reviewed and tested by the author.

| TOOL             | VERSION    | PURPOSE                                      |
|------------------|------------|----------------------------------------------|
| Anthropic Claude | Sonnet 4.5 | Coding assistance, Documentation, Unit Tests |
| Anthropic Claude | Opus 4.5   | Coding assistance, Documentation             |

## Project Structure

```
spark/
├── __init__.py           # Package initialization
├── main.py               # Application entry point
├── config.py             # Configuration management
├── database.py           # SQLite database operations
├── themes.py             # Theme definitions and stylesheets
├── main_window.py        # Main application window
├── notes_widget.py       # Notes functionality
├── spreadsheet_widget.py # Spreadsheet functionality
├── snippets_widget.py    # Code snippets functionality
├── backup_manager.py     # Backup management
└── demo_data.py          # Demo data generation

requirements.txt          # Python dependencies
setup.py                  # Installation configuration
README.md                 # This file
```

## Database Schema

SPARK Personal uses SQLite with the following tables:

- **notes**: Hierarchical note storage
- **spreadsheets**: Spreadsheet data in JSON format
- **snippets**: Code snippets with metadata

All tables include timestamps for creation and modification tracking.

## Development

### Adding a new theme

Edit [themes.py](spark/themes.py) and add your theme to the `THEMES` dictionary:

```python
THEMES = {
    "Your Theme": {
        "background": "#ffffff",
        "foreground": "#000000",
        # ... other colors
    }
}
```

### Extending the formula engine

Edit [spreadsheet_widget.py](spark/spreadsheet_widget.py) and add new functions to the `FormulaEngine` class.

## Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Database errors
- Check permissions on `~/.spark_personal/` directory
- Try deleting the database file to start fresh (backup first!)

### Theme not applying
- Restart the application after changing theme
- Check config file for correct theme name

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

GPL 3.0 License - See LICENSE file for details

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Markdown rendering by [Python-Markdown](https://python-markdown.github.io/)
- Syntax highlighting by [Pygments](https://pygments.org/)
- Configuration with [PyYAML](https://pyyaml.org/)

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**SPARK Personal** - Ignite your productivity! ⚡
