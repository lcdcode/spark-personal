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
Something like Syncthing is recommended for this task.

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

## Spreadsheet Support
Spreadsheets are currently VIEWABLE ONLY on SPARK Mobile.  A future update may support editing.

Formulas currently supported on mobile (note complex combinations of formulas may not evaluate due to current problems evaluating nested functions):

### Mathematical Functions
- `ABS(value)` - Absolute value
- `FLOOR(value)` - Round down to nearest integer
- `CEILING(value)` / `CEIL(value)` - Round up to nearest integer
- `ROUND(value)` / `ROUND(value, decimals)` - Round to specified decimals
- `TRUNC(value)` - Truncate to integer (remove decimal)
- `SQRT(value)` - Square root
- `POWER(base, exponent)` / `POW(base, exponent)` - Power/exponentiation
- `MOD(value, divisor)` - Modulo (remainder after division)

### Statistical Functions
- `SUM(range)` - Sum of values
- `AVERAGE(range)` - Average of values
- `MIN(range)` - Minimum value
- `MAX(range)` - Maximum value
- `COUNT(range)` - Count of values
- `MEDIAN(range)` - Median value

### Logical Functions
- `IF(condition, true_value, false_value)` - Conditional evaluation
- `AND(condition1, condition2, ...)` - Logical AND
- `OR(condition1, condition2, ...)` - Logical OR
- `NOT(condition)` - Logical NOT

### Date/Time Functions
- `TODAY()` - Current date (numeric timestamp)
- `NOW()` - Current date and time (numeric timestamp)
- `DATE(timestamp)` - Convert timestamp to date string
- `TIME(timestamp)` - Convert timestamp to time string (HH:MM:SS)

### Constants
- `PI()` or `PI` - Mathematical constant π (3.14159...)
- `E()` or `E` - Mathematical constant e (2.71828...)

### Operators
- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `=`, `<>`, `<`, `>`, `<=`, `>=`
- Cell references: `A1`, `B2`, etc.
- Ranges: `A1:A10`, `B1:C5`, etc.
