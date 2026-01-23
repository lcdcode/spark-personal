# SPARK Mobile Features

## Implemented Features

### Notes
- ✓ Create, edit, and delete notes
- ✓ Search notes by title or content
- ✓ Hierarchical organization (parent/child support)
- ✓ Full-text editor with multiline support
- ✓ Real-time search as you type

### Snippets
- ✓ Create, edit, and delete code snippets
- ✓ Language selection (16+ languages supported)
- ✓ Tag support for organization
- ✓ Search by title, code, or tags
- ✓ Monospace font for code display

### Spreadsheets
- ✓ Create and delete spreadsheets
- ✓ View cell data
- ✓ JSON-based storage (compatible with desktop app)
- Note: Full editing is available in the desktop app

## UI Features

- **Dark Theme**: Easy on the eyes for mobile viewing
- **Touch-Optimized**: Large touch targets and swipe-friendly
- **Tabbed Navigation**: Easy switching between Notes/Snippets/Sheets
- **Popup Dialogs**: Full-screen editors for focused work
- **Search**: Real-time filtering in Notes and Snippets

## Database Compatibility

The mobile app uses the **exact same database format** as the desktop SPARK app:

- Same SQLite schema
- Same table structures
- You can copy `spark.db` between desktop and mobile
- All CRUD operations work identically

## Supported Languages (Snippets)

python, javascript, java, c, cpp, go, rust, ruby, php, swift, kotlin, typescript, bash, sql, html, css

## APK Size

- **~23MB** - Much smaller than PySide6 version (142MB)
- Includes Python 3, Kivy, and all dependencies

## Platform Support

- **Android**: Tested on ARM64-v8a (Android 5.0+)
- **iOS**: Buildozer supports iOS (requires macOS to build)
- **Desktop**: Can run on Linux/Windows/macOS for testing

## Performance

- Fast startup (~2 seconds on modern devices)
- Smooth scrolling with hundreds of items
- Instant search results
- Low memory usage

## Future Enhancements

Potential features for future versions:

1. **Sync**: Cloud sync between devices
2. **Export**: Export notes/snippets to Markdown/JSON
3. **Themes**: Light theme option
4. **Syntax Highlighting**: Color-coded snippets
5. **Rich Text**: Markdown rendering in notes
6. **Attachments**: Image support in notes
7. **Backup**: Automatic database backups
8. **Spreadsheet Editing**: Full cell editing on mobile
9. **Formula Support**: Calculator-style formulas
10. **Widgets**: Android home screen widgets

## Testing

### On Desktop

```bash
cd spark-mobile
pip install kivy
python3 main.py
```

### On Device

```bash
cd spark-mobile
./build.sh
adb install -r bin/sparkmobile-0.2-arm64-v8a-debug.apk
```

## Known Limitations

1. Spreadsheets are view-only on mobile (edit on desktop)
2. No syntax highlighting yet (planned)
3. No Markdown rendering (planned)
4. Single database per installation (no multiple workspaces)

## Architecture

```
main.py                 # App entry point, database initialization
database.py             # SQLite operations (shared with desktop)
notes_screen.py         # Notes UI and logic
snippets_screen.py      # Snippets UI and logic
spreadsheets_screen.py  # Spreadsheets UI and logic
```

All screens follow the same pattern:
1. List view with search/add buttons
2. Popup dialogs for create/edit
3. Database operations for persistence
4. Touch-optimized buttons and inputs
