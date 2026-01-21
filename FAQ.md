# SPARK Personal - Frequently Asked Questions

## Installation & Setup

### Q: The launcher keeps warning about missing dependencies, but SPARK works fine. How do I stop the warnings?

**A:** The launcher is smart - it will **automatically** stop checking once SPARK starts successfully:

**Just run normally:**
```bash
./run.sh
# When prompted, press 'y' to continue
# If SPARK starts successfully, it won't check again
# If SPARK fails, it will check again next time (to help you debug)
```

**Alternative options:**

**Option 1: Skip the check for this run only**
```bash
./run.sh --skip-deps-check
```

**Option 2: Manually mark dependencies as OK**
```bash
touch .system_deps_checked
./run.sh
```

**Note:** The check is designed to help catch missing dependencies early. Once SPARK runs successfully once, the check is automatically disabled.

### Q: Where does SPARK store my data?

**A:** All data is stored in `~/.spark_personal/`:
- `spark.db` - Your notes, spreadsheets, and snippets
- `config.yaml` - Settings
- `images/` - Images from notes
- `backups/` - Automatic backups

NOTHING is stored external to your computer unless you back up your db file somewhere. (Backup recommended!!)

### Q: How do I uninstall SPARK Personal?

**A:**
```bash
# Remove application (keeps your data)
cd /path/to/spark
rm -rf venv .system_deps_checked

# Remove your data (CAUTION: Permanent deletion!)
rm -rf ~/.spark_personal

# Remove the entire project
cd ..
rm -rf spark
```

### Q: Can I use SPARK without installing system dependencies?

**A:** On Linux, you need Qt system libraries. If the dependency check fails but SPARK works, the libraries might be installed in non-standard locations. Use `./run.sh --skip-deps-check` or press 'y' when prompted.

### Q: Does SPARK work offline?

**A:** Yes! SPARK is completely offline and never connects to the internet.

---

## Features & Usage

### Q: How do I search across all my notes?

**A:** Use the search bar at the bottom (or press Ctrl+F). Search works in the current tab:
- In **Notes** tab: Searches note titles and content
- In **Code Snippets** tab: Searches titles, code, and tags

### Q: Can I export my notes?

**A:** Currently, notes are stored in SQLite. Export functionality is planned for a future release. You can backup the entire database using File → Backup Manager.

### Q: What Markdown features are supported?

**A:** SPARK supports standard Markdown:
- Headers: `# H1`, `## H2`, etc.
- **Bold**: `**text**`
- *Italic*: `*text*`
- Lists: `- item` or `1. item`
- Checkboxes `[ ]` and `[x]`
- Code: `` `code` `` or ``` for blocks
- Links: `[text](url)`
- Images: `![alt](path)`

### Q: What spreadsheet functions are available?

**A:** Currently supported:
- `SUM(a,b,c,...)` - Add numbers
- `AVERAGE(a,b,c,...)` - Calculate average
- `IF(condition,true,false)` - Conditional
- `TODAY()` - Current date
- `NOW()` - Current date and time
- `DATE()` - Show a date/time in YYYY-MM-DD format
- `AND(True,True)`, `OR(False,False)`, `NOT(True)` - Logic

Most common arithmetic operators like `+`, `-`, `*`, `/`, `^`, `//`, etc.

Cell references work like Excel: `A1`, `B2`, etc.

### Q: How do I add images to notes?

**A:** Image support framework is in place. Currently, you can reference images using Markdown syntax: `![description](image.png)` (Note that all images are stored in an images/ folder in your SPARK user data directory.)

### Q: Can I sync SPARK across multiple computers?

**A:** Not currently built-in. You can manually sync the `~/.spark_personal/` directory to somewhere else you trust using a safe backup tool like Syncthing - **WARNING!** As of version 1.0.0, your data is NOT encrypted, so BE CAREFUL WHERE YOU BACK UP TO! Encryption is a planned feature, but for now, do not back up to shared locations or most cloud services!

---

## Backups

### Q: How do automatic backups work?

**A:**
- Enabled by default (every 24 hours)
- Keeps the 10 most recent backups
- Stored in `~/.spark_personal/backups/` (or custom location)
- Configure in File → Backup Manager

### Q: How do I restore from a backup?

**A:**
1. File → Backup Manager
2. Select a backup from the list
3. Click "Restore Selected"
4. Restart SPARK

Or manually:
```bash
cp ~/.spark_personal/backups/spark_backup_YYYYMMDD_HHMMSS.db ~/.spark_personal/spark.db
```

### Q: Can I change the backup location?

**A:** Yes! File → Backup Manager → Change button. Choose any directory you want.

---

## Customization

### Q: How do I change the theme?

**A:** File → Settings → Select theme → Save → **Restart SPARK**

Or via View menu for quick switching.

### Q: Can I change fonts?

**A:** Yes! File → Settings → Font Family and Font Size → Save → Restart

### Q: How do I disable autosave?

**A:** File → Settings → Uncheck "Autosave Enabled" or adjust interval → Save

### Q: Can I customize keyboard shortcuts?

**A:** Currently, shortcuts are fixed:
- `Ctrl+S` - Save
- `Ctrl+F` - Search
- `Ctrl+Q` - Quit

Custom shortcuts planned for future release.

---

## Troubleshooting

### Q: SPARK won't start - "Qt platform plugin" error

**A:** Install Qt system libraries (Linux only):
```bash
# Ubuntu/Debian
sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0

# Fedora/RHEL
sudo dnf install -y xcb-util-cursor libxkbcommon-x11
```

See [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md) for details.

### Q: My data disappeared!

**A:** Check if you're looking in the right place:
```bash
ls -la ~/.spark_personal/spark.db
```

If the file exists but appears empty, restore from backup (File → Backup Manager).

### Q: Formulas aren't calculating

**A:** Click the **Recalculate** button. Make sure formulas start with `=`.

### Q: Search isn't finding my content

**A:**
1. Make sure you're in the right tab (Notes or Snippets)
2. Try a single keyword
3. Check spelling

### Q: The app is slow

**A:**
- Check database size: `ls -lh ~/.spark_personal/spark.db`
- Large databases (>100MB) may be slower
- Consider archiving old notes

---

## Development

### Q: Can I contribute to SPARK Personal?

**A:** Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Q: What Python version do I need?

**A:** Python 3.8 or higher. Python 3.10+ recommended.

### Q: Can I add new features?

**A:** Absolutely! SPARK has a modular architecture. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add:
- New themes
- Spreadsheet functions
- Widget tabs
- Database tables

### Q: Is there an API?

**A:** Not currently, but the database is SQLite and can be accessed directly if needed.

---

## Platform-Specific

### Q: Does SPARK work on macOS?

**A:** Yes! Install Python 3.8+ via Homebrew, then run `./run.sh`.

### Q: Does SPARK work on Windows?

**A:** Yes! Use `run.bat` instead of `run.sh`.

### Q: Does SPARK work on ARM/M1 Macs?

**A:** Yes, as long as you have Python 3.8+ and PyQt6 supports your platform.

### Q: Can I run SPARK on a Raspberry Pi?

**A:** Yes, but you'll need to install system dependencies. See [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md).

### Q: Does SPARK work in Docker?

**A:** Yes! See the Docker example in [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md). You'll need X11 forwarding or use `QT_QPA_PLATFORM=offscreen` for headless operation.

---

## Data & Privacy

### Q: Does SPARK collect any data?

**A:** No. SPARK is completely offline and collects zero data.

### Q: Is my data encrypted?

**A:** Currently no. The SQLite database is unencrypted. Encryption is planned for a future release.

### Q: Can I use SPARK for sensitive information?

**A:** Yes, but:
- Data is stored unencrypted
- Use full-disk encryption (BitLocker, FileVault, LUKS)
- Store backups securely
- Consider encrypting the `~/.spark_personal/` directory

### Q: Where does SPARK phone home to?

**A:** Nowhere. SPARK has no network code and never connects to the internet.

---

## Performance

### Q: What's the maximum database size?

**A:** SQLite can handle databases up to 140TB, but performance may degrade with very large datasets (>1GB).

### Q: How many notes can I store?

**A:** Practically unlimited. Tested with 10,000+ notes with good performance.

### Q: Does SPARK use a lot of RAM?

**A:** No. Typical usage is 50-150MB.

---

## Miscellaneous

### Q: What does "SPARK" stand for?

**A:** It's just a catchy name! ⚡

### Q: Is SPARK open source?

**A:** Yes! MIT License. See [LICENSE](LICENSE).

### Q: Can I use SPARK for commercial purposes?

**A:** Yes! MIT License allows commercial use.

### Q: Who made SPARK?

**A:** Built with Python and PyQt6. See [README.md](README.md) for credits.

### Q: Is there a mobile version?

**A:** Not currently. Mobile support is on the roadmap.

### Q: Can I rename the application?

**A:** Yes, it's MIT licensed. Fork and customize as you like!

---

## Getting More Help

- **Installation Issues**: [INSTALL.md](INSTALL.md)
- **System Dependencies**: [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Feature Documentation**: [README.md](README.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Report a Bug**: GitHub Issues

---

**Still have questions?** Check the documentation files or open an issue on GitHub!
