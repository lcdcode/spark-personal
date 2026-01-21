#!/bin/bash
# Build with Python 3.11 using NDK r27c for proper libc++ compatibility

set -e

export VIRTUAL_ENV="/home/user/code/spark/venv"
export PATH="$VIRTUAL_ENV/bin:$PATH"
cd /home/user/code/spark

echo "=========================================="
echo " SPARK Android - Python 3.11 + NDK r27c"
echo "=========================================="
echo ""

# Clean start
rm -rf .buildozer deployment buildozer.spec SPARK-*.apk

# Install spark package into venv so it's available in site-packages
echo "Installing spark package into virtualenv..."
venv/bin/pip install -e . --quiet
echo "✓ spark package installed"
echo ""

# Start the build in background
echo "[1/2] Starting build with NDK r27c..."
venv/bin/pyside6-android-deploy \
    --config-file pysidedeploy.spec \
    --ndk-path ~/.pyside6_android_deploy/android-ndk/android-ndk-r27c \
    --sdk-path ~/.pyside6_android_deploy/android-sdk \
    --verbose \
    --force 2>&1 | tee /tmp/build_ndk27.log &

BUILD_PID=$!
echo "Build PID: $BUILD_PID"

# Monitor for p4a clone and patch to Python 3.11
echo ""
echo "[2/2] Monitoring for python-for-android clone..."

PATCHED=false
BUILDOZER_PATCHED=false
for i in {1..600}; do
    # Check if p4a recipes exist
    if [ -f ".buildozer/android/platform/python-for-android/pythonforandroid/recipes/python3/__init__.py" ] && [ "$PATCHED" = "false" ]; then
        echo ""
        echo "✓ python-for-android cloned! Applying Python 3.11 patch..."
        sleep 1

        # Patch python3 recipe to 3.11.11
        sed -i "s/version = '3.14.0'/version = '3.11.11'/" \
            .buildozer/android/platform/python-for-android/pythonforandroid/recipes/python3/__init__.py
        sed -i '/if _p_version.minor >= 14:/,+1d' \
            .buildozer/android/platform/python-for-android/pythonforandroid/recipes/python3/__init__.py

        # Patch hostpython3 recipe to 3.11.11
        sed -i "s/version = '3.14.0'/version = '3.11.11'/" \
            .buildozer/android/platform/python-for-android/pythonforandroid/recipes/hostpython3/__init__.py
        sed -i '/if _p_version.minor >= 14:/,+1d' \
            .buildozer/android/platform/python-for-android/pythonforandroid/recipes/hostpython3/__init__.py

        # Verify patches
        if grep -q "3.11.11" .buildozer/android/platform/python-for-android/pythonforandroid/recipes/python3/__init__.py; then
            echo "✓ Successfully patched to Python 3.11.11!"
            echo ""
            echo "Build continuing with:"
            echo "  - Python: 3.11.11 (compatible with PySide6)"
            echo "  - NDK: r27c (matches PySide6 wheel libc++)"
            echo ""
            echo "This should fix the libc++ symbol error!"
            PATCHED=true
        else
            echo "✗ Patch verification failed!"
            kill $BUILD_PID 2>/dev/null || true
            exit 1
        fi
    fi

    # Check if buildozer.spec exists and patch it to include spark package
    if [ -f "buildozer.spec" ] && [ "$BUILDOZER_PATCHED" = "false" ]; then
        echo ""
        echo "✓ buildozer.spec found! Adding spark package..."

        # Add spark directory to source.include_exts and source.include_patterns
        if ! grep -q "source.include_patterns = spark/\*\*" buildozer.spec; then
            # Find the line with source.include_exts and add our patterns after it
            sed -i '/^source.include_exts = /a source.include_patterns = spark/**' buildozer.spec
            echo "✓ Added spark package to buildozer.spec"
            BUILDOZER_PATCHED=true
        fi
    fi

    # Check if build is still running
    if ! kill -0 $BUILD_PID 2>/dev/null; then
        if [ "$PATCHED" = "false" ]; then
            echo "Build ended before we could patch"
            exit 1
        else
            break
        fi
    fi

    # Progress indicator
    if [ $((i % 30)) -eq 0 ] && [ "$PATCHED" = "false" ]; then
        echo "Still waiting for clone... ($i seconds)"
    fi

    sleep 1
done

# Wait for build to complete
echo ""
echo "Waiting for build to complete (this takes 10-20 minutes)..."
wait $BUILD_PID
BUILD_RESULT=$?

echo ""
echo "=========================================="
if [ $BUILD_RESULT -eq 0 ]; then
    echo " ✓ BUILD SUCCESSFUL"
    echo "=========================================="
    echo ""

    APK=$(find . -name "*.apk" 2>/dev/null | head -1)
    if [ -n "$APK" ]; then
        ls -lh "$APK"
        echo ""
        echo "APK: $APK"
        echo ""
        echo "This build uses:"
        echo "  ✓ Python 3.11.11 (PySide6 compatible)"
        echo "  ✓ NDK r27c (matches PySide6 wheel expectations)"
        echo "  ✓ libc++ from r27c (should fix symbol errors)"
        echo ""
        echo "Try installing this APK - the libc++ crash should be resolved!"
    else
        echo "⚠ Build reported success but no APK found"
    fi
else
    echo " ✗ BUILD FAILED (exit code: $BUILD_RESULT)"
    echo "=========================================="
    echo ""
    echo "Check /tmp/build_ndk27.log for details"
    exit $BUILD_RESULT
fi
