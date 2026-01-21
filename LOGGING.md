# SPARK Personal - Error Logging

## Overview

Comprehensive error logging has been added to SPARK Personal to help diagnose crashes and issues, particularly those occurring when adding or editing notes.

## Recent Fix

**Fixed: RuntimeError when clicking notes after save** - The crash occurred because Qt was trying to access deleted QTreeWidgetItem objects. The fix includes:
1. Added error handling in `on_note_selected` to catch deleted items
2. Optimized save behavior to only reload tree when title changes (not for content-only saves)
3. This prevents unnecessary tree reloads that were causing the crash

## Log File Location

All logs are written to: `~/.spark_personal/spark_debug.log`

This file contains:
- Detailed timestamps for every operation
- Function names and line numbers
- Full stack traces for any errors
- Debug information about database operations
- User actions (adding notes, saving, etc.)

## Viewing Logs

To monitor SPARK in real-time:
```bash
tail -f ~/.spark_personal/spark_debug.log
```

To view recent errors:
```bash
grep -i error ~/.spark_personal/spark_debug.log | tail -20
```

To view recent crashes:
```bash
grep -i "critical\|unhandled" ~/.spark_personal/spark_debug.log
```

## What's Logged

### Startup and Initialization
- Application startup time
- Python version
- Log file location
- Database initialization
- Configuration loading

### Note Operations
- Adding new root notes
- Adding child notes
- Saving notes (manual and autosave)
- Loading notes into the tree
- Updating notes
- Deleting notes

### Database Operations
- All SQL queries with parameters
- Connection events
- Transaction commits
- Database errors with full stack traces

### Errors and Crashes
- **Unhandled exceptions**: Caught globally with full stack traces
- **Operation failures**: Each operation logs its failure with context
- **User-facing errors**: Shown in dialog boxes and logged to file

## Error Dialog Boxes

When an error occurs, SPARK will:
1. Log the full error with stack trace to the debug log
2. Show a user-friendly error dialog
3. Tell the user to check `~/.spark_personal/spark_debug.log` for details

## Example Log Entries

### Successful Note Creation
```
2026-01-21 15:30:45,123 [INFO] spark.notes_widget:add_note:374 - User requested to add new root note
2026-01-21 15:30:47,456 [INFO] spark.notes_widget:add_note:378 - Creating new root note with title: 'My New Note'
2026-01-21 15:30:47,457 [INFO] spark.database:add_note:110 - Adding note: title='My New Note...', parent_id=None, content_len=0
2026-01-21 15:30:47,459 [INFO] spark.database:add_note:120 - Note added successfully with id=42
2026-01-21 15:30:47,460 [INFO] spark.notes_widget:add_note:380 - Root note created with id=42, reloading notes tree
2026-01-21 15:30:47,461 [DEBUG] spark.notes_widget:load_notes:309 - Loading notes into tree widget
2026-01-21 15:30:47,465 [DEBUG] spark.notes_widget:load_notes:313 - Found 5 root notes
2026-01-21 15:30:47,470 [DEBUG] spark.notes_widget:load_notes:321 - Notes tree loading complete
2026-01-21 15:30:47,471 [INFO] spark.notes_widget:add_note:383 - Root note creation completed successfully
```

### Error During Save
```
2026-01-21 15:32:10,123 [INFO] spark.notes_widget:save_current_note:545 - Saving note id=42
2026-01-21 15:32:10,124 [DEBUG] spark.notes_widget:save_current_note:549 - Note title: 'My New Note...', content_len=1234
2026-01-21 15:32:10,125 [ERROR] spark.database:update_note:139 - Failed to update note 42: database is locked
Traceback (most recent call last):
  File "/home/user/code/spark/spark/database.py", line 130, in update_note
    cursor.execute(...)
sqlite3.OperationalError: database is locked
2026-01-21 15:32:10,126 [ERROR] spark.notes_widget:save_current_note:559 - Failed to save note id=42: database is locked
```

### Crash / Unhandled Exception
```
2026-01-21 15:35:22,789 [CRITICAL] spark.main:excepthook:56 - Unhandled exception occurred!
Traceback (most recent call last):
  File "/home/user/code/spark/spark/notes_widget.py", line 335, in add_tree_item
    item.setText(0, note['title'])
KeyError: 'title'
```

## Debugging Tips

1. **Reproduce the crash** while monitoring the log file
2. **Look for the last few operations** before the crash
3. **Check for ERROR or CRITICAL** log levels
4. **Full stack traces** show exactly where the error occurred
5. **Share the relevant log section** when reporting issues

## Log File Management

The log file appends to itself on each run, so it will grow over time. To clear old logs:

```bash
# View log file size
ls -lh ~/.spark_personal/spark_debug.log

# Clear the log file
> ~/.spark_personal/spark_debug.log

# Or delete it (will be recreated on next run)
rm ~/.spark_personal/spark_debug.log
```

## Log Levels

- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: General informational messages about operations
- **WARNING**: Something unexpected happened, but SPARK continues
- **ERROR**: A serious problem occurred, operation failed
- **CRITICAL**: A very serious error, SPARK may crash

## Implementation Details

Logging is implemented in:
- [spark/main.py](spark/main.py) - Global exception handler and startup logging
- [spark/database.py](spark/database.py) - All database operations
- [spark/notes_widget.py](spark/notes_widget.py) - User interactions with notes

All log messages include:
- Timestamp (millisecond precision)
- Log level
- Module name
- Function name
- Line number
- Message and full stack traces for errors
