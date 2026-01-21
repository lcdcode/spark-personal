#!/bin/bash
# SPARK Personal launcher script with automatic setup and dependency management
#
# Usage:
#   ./run.sh                    - Normal start (auto-setup if needed)
#   ./run.sh --skip-deps-check  - Skip dependency check entirely
#   ./run.sh --install-deps     - Force install system dependencies
#
# To reset dependency check:
#   rm .system_deps_checked

# Enable error output for debugging
set -o pipefail

VENV_DIR="venv"
SYSTEM_DEPS_CHECKED=".system_deps_checked"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/fedora-release ]; then
        echo "fedora"
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    elif [ -f /etc/arch-release ]; then
        echo "arch"
    else
        echo "unknown"
    fi
}

DISTRO=$(detect_distro)

# Function to install system dependencies automatically
install_system_deps() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Installing System Dependencies${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    case "$DISTRO" in
        debian|ubuntu|linuxmint|pop)
            echo "Detected Debian/Ubuntu-based system"
            echo "Installing Qt dependencies..."
            sudo apt update
            sudo apt install -y \
                python3-venv \
                libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 \
                libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
                libxcb-randr0 libxcb-render-util0 \
                libdbus-1-3 libegl1 libfontconfig1 libgl1
            ;;

        fedora|rhel|centos|rocky|almalinux)
            echo "Detected Fedora/RHEL-based system"
            echo "Installing Qt dependencies..."
            sudo dnf install -y \
                python3-virtualenv \
                xcb-util-cursor xcb-util-image xcb-util-keysyms \
                xcb-util-renderutil xcb-util-wm \
                libxkbcommon-x11 mesa-libEGL fontconfig dbus-libs
            ;;

        arch|manjaro|endeavouros)
            echo "Detected Arch-based system"
            echo "Installing Qt dependencies..."
            sudo pacman -S --needed --noconfirm \
                python-virtualenv \
                xcb-util-cursor xcb-util-image xcb-util-keysyms \
                xcb-util-renderutil xcb-util-wm \
                libxkbcommon-x11 mesa fontconfig
            ;;

        opensuse*|suse)
            echo "Detected openSUSE system"
            echo "Installing Qt dependencies..."
            sudo zypper install -y \
                python3-virtualenv \
                libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 \
                libxcb-icccm4 libxcb-image0 libxcb-keysyms1 \
                libxcb-randr0 libxcb-render-util0 \
                libdbus-1-3 Mesa-libEGL1 fontconfig
            ;;

        *)
            echo -e "${YELLOW}Unknown distribution: $DISTRO${NC}"
            echo "Please install Qt dependencies manually. See SYSTEM_DEPENDENCIES.md"
            return 1
            ;;
    esac

    if [ $? -eq 0 ]; then
        echo
        echo -e "${GREEN}✓ System dependencies installed successfully${NC}"
        touch "$SYSTEM_DEPS_CHECKED"
        return 0
    else
        echo -e "${RED}✗ Failed to install system dependencies${NC}"
        return 1
    fi
}

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
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo

        read -p "Would you like to install them automatically? (Y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            echo
            echo -e "${YELLOW}Manual installation required. Run one of these commands:${NC}"
            echo
            case "$DISTRO" in
                debian|ubuntu|linuxmint|pop)
                    echo "  sudo apt update"
                    echo "  sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libdbus-1-3 libegl1 libfontconfig1 libgl1"
                    ;;
                fedora|rhel|centos|rocky|almalinux)
                    echo "  sudo dnf install -y xcb-util-cursor xcb-util-image xcb-util-keysyms xcb-util-renderutil xcb-util-wm libxkbcommon-x11 mesa-libEGL fontconfig"
                    ;;
                arch|manjaro|endeavouros)
                    echo "  sudo pacman -S --needed xcb-util-cursor xcb-util-image xcb-util-keysyms xcb-util-renderutil xcb-util-wm libxkbcommon-x11 mesa fontconfig"
                    ;;
                *)
                    echo "  See SYSTEM_DEPENDENCIES.md for your distribution"
                    ;;
            esac
            echo
            echo -e "${YELLOW}For detailed instructions, see: SYSTEM_DEPENDENCIES.md${NC}"
            echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            exit 1
        else
            echo
            install_system_deps
            if [ $? -ne 0 ]; then
                echo -e "${RED}Failed to install dependencies automatically${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${GREEN}✓ System dependencies OK${NC}"
        touch "$SYSTEM_DEPS_CHECKED"
    fi
}

# Handle command line arguments
if [[ "$1" == "--install-deps" ]]; then
    install_system_deps
    exit $?
elif [[ "$1" != "--skip-deps-check" ]]; then
    check_system_dependencies
fi

# Check for Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo "Install Python 3.8 or newer:"
    case "$DISTRO" in
        debian|ubuntu|linuxmint|pop)
            echo "  sudo apt install python3 python3-venv"
            ;;
        fedora|rhel|centos|rocky|almalinux)
            echo "  sudo dnf install python3 python3-virtualenv"
            ;;
        arch|manjaro|endeavouros)
            echo "  sudo pacman -S python python-virtualenv"
            ;;
        *)
            echo "  Install Python 3.8+ using your package manager"
            ;;
    esac
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Setting up SPARK Personal for first time..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo

    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR" 2>/dev/null
    VENV_RESULT=$?

    if [ $VENV_RESULT -ne 0 ]; then
        echo -e "${YELLOW}venv module not available, trying with virtualenv...${NC}"
        if command -v virtualenv >/dev/null 2>&1; then
            virtualenv -p python3 "$VENV_DIR"
            VENV_RESULT=$?
        else
            echo -e "${RED}Error: Cannot create virtual environment${NC}"
            echo
            echo "Install python3-venv:"
            case "$DISTRO" in
                debian|ubuntu|linuxmint|pop)
                    echo "  sudo apt install python3-venv"
                    ;;
                fedora|rhel|centos|rocky|almalinux)
                    echo "  sudo dnf install python3-virtualenv"
                    ;;
                arch|manjaro|endeavouros)
                    echo "  sudo pacman -S python-virtualenv"
                    ;;
            esac
            read -p "Press Enter to exit..."
            exit 1
        fi
    fi

    if [ $VENV_RESULT -ne 0 ]; then
        echo -e "${RED}Error: Failed to create virtual environment${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi

    echo "Installing Python dependencies..."
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo -e "${RED}Error: Virtual environment activation script not found${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi

    source "$VENV_DIR/bin/activate" || {
        echo -e "${RED}Error: Failed to activate virtual environment${NC}"
        read -p "Press Enter to exit..."
        exit 1
    }

    pip install --upgrade pip --quiet || {
        echo -e "${RED}Error: Failed to upgrade pip${NC}"
        read -p "Press Enter to exit..."
        exit 1
    }

    if [ ! -f requirements.txt ]; then
        echo -e "${RED}Error: requirements.txt not found${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi

    pip install -r requirements.txt || {
        echo -e "${RED}Error: Failed to install Python dependencies${NC}"
        read -p "Press Enter to exit..."
        exit 1
    }

    echo
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ Setup complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
else
    # Activate existing virtual environment
    if [ ! -f "$VENV_DIR/bin/activate" ]; then
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}Error: Virtual environment appears corrupted${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo
        echo "The venv directory exists but the activation script is missing."
        echo "Please remove the venv directory and try again:"
        echo
        echo "  rm -rf venv"
        echo "  ./run.sh"
        echo
        read -p "Press Enter to exit..."
        exit 1
    fi

    source "$VENV_DIR/bin/activate" || {
        echo -e "${RED}Error: Failed to activate virtual environment${NC}"
        read -p "Press Enter to exit..."
        exit 1
    }
fi

echo "Starting SPARK Personal..."

# Set up log file location
LOG_DIR="$HOME/.spark_personal"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/spark.log"

echo "Output will be logged to: $LOG_FILE"
echo

# Run SPARK in background with nohup
# Use the venv's python to ensure correct environment
nohup "$VENV_DIR/bin/python" -m spark.main > "$LOG_FILE" 2>&1 &
SPARK_PID=$!

# Give it a moment to start
sleep 2

# Check if process is still running
if ps -p $SPARK_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ SPARK Personal started successfully (PID: $SPARK_PID)${NC}"

    # Mark dependencies as checked on Linux
    if [ "$(uname)" = "Linux" ] && [ ! -f "$SYSTEM_DEPS_CHECKED" ]; then
        touch "$SYSTEM_DEPS_CHECKED"
    fi

    echo
    echo "SPARK is now running in the background."
    echo "You can close this terminal - SPARK will continue running."
    echo
    echo "To view logs: tail -f $LOG_FILE"
    echo "To stop SPARK: kill $SPARK_PID"
    echo

    # Keep terminal open so user can read the message
    # Don't use timeout if we can't detect if we're in an interactive terminal
    if [ -t 0 ]; then
        read -t 10 -p "Press Enter to close (auto-closes in 10 seconds)..." || true
    else
        # Not interactive, wait 10 seconds
        sleep 10
    fi
    echo
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  SPARK Personal failed to start${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo -e "${YELLOW}Check the log file for details:${NC} $LOG_FILE"
    echo
    echo -e "${YELLOW}This is likely due to missing Qt system libraries.${NC}"
    echo

    # Ensure we check dependencies again next time since it failed
    rm -f "$SYSTEM_DEPS_CHECKED"

    if [ "$(uname)" = "Linux" ]; then
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo
        read -p "Would you like to try installing system dependencies? (Y/n) " -n 1 -r
        echo
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            install_system_deps
            if [ $? -eq 0 ]; then
                echo
                echo -e "${GREEN}Dependencies installed. Trying to start SPARK again...${NC}"
                echo
                exec "$0"  # Restart the script
            fi
        else
            echo -e "${YELLOW}Manual installation required:${NC}"
            echo
            case "$DISTRO" in
                debian|ubuntu|linuxmint|pop)
                    echo "  sudo apt update"
                    echo "  sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1"
                    ;;
                fedora|rhel|centos|rocky|almalinux)
                    echo "  sudo dnf install -y xcb-util-cursor libxkbcommon-x11"
                    ;;
                arch|manjaro|endeavouros)
                    echo "  sudo pacman -S --needed xcb-util-cursor libxkbcommon-x11"
                    ;;
                *)
                    echo "  See SYSTEM_DEPENDENCIES.md for your distribution"
                    ;;
            esac
            echo
            echo -e "${YELLOW}For detailed troubleshooting, see: SYSTEM_DEPENDENCIES.md${NC}"
        fi
    fi

    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
