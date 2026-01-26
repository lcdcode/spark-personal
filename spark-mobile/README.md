# SPARK Mobile

## NOTE: UPON FIRST INSTALLATION BEFORE LAUNCHING, Create the folder Documents/SPARK/ and give SPARK Mobile a storage scope to it!

Mobile-first version of SPARK Personal for Android and iOS.

## Features

- **Database Compatible**: Uses the same SQLite schema as the desktop app
- **Touch-First UI**: Designed for mobile interaction from the ground up
- **Kivy Framework**: Native mobile support with proven Android deployment

## Database Compatibility

The mobile app shares the same database format with the desktop app:

- **Notes**: Hierarchical note-taking with parent/child relationships
- **Snippets**: Code snippets with syntax highlighting and language tags
- **Spreadsheets**: Spreadsheet data with formula support

You can sync your database file between desktop and mobile apps.

## Building for Android

```bash
# Install buildozer (first time only)
pip install buildozer

# Build APK
buildozer android debug

# Deploy to connected device
buildozer android deploy run
```

## Testing on Desktop

You can test the mobile UI on desktop before building:

```bash
pip install kivy
python main.py
```

## Project Structure

```
spark-mobile/
├── main.py           # Main application entry point
├── database.py       # Database layer (shared with desktop)
├── buildozer.spec    # Android build configuration
├── assets/           # Images, icons, etc.
└── data/             # Local database (testing only)
```

## Next Steps

1. Build and test basic APK
2. Add UI components for Notes, Snippets, Spreadsheets
3. Implement search and filtering
4. Add sync capabilities
