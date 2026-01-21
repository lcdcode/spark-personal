# System Dependencies for SPARK Personal

SPARK Personal requires certain system libraries to be installed, particularly for the Qt GUI framework. This guide covers all platform-specific dependencies.

## Linux Dependencies

### Required System Packages

PyQt6 requires several system libraries to function properly. Install them before running SPARK Personal:

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libdbus-1-3 \
    libxcb-xfixes0 \
    libegl1 \
    libfontconfig1 \
    libgl1
```

#### Fedora/RHEL/CentOS

```bash
sudo dnf install -y \
    python3 \
    python3-pip \
    python3-virtualenv \
    xcb-util-cursor \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    xcb-util-wm \
    libxkbcommon-x11 \
    mesa-libEGL \
    fontconfig \
    mesa-libGL
```

#### Arch Linux

```bash
sudo pacman -S --needed \
    python \
    python-pip \
    python-virtualenv \
    libxcb \
    xcb-util-cursor \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    xcb-util-wm \
    libxkbcommon-x11 \
    mesa \
    fontconfig
```

#### openSUSE

```bash
sudo zypper install -y \
    python3 \
    python3-pip \
    python3-virtualenv \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    Mesa-libEGL1 \
    fontconfig
```

### Common Qt Platform Plugin Errors

#### Error: "Could not load the Qt platform plugin 'xcb'"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install libxcb-cursor0 libxcb-xinerama0

# Fedora/RHEL
sudo dnf install xcb-util-cursor

# Arch
sudo pacman -S xcb-util-cursor
```

#### Error: "xcb-cursor0 or libxcb-cursor0 is needed"

**Solution:**
```bash
# Ubuntu/Debian (22.04+)
sudo apt install libxcb-cursor0

# Ubuntu/Debian (20.04 and older)
sudo apt install libxcb-cursor-dev

# Fedora/RHEL
sudo dnf install xcb-util-cursor
```

#### Error: "libxkbcommon-x11.so.0: cannot open shared object file"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install libxkbcommon-x11-0

# Fedora/RHEL
sudo dnf install libxkbcommon-x11
```

## macOS Dependencies

macOS usually has all required dependencies. If you encounter issues:

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Qt dependencies are included with PyQt6
```

## Windows Dependencies

Windows typically doesn't require additional system dependencies. PyQt6 includes everything needed.

If you encounter issues:
1. Ensure you have the latest Visual C++ Redistributable:
   - Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Ensure Windows is up to date

## Headless/Server Environments

If running on a headless server without X11:

```bash
# Install virtual display
sudo apt install xvfb

# Run with virtual display
xvfb-run ./run.sh
```

Or use the offscreen platform:
```bash
export QT_QPA_PLATFORM=offscreen
./run.sh
```

## Docker/Container Environments

For Docker or containerized environments, include these in your Dockerfile:

```dockerfile
FROM python:3.11-slim

# Install Qt dependencies
RUN apt-get update && apt-get install -y \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libdbus-1-3 \
    libxcb-xfixes0 \
    libegl1 \
    libfontconfig1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# For headless operation
ENV QT_QPA_PLATFORM=offscreen

# Copy and run SPARK
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "-m", "spark.main"]
```

## Verification

After installing system dependencies, verify Qt works:

```bash
# Create and activate venv
python3 -m venv test_venv
source test_venv/bin/activate

# Install PyQt6
pip install PyQt6

# Test Qt
python -c "from PyQt6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); print('Qt works!')"

# Cleanup
deactivate
rm -rf test_venv
```

If this prints "Qt works!" you're all set!

## Troubleshooting

### Check Missing Libraries

Find what libraries are missing:

```bash
# Install ldd if not available
sudo apt install binutils

# Check PyQt6 dependencies
python3 -c "from PyQt6 import QtCore; print(QtCore.__file__)" | xargs dirname | xargs -I {} find {} -name "*.so*" | head -1 | xargs ldd | grep "not found"
```

### Set Qt Platform

If issues persist, try different Qt platforms:

```bash
# Try Wayland
export QT_QPA_PLATFORM=wayland
./run.sh

# Try XCB with debug
export QT_DEBUG_PLUGINS=1
export QT_QPA_PLATFORM=xcb
./run.sh

# Try offscreen (no GUI, for testing)
export QT_QPA_PLATFORM=offscreen
./run.sh
```

### Enable Qt Debug Output

```bash
export QT_DEBUG_PLUGINS=1
export QT_LOGGING_RULES="qt.qpa.*=true"
./run.sh
```

This will show detailed information about what Qt is trying to load.

## Quick Install Scripts

### Ubuntu/Debian One-Liner

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libdbus-1-3 libegl1 libfontconfig1 libgl1 && echo "Dependencies installed successfully!"
```

### Fedora/RHEL One-Liner

```bash
sudo dnf install -y python3 python3-pip python3-virtualenv xcb-util-cursor xcb-util-image xcb-util-keysyms xcb-util-renderutil xcb-util-wm libxkbcommon-x11 mesa-libEGL fontconfig && echo "Dependencies installed successfully!"
```

## Summary

**Before running SPARK Personal for the first time:**

1. **Linux**: Install system dependencies (see above for your distro)
2. **macOS**: No extra dependencies needed
3. **Windows**: No extra dependencies needed

**If you get Qt errors:**
- Check the error message
- Install missing libraries from the lists above
- Use the verification script to test

---

**Most common fix for Linux users:**
```bash
sudo apt install libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0
```

Then run `./run.sh` again.
