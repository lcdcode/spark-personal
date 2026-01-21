# SPARK Personal - Quick Start Guide

Get up and running with SPARK Personal in 2 minutes!

## Installation

### Step 1: Ensure Python is Installed
Make sure you have Python 3.8 or higher installed:
```bash
python --version
```

### Step 2: Run the Launcher Script

**That's it!** Just make the launcher script executable with a chmod, run the script, and everything else is automatic:

**Linux/macOS:**
```bash
chmod +x run.sh  # Make executable (only needed once)
./run.sh
```

**Windows:**
```batch
run.bat
```

The launcher will automatically:
- Create a Python virtual environment
- Install all required dependencies
- Start SPARK Personal

**No manual pip install needed!** The virtual environment keeps everything isolated from your system Python.

---

### Alternative: Manual Installation

If you prefer manual control:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run
python -m spark.main
```

## First Steps

### 1. Explore the Demo Data
When you first launch SPARK Personal, you'll see demo data including:
- Welcome notes explaining features
- Programming tips with example notes
- Sample spreadsheets (budget tracker, calculator)
- Code snippet examples in various languages

### 2. Create Your First Note
1. Go to the **Notes** tab
2. Click **Add Note**
3. Enter a title
4. Start typing in the **Editor** tab
5. Use Markdown formatting:
   - `# Heading`
   - `**bold**` and `*italic*`
   - `` `code` ``
   - Lists with `-` or `1.`
6. Click **Preview** to see the rendered result
7. Press **Ctrl+S** to save

### 3. Try the Spreadsheet
1. Go to the **Spreadsheets** tab
2. Click **New Sheet**
3. Enter data in cells
4. Try a formula: `=SUM(10,20,30)`
5. Click **Recalculate** to update
6. Click **Save** to persist

### 4. Add a Code Snippet
1. Go to the **Code Snippets** tab
2. Click **Add Snippet**
3. Choose a programming language
4. Paste or type your code
5. Add tags (comma-separated)
6. Click **Save**
7. Use **Copy to Clipboard** for quick access

### 5. Customize Your Experience
1. Go to **File → Settings**
2. Choose a theme (Light, Dark, Solarized, Gruvbox)
3. Adjust font and size
4. Configure autosave interval
5. Click **Save** and restart

### 6. Set Up Backups
1. Go to **File → Backup Manager**
2. Click **Create Backup** to make your first backup
3. Configure automatic backups:
   - Enable automatic backups
   - Set interval (default: 24 hours)
4. Optionally change backup location

## Tips & Tricks

### Keyboard Shortcuts
- **Ctrl+S**: Save current item
- **Ctrl+F**: Focus search
- **Ctrl+Q**: Quit application

### Search
Use the search bar at the bottom to quickly find:
- Notes by title or content
- Snippets by title, code, or tags

### Organize Notes
Create a hierarchy by:
1. Selecting a parent note
2. Clicking **Add Child**
3. Building a tree structure

### Spreadsheet Formulas
- Cell references: `A1`, `B2`, etc.
- Functions: `=SUM(A1,A2,A3)`
- Logical: `=IF(A1>10,"High","Low")`
- Date: `=TODAY()` or `=NOW()`

### Theme Switching
Quick theme change:
- **View** menu → Select theme
- Changes apply immediately

### Data Location
All your data is stored in:
```
~/.spark_personal/
├── config.yaml      # Configuration
├── spark.db         # Database
├── images/          # Note images
└── backups/         # Backup files
```

## Common Workflows

### Taking Meeting Notes
1. Create a "Meetings" parent note
2. For each meeting, add a child note
3. Use Markdown for formatting
4. Add action items as bullet lists
5. Search later to find specific meetings

### Code Reference Library
1. Organize snippets by language
2. Use tags for categories (e.g., "api", "database")
3. Filter by language in the dropdown
4. Search across all snippets
5. Quick copy when you need them

### Budget Tracking
1. Create a spreadsheet for each month
2. Use formulas to calculate totals
3. Track spending categories
4. Use `AVERAGE()` for trends

### Project Documentation
1. Create a parent note for the project
2. Add child notes for:
   - Architecture
   - API documentation
   - Setup instructions
   - Meeting notes
3. Use Markdown code blocks for examples

## Next Steps

- Read the full [README.md](README.md) for detailed features
- Customize themes in [themes.py](spark/themes.py)
- Check [technical_doc.md](technical_doc.md) for architecture
- Set up regular backups
- Start organizing your knowledge!

## Need Help?

- Check the **Help → About** menu
- Review the README for troubleshooting
- Open an issue on GitHub

---

Happy organizing! 🚀
