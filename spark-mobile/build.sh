#!/bin/bash
# Build SPARK Mobile APK for Android

set -e

echo "=========================================="
echo " Building SPARK Mobile for Android"
echo "=========================================="
echo ""

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "Error: buildozer not found"
    echo "Install with: pip install buildozer"
    exit 1
fi

# Clean previous builds if requested
if [ "$1" == "clean" ]; then
    echo "Cleaning previous builds..."
    rm -rf .buildozer
    rm -f *.apk
    echo ""
fi

# Build the APK
echo "Starting build (this may take 10-15 minutes on first build)..."
echo ""

buildozer android debug

# Check for APK
APK=$(find bin -name "*.apk" 2>/dev/null | head -1)
if [ -n "$APK" ]; then
    echo ""
    echo "=========================================="
    echo " ✓ BUILD SUCCESSFUL"
    echo "=========================================="
    echo ""
    ls -lh "$APK"
    echo ""
    echo "APK: $APK"
    echo ""
    echo "To install on device:"
    echo "  adb install -r $APK"
else
    echo ""
    echo "=========================================="
    echo " ✗ BUILD FAILED"
    echo "=========================================="
    echo ""
    echo "Check the output above for errors"
    exit 1
fi
