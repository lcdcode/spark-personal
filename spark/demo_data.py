"""Demo data for SPARK Personal onboarding."""

import json
import shutil
from pathlib import Path


def create_demo_data(database, config=None):
    """Create demo data for new users."""

    # Check if database already has data
    existing_notes = database.get_all_notes()
    if existing_notes:
        return  # Don't create demo data if database already has content

    # Copy spark.png to images folder if config is provided
    if config:
        try:
            # Get the images directory
            images_dir = config.get_images_dir()

            # Find spark.png in the application directory
            app_dir = Path(__file__).parent.parent
            spark_logo = app_dir / "spark.png"

            if spark_logo.exists():
                # Copy to images folder
                destination = images_dir / "spark.png"
                shutil.copy2(spark_logo, destination)
        except Exception as e:
            # Don't fail demo data creation if image copy fails
            print(f"Note: Could not copy spark.png to images folder: {e}")

    # Create demo notes
    welcome_id = database.add_note(
        "DEMO - 1. Welcome to SPARK Personal",
        """# Welcome to SPARK Personal!

SPARK Personal is your all-in-one personal knowledgebase and snippet manager.

## Getting Started

### Notes
You're currently viewing a note! Notes support **Markdown** formatting, making it easy to:
- Create *formatted* text
- Add `code` snippets inline
- Build lists and checklists
- And much more!

### Features
1. **Hierarchical Organization** - Organize notes in a tree structure
2. **Markdown Support** - Use Editor and Preview tabs
3. **Image Support** - Drag & drop or paste images
4. **Search** - Full-text search across all notes
5. **Autosave** - Your work is automatically saved

Try creating a child note by selecting this note and clicking "Add Child"!
"""
    )

    # Programming tips
    programming_id = database.add_note(
        "DEMO - 3. Programming Tips",
        """# Programming Tips & Best Practices

This is a great place to store your programming knowledge!

## Code Quality
- Write clean, readable code
- Follow the DRY principle (Don't Repeat Yourself)
- Use meaningful variable names
- Comment complex logic

## Version Control
- Commit early and often
- Write descriptive commit messages
- Use branches for new features
- Review code before merging
"""
    )

    # Markdown formatting guide
    database.add_note(
        "DEMO - 2. Markdown Formatting Guide",
        """# Markdown Formatting Guide

This note demonstrates all the basic Markdown formatting you can use in SPARK Personal.

---

## Headers

# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6

---

## Text Formatting

**Bold text** using double asterisks

*Italic text* using single asterisks

***Bold and italic*** using triple asterisks

~~Strikethrough~~ using double tildes

`Inline code` using backticks

---

## Lists

### Bulleted List (Unordered)

- First item
- Second item
  - Nested item
  - Another nested item
    - Deeply nested
- Third item

### Numbered List (Ordered)

1. First step
2. Second step
   1. Sub-step A
   2. Sub-step B
3. Third step

### Checklists (Task Lists)

- [ ] Unchecked item
- [x] Checked item
- [ ] Another task to do
- [x] Completed task

---

## Block Quote

> This is a block quote.
> It can span multiple lines.
>
> And include multiple paragraphs.

> Nested quotes work too:
>> This is a nested quote
>>> Even deeper nesting

---

## Code

### Inline Code

Use `print("Hello")` to output text in Python.

### Code Block (Fenced)

```python
def fibonacci(n):
    \"\"\"Generate Fibonacci sequence.\"\"\"
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Usage
for num in fibonacci(10):
    print(num)
```

```javascript
// JavaScript example
const greet = (name) => {
    return `Hello, ${name}!`;
};

console.log(greet('World'));
```

---

## Links and Images

[A link](https://example.com)

[Another link](https://example.com "Hover text")

Images:

![SPARK Logo](spark.png)

---

## Horizontal Rules

Three or more dashes, asterisks, or underscores:

---

***

___

---

## Tables

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Some     | Some     | Even    |
| text     | more     | more     |
| | text | text |

---

## Escaping Characters

Use backslash to escape special characters:

\\*Not italic\\*

\\# Not a header

\\`Not code\\`

---

## Tips

- Switch between **Editor** and **Preview** tabs to see formatted output
- Use **Ctrl+S** to save your notes
- Markdown renders automatically in Preview mode
"""
    )

    # Add child note
    database.add_note(
        "DEMO - Python Tips",
        """# Python-Specific Tips

## Virtual Environments
Always use virtual environments for your projects:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

## List Comprehensions
Prefer list comprehensions for simple transformations:
```python
# Instead of:
squares = []
for x in range(10):
    squares.append(x**2)

# Use:
squares = [x**2 for x in range(10)]
```
""",
        parent_id=programming_id
    )

    # Add demo spreadsheet
    demo_sheet_data = {
        "A1": "Budget Tracker",
        "A3": "Category",
        "B3": "Amount",
        "C3": "Notes",
        "A4": "Food",
        "B4": "500",
        "C4": "Groceries",
        "A5": "Transportation",
        "B5": "200",
        "C5": "Gas & Parking",
        "A6": "Entertainment",
        "B6": "150",
        "C6": "Movies, Games",
        "A8": "Total",
        "B8": "=SUM(B4:B6)",
    }
    database.add_spreadsheet("Monthly Budget", json.dumps(demo_sheet_data))

    # Simple calculations sheet
    calc_sheet_data = {
        "A1": "Simple Calculator",
        "A3": "Value 1",
        "B3": "10",
        "A4": "Value 2",
        "B4": "20",
        "A5": "Sum",
        "B5": "=SUM(B3,B4)",
        "A6": "Average",
        "B6": "=AVERAGE(B3:B4)",
        "A8": "Today's Date",
        "B8": "=DATE(TODAY())",
    }
    database.add_spreadsheet("Calculator", json.dumps(calc_sheet_data))

    # Add demo snippets
    database.add_snippet(
        "Python Hello World",
        """def greet(name):
    \"\"\"Greet a person by name.\"\"\"
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
""",
        "Python",
        "basics, functions, hello-world"
    )

    database.add_snippet(
        "JavaScript Fetch API",
        """// Fetch data from an API
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Usage
fetchData('https://api.example.com/data')
    .then(data => console.log(data))
    .catch(error => console.error(error));
""",
        "JavaScript",
        "api, fetch, async, error-handling"
    )

    database.add_snippet(
        "SQL Query Template",
        """-- Select with JOIN
SELECT
    u.id,
    u.name,
    u.email,
    COUNT(o.id) as order_count,
    SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = 1
GROUP BY u.id, u.name, u.email
HAVING COUNT(o.id) > 0
ORDER BY total_spent DESC
LIMIT 10;
""",
        "SQL",
        "query, join, aggregate, template"
    )

    database.add_snippet(
        "Git Commands Cheatsheet",
        """# Common Git Commands

# Clone a repository
git clone <repository-url>

# Create and switch to new branch
git checkout -b feature/new-feature

# Stage changes
git add .

# Commit changes
git commit -m "Descriptive commit message"

# Push to remote
git push origin <branch-name>

# Pull latest changes
git pull origin main

# Merge branch
git merge feature/new-feature

# View status
git status

# View commit history
git log --oneline --graph
""",
        "Shell",
        "git, version-control, commands, cheatsheet"
    )

    database.add_snippet(
        "React Functional Component",
        """import React, { useState, useEffect } from 'react';

function MyComponent({ title, initialCount = 0 }) {
    const [count, setCount] = useState(initialCount);

    useEffect(() => {
        document.title = `Count: ${count}`;
    }, [count]);

    const increment = () => setCount(prev => prev + 1);
    const decrement = () => setCount(prev => prev - 1);

    return (
        <div>
            <h1>{title}</h1>
            <p>Count: {count}</p>
            <button onClick={increment}>+</button>
            <button onClick={decrement}>-</button>
        </div>
    );
}

export default MyComponent;
""",
        "JavaScript",
        "react, hooks, component, useState, useEffect"
    )
