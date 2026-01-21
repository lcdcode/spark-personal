#!/bin/bash
# SPARK Personal launcher script with virtual environment support and dependency checking
#
# Usage:
#   ./run.sh                    - Normal start (checks dependencies once)
#   ./run.sh --skip-deps-check  - Skip dependency check entirely
#
# To reset dependency check:
#   rm .system_deps_checked

set -e  # Exit on error

VENV_DIR="venv"
SYSTEM_DEPS_CHECKED=".system_deps_checked"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check for Qt system dependencies on Linux
check_system_dependencies() {
    if [ "$(uname)" != "Linux" ]; then
        return 0  # Skip check on non-Linux systems
    fi

    # Only check once per installation
    if [ -f "$SYSTEM_DEPS_CHECKED" ]; then
        return 0
    fi

    echo "Checking system dependencies..."

    MISSING_DEPS=()

    # Try multiple methods to check for libraries
    check_lib() {
        local lib=$1

        # Method 1: Use ldconfig if available (fastest)
        if command -v ldconfig >/dev/null 2>&1; then
            # Strip .so and search for the library name
            local libname="${lib%.so}"
            if ldconfig -p 2>/dev/null | grep -q "$libname"; then
                return 0
            fi
        fi

        # Method 2: Direct filesystem check in common paths
        # Limit depth to avoid slow searches, check only top-level lib dirs
        for dir in /usr/lib/x86_64-linux-gnu /usr/lib64 /usr/lib /lib/x86_64-linux-gnu /lib64 /lib; do
            if [ -d "$dir" ]; then
                if find "$dir" -maxdepth 1 -name "${lib}*" 2>/dev/null | grep -q .; then
                    return 0
                fi
            fi
        done

        return 1
    }

    # Check for common Qt dependencies
    if ! check_lib "libxcb-cursor.so"; then
        MISSING_DEPS+=("libxcb-cursor0")
    fi

    if ! check_lib "libxkbcommon-x11.so"; then
        MISSING_DEPS+=("libxkbcommon-x11-0")
    fi

    if ! check_lib "libxcb-xinerama.so"; then
        MISSING_DEPS+=("libxcb-xinerama0")
    fi

    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}⚠️  Missing System Dependencies${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo
        echo -e "${YELLOW}SPARK Personal requires Qt system libraries that are not installed.${NC}"
        echo
        echo "Missing libraries:"
        for dep in "${MISSING_DEPS[@]}"; do
            echo "  - $dep"
        done
        echo
        echo -e "${GREEN}To fix this, run:${NC}"
        echo

        # Detect Linux distribution and suggest appropriate command
        if [ -f /etc/debian_version ]; then
            echo "  sudo apt update"
            echo "  sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libdbus-1-3 libegl1 libfontconfig1 libgl1"
        elif [ -f /etc/fedora-release ] || [ -f /etc/redhat-release ]; then
            echo "  sudo dnf install -y xcb-util-cursor xcb-util-image xcb-util-keysyms xcb-util-renderutil xcb-util-wm libxkbcommon-x11 mesa-libEGL fontconfig"
        elif [ -f /etc/arch-release ]; then
            echo "  sudo pacman -S --needed xcb-util-cursor xcb-util-image xcb-util-keysyms xcb-util-renderutil xcb-util-wm libxkbcommon-x11 mesa fontconfig"
        else
            echo "  See SYSTEM_DEPENDENCIES.md for your distribution"
        fi

        echo
        echo -e "${YELLOW}For detailed instructions, see: SYSTEM_DEPENDENCIES.md${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo

        read -p "Would you like to continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        else
            # User chose to continue - DON'T mark as checked yet
            # We'll only mark it if SPARK starts successfully
            echo -e "${YELLOW}Continuing. Will check again if SPARK fails to start.${NC}"
        fi
    else
        echo -e "${GREEN}✓ System dependencies OK${NC}"
        touch "$SYSTEM_DEPS_CHECKED"
    fi
}

# Check system dependencies first (can be skipped with --skip-deps-check)
if [[ "$1" != "--skip-deps-check" ]]; then
    check_system_dependencies
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Setting up SPARK Personal for first time..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"

    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        echo "Please ensure Python 3.8+ is installed"
        exit 1
    fi

    echo "Installing Python dependencies..."
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip --quiet
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Failed to install dependencies${NC}"
        exit 1
    fi

    echo
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
else
    # Activate existing virtual environment
    source "$VENV_DIR/bin/activate"
fi

echo "Starting SPARK Personal..."
echo

# Run with error handling for Qt platform issues
if python -m spark.main 2>&1; then
    # SPARK started successfully!
    # Only now mark dependencies as checked (if on Linux and not already checked)
    if [ "$(uname)" = "Linux" ] && [ ! -f "$SYSTEM_DEPS_CHECKED" ]; then
        touch "$SYSTEM_DEPS_CHECKED"
    fi
    exit 0
else
    EXIT_CODE=$?

    # SPARK failed to start
    echo
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  SPARK Personal failed to start${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "${YELLOW}This is likely due to missing Qt system libraries.${NC}"
    echo
    echo -e "${GREEN}To fix this, install the required system packages:${NC}"
    echo

    if [ -f /etc/debian_version ]; then
        echo "  sudo apt update"
        echo "  sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1"
    elif [ -f /etc/fedora-release ] || [ -f /etc/redhat-release ]; then
        echo "  sudo dnf install -y xcb-util-cursor libxkbcommon-x11"
    else
        echo "  See SYSTEM_DEPENDENCIES.md for your distribution"
    fi

    echo
    echo -e "${YELLOW}For detailed troubleshooting, see: SYSTEM_DEPENDENCIES.md${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Ensure we check dependencies again next time since it failed
    rm -f "$SYSTEM_DEPS_CHECKED"

    exit $EXIT_CODE
fi
