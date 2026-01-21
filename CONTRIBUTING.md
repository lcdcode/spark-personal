# Contributing to SPARK Personal

Thank you for your interest in contributing to SPARK Personal! This guide will help you get started.

## Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/spark-personal.git
cd spark-personal
pip install -r requirements.txt
pip install -e .
```

### 2. Development Tools

Recommended tools:
- **IDE**: PyCharm, Vim/Neovim, VS Code or fork with Python extension
- **Testing**: pytest

### 3. Running from Source

```bash
python -m spark.main
```

## Project Architecture

### Core Components

1. **config.py** - Configuration management using YAML
2. **database.py** - SQLite database operations
3. **main_window.py** - Main application window and menu
4. **themes.py** - Theme definitions and Qt stylesheets

### Feature Widgets

1. **notes_widget.py** - Hierarchical notes with Markdown
2. **spreadsheet_widget.py** - Spreadsheet with formula engine
3. **snippets_widget.py** - Code snippets with syntax highlighting
4. **backup_manager.py** - Backup and restore functionality

### Helper Modules

1. **demo_data.py** - Demo data generation
2. **main.py** - Application entry point

## Adding New Features

### Adding a New Theme

Edit [spark/themes.py](spark/themes.py):

```python
THEMES = {
    "Your New Theme": {
        "background": "#hexcolor",
        "foreground": "#hexcolor",
        "accent": "#hexcolor",
        "border": "#hexcolor",
        "hover": "#hexcolor",
        "selected": "#hexcolor",
        "editor_bg": "#hexcolor",
        "editor_fg": "#hexcolor",
        "tree_bg": "#hexcolor",
    }
}
```

### Adding a Spreadsheet Function

Edit [spark/spreadsheet_widget.py](spark/spreadsheet_widget.py) in the `FormulaEngine` class:

```python
def handle_functions(self, formula: str) -> str:
    # Add your function
    formula = re.sub(
        r'YOURFUNC\((.*?)\)',
        lambda m: str(self.func_your_func(m.group(1))),
        formula
    )
    return formula

def func_your_func(self, args: str) -> Any:
    """Your function implementation."""
    # Implementation here
    pass
```

### Adding a New Widget/Tab

1. Create new widget file (e.g., `spark/your_widget.py`)
2. Implement widget class inheriting from `QWidget`
3. Add signal for modifications: `item_modified = pyqtSignal()`
4. Import in [spark/main_window.py](spark/main_window.py)
5. Add to tabs in `MainWindow.init_ui()`:

```python
self.your_widget = YourWidget(self.database, self.config)
self.your_widget.item_modified.connect(self.on_data_modified)
self.tabs.addTab(self.your_widget, "Your Feature")
```

### Adding Database Tables

Edit [spark/database.py](spark/database.py):

```python
def init_database(self):
    # Add your table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS your_table (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
```

Add CRUD methods:

```python
def add_item(self, name: str) -> int:
    conn = self.connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO your_table (name) VALUES (?)', (name,))
    conn.commit()
    return cursor.lastrowid

def get_item(self, item_id: int) -> Optional[sqlite3.Row]:
    conn = self.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM your_table WHERE id = ?', (item_id,))
    return cursor.fetchone()
```

## Coding Standards

### Python Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to classes and public methods
- Keep functions focused and small

Example:

```python
def calculate_total(values: List[float]) -> float:
    """Calculate the sum of all values.

    Args:
        values: List of numeric values to sum

    Returns:
        The sum of all values
    """
    return sum(values)
```

### Qt/PyQt6 Guidelines

- Use signals and slots for component communication
- Always use layouts, never absolute positioning
- Clean up resources in `closeEvent()`
- Block signals when programmatically updating widgets

Example:

```python
# Block signals during update
self.widget.blockSignals(True)
self.widget.setValue(new_value)
self.widget.blockSignals(False)
```

### Database Guidelines

- Always use parameterized queries (prevent SQL injection)
- Commit after write operations
- Use transactions for multiple operations
- Add indexes for searchable columns

Example:

```python
# Good - parameterized
cursor.execute('SELECT * FROM notes WHERE id = ?', (note_id,))

# Bad - vulnerable to SQL injection
cursor.execute(f'SELECT * FROM notes WHERE id = {note_id}')
```

## Testing

### Manual Testing Checklist

Before submitting:

- [ ] Test on Python 3.8, 3.9, 3.10+
- [ ] Test all CRUD operations (Create, Read, Update, Delete)
- [ ] Test autosave functionality
- [ ] Test backup and restore
- [ ] Test theme switching
- [ ] Test search functionality
- [ ] Test with empty database
- [ ] Test with demo data
- [ ] Check for memory leaks (long-running session)

### Automated Testing (Future)

When adding tests:

```python
# tests/test_database.py
def test_add_note():
    db = Database(':memory:')
    note_id = db.add_note("Test Note", "Content")
    assert note_id > 0
    note = db.get_note(note_id)
    assert note['title'] == "Test Note"
```

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### PR Guidelines

- Provide clear description of changes
- Reference any related issues
- Include screenshots for UI changes
- Ensure code follows style guidelines
- Update documentation if needed

## Feature Ideas

Looking for contribution ideas? Here are some potential enhancements:

### High Priority
- [ ] Export notes to PDF/HTML
- [ ] Import/export snippets (JSON, XML)
- [ ] Note templates
- [ ] Tagging system for notes
- [ ] Full-text search with highlighting
- [ ] Keyboard shortcuts customization

### Medium Priority
- [ ] Note version history
- [ ] Spreadsheet charts/graphs
- [ ] Snippet sharing (export/import)
- [ ] Note linking (wiki-style)
- [ ] Dark mode for Markdown preview
- [ ] Plugin system

### Low Priority
- [ ] Cloud sync support
- [ ] Mobile companion app
- [ ] Encrypted notes
- [ ] Collaborative features
- [ ] Integration with external editors
- [ ] REST API

## Code Review Criteria

When reviewing PRs, we look for:

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it clean, readable, maintainable?
- **Performance**: Are there any bottlenecks?
- **Security**: Are there any vulnerabilities?
- **UX**: Is the user experience intuitive?
- **Documentation**: Are changes documented?
- **Testing**: Has it been tested thoroughly?

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: Email security@sparkpersonal.dev
- **Chat**: Join our Discord (coming soon)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- About dialog (for major contributions)

Thank you for making SPARK Personal better! 🎉
