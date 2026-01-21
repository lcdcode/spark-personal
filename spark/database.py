"""Database models and management for SPARK Personal."""

import os
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime


class Database:
    """Manages SQLite database operations."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.init_database()

    def connect(self):
        """Establish database connection."""
        if not self.connection:
            # Check if database file is new (doesn't exist yet)
            is_new_db = not self.db_path.exists()

            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row

            # Set restrictive permissions on new database file
            if is_new_db:
                try:
                    os.chmod(self.db_path, 0o600)
                except OSError:
                    pass  # May fail on some systems, not critical
        return self.connection

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def init_database(self):
        """Initialize database schema."""
        conn = self.connect()
        cursor = conn.cursor()

        # Notes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                parent_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES notes(id) ON DELETE CASCADE
            )
        ''')

        # Spreadsheets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spreadsheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Code snippets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                code TEXT,
                language TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create indexes for search
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_snippets_title ON snippets(title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_snippets_language ON snippets(language)')

        conn.commit()

    # Notes operations
    def add_note(self, title: str, content: str = "", parent_id: Optional[int] = None) -> int:
        """Add a new note."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO notes (title, content, parent_id) VALUES (?, ?, ?)',
            (title, content, parent_id)
        )
        conn.commit()
        return cursor.lastrowid

    def update_note(self, note_id: int, title: str, content: str):
        """Update an existing note."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE notes SET title = ?, content = ?, modified_at = ? WHERE id = ?',
            (title, content, datetime.now(), note_id)
        )
        conn.commit()

    def delete_note(self, note_id: int):
        """Delete a note and its children."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()

    def get_note(self, note_id: int) -> Optional[sqlite3.Row]:
        """Get a note by ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notes WHERE id = ?', (note_id,))
        return cursor.fetchone()

    def get_all_notes(self) -> List[sqlite3.Row]:
        """Get all notes."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notes ORDER BY parent_id, title')
        return cursor.fetchall()

    def get_root_notes(self) -> List[sqlite3.Row]:
        """Get all root-level notes."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notes WHERE parent_id IS NULL ORDER BY title')
        return cursor.fetchall()

    def get_child_notes(self, parent_id: int) -> List[sqlite3.Row]:
        """Get child notes of a parent."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notes WHERE parent_id = ? ORDER BY title', (parent_id,))
        return cursor.fetchall()

    def search_notes(self, query: str) -> List[sqlite3.Row]:
        """Search notes by title or content."""
        conn = self.connect()
        cursor = conn.cursor()
        search_pattern = f'%{query}%'
        cursor.execute(
            'SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? ORDER BY modified_at DESC',
            (search_pattern, search_pattern)
        )
        return cursor.fetchall()

    # Spreadsheet operations
    def add_spreadsheet(self, name: str, data: str = "{}") -> int:
        """Add a new spreadsheet."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO spreadsheets (name, data) VALUES (?, ?)',
            (name, data)
        )
        conn.commit()
        return cursor.lastrowid

    def update_spreadsheet(self, sheet_id: int, name: str, data: str):
        """Update an existing spreadsheet."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE spreadsheets SET name = ?, data = ?, modified_at = ? WHERE id = ?',
            (name, data, datetime.now(), sheet_id)
        )
        conn.commit()

    def delete_spreadsheet(self, sheet_id: int):
        """Delete a spreadsheet."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM spreadsheets WHERE id = ?', (sheet_id,))
        conn.commit()

    def get_spreadsheet(self, sheet_id: int) -> Optional[sqlite3.Row]:
        """Get a spreadsheet by ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM spreadsheets WHERE id = ?', (sheet_id,))
        return cursor.fetchone()

    def get_all_spreadsheets(self) -> List[sqlite3.Row]:
        """Get all spreadsheets."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM spreadsheets ORDER BY name')
        return cursor.fetchall()

    # Snippet operations
    def add_snippet(self, title: str, code: str = "", language: str = "", tags: str = "") -> int:
        """Add a new code snippet."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO snippets (title, code, language, tags) VALUES (?, ?, ?, ?)',
            (title, code, language, tags)
        )
        conn.commit()
        return cursor.lastrowid

    def update_snippet(self, snippet_id: int, title: str, code: str, language: str, tags: str):
        """Update an existing snippet."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE snippets SET title = ?, code = ?, language = ?, tags = ?, modified_at = ? WHERE id = ?',
            (title, code, language, tags, datetime.now(), snippet_id)
        )
        conn.commit()

    def delete_snippet(self, snippet_id: int):
        """Delete a snippet."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM snippets WHERE id = ?', (snippet_id,))
        conn.commit()

    def get_snippet(self, snippet_id: int) -> Optional[sqlite3.Row]:
        """Get a snippet by ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM snippets WHERE id = ?', (snippet_id,))
        return cursor.fetchone()

    def get_all_snippets(self) -> List[sqlite3.Row]:
        """Get all snippets."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM snippets ORDER BY language, title')
        return cursor.fetchall()

    def get_snippets_by_language(self, language: str) -> List[sqlite3.Row]:
        """Get snippets by language."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM snippets WHERE language = ? ORDER BY title', (language,))
        return cursor.fetchall()

    def search_snippets(self, query: str) -> List[sqlite3.Row]:
        """Search snippets by title, code, or tags."""
        conn = self.connect()
        cursor = conn.cursor()
        search_pattern = f'%{query}%'
        cursor.execute(
            'SELECT * FROM snippets WHERE title LIKE ? OR code LIKE ? OR tags LIKE ? ORDER BY modified_at DESC',
            (search_pattern, search_pattern, search_pattern)
        )
        return cursor.fetchall()
