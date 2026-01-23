# Installing SPARK Mobile

## Latest Version

**sparkmobile-0.2-arm64-v8a-debug.apk** (23 MB)

Version 0.2 includes:
- Full Notes functionality (create, edit, delete, search)
- Full Snippets functionality with language support
- Spreadsheets viewer
- App icon
- Dark theme optimized for mobile

## Installation

### Method 1: ADB (Recommended)

```bash
# From the spark-mobile directory
adb install -r bin/sparkmobile-0.2-arm64-v8a-debug.apk
```

### Method 2: File Transfer

1. Copy the APK to your device:
   ```bash
   adb push bin/sparkmobile-0.2-arm64-v8a-debug.apk /sdcard/Download/
   ```

2. On your device:
   - Open Files app
   - Navigate to Downloads
   - Tap the APK file
   - Allow installation from unknown sources if prompted
   - Tap "Install"

### Method 3: Direct Copy

1. Copy `bin/sparkmobile-0.2-arm64-v8a-debug.apk` to your device via USB
2. Use your device's file manager to locate and install it

## First Run

When you first launch SPARK Mobile:

1. The app will create a database at `/data/data/org.spark.sparkmobile/files/spark.db`
2. Start by adding some notes or snippets
3. All data is stored locally on your device

## Permissions

SPARK Mobile requests:
- **Storage**: To read/write the database file
- No network permissions (fully offline)
- No location or camera access

## Syncing with Desktop

To use the same database on both desktop and mobile:

### Option 1: Manual Sync

1. On device, locate database:
   ```bash
   adb pull /data/data/org.spark.sparkmobile/files/spark.db ./mobile_spark.db
   ```

2. Copy to desktop app:
   ```bash
   cp mobile_spark.db ~/.spark/spark.db  # Adjust path as needed
   ```

### Option 2: Cloud Sync (Future)

A cloud sync feature is planned for future versions to automatically sync between devices.

## Troubleshooting

### App Won't Install

- Make sure you have "Install from Unknown Sources" enabled
- Check that you have enough storage space (30+ MB free)
- Try uninstalling any previous version first

### App Crashes on Start

- Check logcat for errors:
  ```bash
  adb logcat | grep python
  ```

- Database permissions issue? Try clearing app data:
  ```bash
  adb shell pm clear org.spark.sparkmobile
  ```

### Can't See My Data

- The app creates a new database on first run
- To import existing data, you need to manually copy the database file (see Syncing above)

## Updating

To update to a newer version:

```bash
adb install -r bin/sparkmobile-0.X-arm64-v8a-debug.apk
```

The `-r` flag preserves your data when upgrading.

## Uninstalling

```bash
adb uninstall org.spark.sparkmobile
```

Or use your device's Settings > Apps > SPARK Mobile > Uninstall

## System Requirements

- **Android**: 5.0 (Lollipop) or higher
- **Architecture**: ARM64-v8a (most modern devices)
- **Storage**: 30 MB for app + database
- **RAM**: 100 MB minimum

## Development

To test on desktop before installing on device:

```bash
cd spark-mobile
pip install kivy
python3 main.py
```

This creates a test database in `data/spark.db` for desktop testing.
