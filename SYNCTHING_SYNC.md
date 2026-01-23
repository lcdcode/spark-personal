# SPARK Syncthing Bidirectional Sync

## Overview

Both SPARK desktop and mobile apps now support **automatic database change detection** for seamless bidirectional sync via Syncthing.

## How It Works

### Desktop App
- Uses `QFileSystemWatcher` to monitor the database file
- Detects when Syncthing syncs changes from mobile
- Shows a dialog prompt: "Database has been modified externally. Reload?"
- Saves any unsaved changes before reloading
- Refreshes all widgets (Notes, Spreadsheets, Snippets) with new data

### Mobile App
- Checks database file modification time every 5 seconds
- Detects when Syncthing syncs changes from desktop
- Shows a popup: "Database changed externally. Reload?"
- Saves pending changes before reloading
- Refreshes all screens with new data

## Setup

### 1. Configure Database Location

**Desktop:**
- Database: `~/.spark/spark.db` (Linux/Mac) or `%USERPROFILE%\.spark\spark.db` (Windows)

**Mobile (v2.6+):**
- Preferred: `/storage/emulated/0/Documents/SPARK/spark.db`
- Fallback: `/storage/emulated/0/Download/SPARK/spark.db`
- Check logs after install to see which location was used

### 2. Configure Syncthing

**On Desktop:**
1. Add folder: `~/.spark` (or wherever your database is)
2. Share with your mobile device
3. Set sync to bidirectional

**On Mobile:**
1. Add folder: `/storage/emulated/0/Documents/SPARK` or `/storage/emulated/0/Download/SPARK`
2. Share with your desktop
3. Set sync to bidirectional

### 3. Sync Settings (Recommended)

For best experience:
- **Watch for Changes**: Enabled
- **Rescan Interval**: 60 seconds (or less)
- **File Pull Order**: Alphabetic
- **Versioning**: File Versioning (keeps backups of changed files)

## Usage Workflow

### Mobile → Desktop Sync

1. Edit data on mobile app (notes, spreadsheets, or snippets)
2. Mobile auto-saves changes to database
3. Syncthing detects database change and syncs to desktop
4. Desktop app detects file change and shows prompt
5. Click "Yes" to reload database
6. Desktop now shows mobile changes

### Desktop → Mobile Sync

1. Edit data on desktop app
2. Desktop auto-saves changes (configurable interval, default 5 minutes)
3. Syncthing detects database change and syncs to mobile
4. Mobile app detects file change (checked every 5 seconds)
5. Shows popup to reload
6. Tap "Reload" to see desktop changes

## Important Notes

### Conflict Resolution

If both devices are editing simultaneously:
- **Syncthing** handles file conflicts by creating `.sync-conflict` files
- The most recent change "wins" (last-write-wins)
- Check for `.sync-conflict-*` files in your SPARK folder
- If conflicts occur, manually merge data from conflict files

### Best Practices

1. **Wait for sync to complete** before switching devices
2. **Accept reload prompts** when they appear
3. **Save your work** before closing apps (both do this automatically)
4. **Check Syncthing status** before major edits
5. **Use versioning** in Syncthing to keep file history

### Auto-Save Behavior

**Desktop:**
- Auto-saves every 5 minutes (configurable in Settings)
- Also saves when switching between items
- Saves on app close

**Mobile:**
- Auto-saves immediately after any edit
- No configurable interval (always immediate)
- Saves on app pause/close

## Troubleshooting

### Desktop Not Detecting Changes

1. Check Syncthing is running and synced
2. Verify database path: File > Settings > Database Path
3. Check logs for file watcher errors
4. Restart SPARK desktop app

### Mobile Not Detecting Changes

1. Check Syncthing has permission to access the folder
2. Verify database location: Look for "SPARK: ✓ SUCCESS! Database at:" in logs
   ```bash
   adb logcat | grep "SPARK: ✓ SUCCESS"
   ```
3. Ensure app has storage permissions
4. Restart SPARK mobile app

### Changes Not Syncing

1. Open Syncthing web UI on both devices
2. Check folder status - should show "Up to Date"
3. Check for errors in Syncthing logs
4. Verify folders are shared between devices
5. Check if database file is being ignored (.stignore file)

### Reload Prompt Not Appearing

**Desktop:**
- The file watcher may need to be re-initialized
- Restart the app
- Check that database file exists and is accessible

**Mobile:**
- The app may be paused (Android background restrictions)
- The 5-second check interval may have missed the change
- Close and reopen the spreadsheet/note to manually refresh

## Technical Details

### Desktop Implementation
- **File:** [spark/main_window.py](spark/main_window.py:130-135)
- **Monitor:** `QFileSystemWatcher` on database file
- **Trigger:** `fileChanged` signal
- **Handler:** `on_database_changed()` method
- **Reload:** `reload_database()` method

### Mobile Implementation
- **File:** [spark-mobile/main.py](spark-mobile/main.py:91-93)
- **Monitor:** `os.path.getmtime()` every 5 seconds
- **Trigger:** Kivy Clock scheduled interval
- **Handler:** `check_database_changes()` method
- **Reload:** `reload_database()` method

## Versions

- **Desktop:** Database change detection added in current version
- **Mobile:** Database change detection added in v2.3, Documents folder support in v2.6

## Performance Impact

- **Desktop:** Negligible (OS-level file watching)
- **Mobile:** Minimal (one file stat every 5 seconds)
- **Battery:** No significant impact on mobile battery life
- **Network:** Depends on Syncthing configuration and database size

## Security

- Database file permissions: 0600 (user read/write only)
- No cloud services involved (fully peer-to-peer)
- Syncthing uses TLS encryption for device-to-device sync
- Data stays on your devices only
