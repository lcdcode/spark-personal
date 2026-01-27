"""Database models and management for SPARK Personal."""

import os
import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    """Manages SQLite database operations."""

    def __init__(self, db_path: Path, on_save_callback=None):
        logger.info(f"Initializing database at: {db_path}")
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.on_save_callback = on_save_callback  # Callback to notify before saving
        try:
            self.init_database()
            logger.info("Database initialization complete")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}", exc_info=True)
            raise

    def _before_commit(self):
        """Call this before any commit to notify the app of self-initiated changes."""
        if self.on_save_callback:
            self.on_save_callback()

    def connect(self):
        """Establish database connection."""
        if not self.connection:
            # Check if database file is new (doesn't exist yet)
            is_new_db = not self.db_path.exists()
            logger.debug(f"Connecting to database (new={is_new_db})")

            try:
                self.connection = sqlite3.connect(str(self.db_path))
                self.connection.row_factory = sqlite3.Row
                logger.debug("Database connection established")

                # Set restrictive permissions on new database file
                if is_new_db:
                    try:
                        os.chmod(self.db_path, 0o600)
                        logger.debug("Set database file permissions to 0600")
                    except OSError as e:
                        logger.warning(f"Could not set database permissions: {e}")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}", exc_info=True)
                raise
        return self.connection

    def close(self):
        """Close database connection."""
        if self.connection:
            logger.debug("Closing database connection")
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
        logger.info(f"Adding note: title='{title[:50]}...', parent_id={parent_id}, content_len={len(content)}")
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO notes (title, content, parent_id) VALUES (?, ?, ?)',
                (title, content, parent_id)
            )
            self._before_commit()
            conn.commit()
            note_id = cursor.lastrowid
            logger.info(f"Note added successfully with id={note_id}")
            return note_id
        except Exception as e:
            logger.error(f"Failed to add note: {e}", exc_info=True)
            raise

    def update_note(self, note_id: int, title: str, content: str):
        """Update an existing note."""
        logger.info(f"Updating note id={note_id}, title='{title[:50]}...', content_len={len(content)}")
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE notes SET title = ?, content = ?, modified_at = ? WHERE id = ?',
                (title, content, datetime.now(), note_id)
            )
            self._before_commit()
            conn.commit()
            logger.info(f"Note {note_id} updated successfully")
        except Exception as e:
            logger.error(f"Failed to update note {note_id}: {e}", exc_info=True)
            raise

    def update_note_parent(self, note_id: int, new_parent_id: Optional[int]):
        """Update a note's parent_id."""
        logger.info(f"Updating note id={note_id} parent to {new_parent_id}")
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Prevent circular references
            if new_parent_id is not None:
                if note_id == new_parent_id:
                    raise ValueError("Cannot make a note its own parent")

                # Check if new_parent_id is a descendant of note_id
                if self._is_descendant(note_id, new_parent_id):
                    raise ValueError("Cannot make a note a child of its own descendant")

            cursor.execute(
                'UPDATE notes SET parent_id = ?, modified_at = ? WHERE id = ?',
                (new_parent_id, datetime.now(), note_id)
            )
            self._before_commit()
            conn.commit()
            logger.info(f"Note {note_id} parent updated successfully")
        except Exception as e:
            logger.error(f"Failed to update note {note_id} parent: {e}", exc_info=True)
            raise

    def _is_descendant(self, ancestor_id: int, potential_descendant_id: int) -> bool:
        """Check if potential_descendant_id is a descendant of ancestor_id."""
        conn = self.connect()
        cursor = conn.cursor()

        # Get all descendants of ancestor_id recursively
        descendants = set()
        to_check = [ancestor_id]

        while to_check:
            current_id = to_check.pop()
            cursor.execute('SELECT id FROM notes WHERE parent_id = ?', (current_id,))
            children = cursor.fetchall()
            for child in children:
                child_id = child['id']
                if child_id == potential_descendant_id:
                    return True
                descendants.add(child_id)
                to_check.append(child_id)

        return False

    def delete_note(self, note_id: int):
        """Delete a note and its children."""
        logger.info(f"Deleting note id={note_id}")
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            self._before_commit()
            conn.commit()
            logger.info(f"Note {note_id} deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete note {note_id}: {e}", exc_info=True)
            raise

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
        self._before_commit()
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
        self._before_commit()
        conn.commit()

    def delete_spreadsheet(self, sheet_id: int):
        """Delete a spreadsheet."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM spreadsheets WHERE id = ?', (sheet_id,))
        self._before_commit()
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
        self._before_commit()
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
        self._before_commit()
        conn.commit()

    def delete_snippet(self, snippet_id: int):
        """Delete a snippet."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM snippets WHERE id = ?', (snippet_id,))
        self._before_commit()
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
