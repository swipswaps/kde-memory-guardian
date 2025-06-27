#!/bin/bash
# KDE Memory Guardian - Complete Environment Setup Script
# Manages dependencies, environments, variables, folders, permissions

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
LOG_FILE="$PROJECT_ROOT/setup.log"
CONFIG_FILE="$PROJECT_ROOT/.env"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Detect OS and package manager
detect_system() {
    if command -v dnf >/dev/null 2>&1; then
        PACKAGE_MANAGER="dnf"
        INSTALL_CMD="sudo dnf install -y"
        OS_TYPE="fedora"
    elif command -v apt >/dev/null 2>&1; then
        PACKAGE_MANAGER="apt"
        INSTALL_CMD="sudo apt install -y"
        OS_TYPE="debian"
    elif command -v pacman >/dev/null 2>&1; then
        PACKAGE_MANAGER="pacman"
        INSTALL_CMD="sudo pacman -S --noconfirm"
        OS_TYPE="arch"
    else
        error "Unsupported package manager. Please install dependencies manually."
        exit 1
    fi
    
    log "Detected OS: $OS_TYPE with package manager: $PACKAGE_MANAGER"
}

# Create necessary directories with proper permissions
setup_directories() {
    log "Setting up directory structure..."
    
    local dirs=(
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/temp"
        "$PROJECT_ROOT/data"
        "$PROJECT_ROOT/backups"
        "$PROJECT_ROOT/testing/screenshots"
        "$PROJECT_ROOT/testing/reports"
        "$PROJECT_ROOT/database-tools/logs"
        "/tmp/kde-memory-guardian"
        "$HOME/.local/share/kde-memory-guardian"
        "$HOME/.config/kde-memory-guardian"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            chmod 755 "$dir"
            log "Created directory: $dir"
        else
            info "Directory already exists: $dir"
        fi
    done
    
    # Set special permissions for temp directories
    chmod 1777 "/tmp/kde-memory-guardian" 2>/dev/null || true
    chmod 700 "$HOME/.local/share/kde-memory-guardian"
    chmod 700 "$HOME/.config/kde-memory-guardian"
}

# Install system dependencies
install_system_dependencies() {
    log "Installing system dependencies..."
    
    local common_deps=(
        "python3"
        "python3-pip"
        "curl"
        "wget"
        "git"
        "sqlite3"
        "xdotool"
        "wmctrl"
    )
    
    local fedora_deps=(
        "python3-devel"
        "gcc"
        "firefox"
        "konsole"
        "at-spi2-core"
        "at-spi2-atk"
        "python3-gobject"
        "dbus-x11"
    )
    
    local debian_deps=(
        "python3-dev"
        "build-essential"
        "firefox"
        "konsole"
        "at-spi2-core"
        "libatspi2.0-dev"
        "python3-gi"
        "dbus-x11"
    )
    
    local arch_deps=(
        "python"
        "base-devel"
        "firefox"
        "konsole"
        "at-spi2-core"
        "at-spi2-atk"
        "python-gobject"
        "dbus"
    )
    
    # Install common dependencies
    for dep in "${common_deps[@]}"; do
        if ! command -v "$dep" >/dev/null 2>&1; then
            log "Installing $dep..."
            $INSTALL_CMD "$dep" || warning "Failed to install $dep"
        else
            info "$dep already installed"
        fi
    done
    
    # Install OS-specific dependencies
    case $OS_TYPE in
        "fedora")
            for dep in "${fedora_deps[@]}"; do
                log "Installing $dep..."
                $INSTALL_CMD "$dep" || warning "Failed to install $dep"
            done
            ;;
        "debian")
            sudo apt update
            for dep in "${debian_deps[@]}"; do
                log "Installing $dep..."
                $INSTALL_CMD "$dep" || warning "Failed to install $dep"
            done
            ;;
        "arch")
            for dep in "${arch_deps[@]}"; do
                log "Installing $dep..."
                $INSTALL_CMD "$dep" || warning "Failed to install $dep"
            done
            ;;
    esac
}

# Install Python dependencies
install_python_dependencies() {
    log "Installing Python dependencies..."
    
    # Upgrade pip first
    python3 -m pip install --user --upgrade pip
    
    # Install testing frameworks
    local python_deps=(
        "playwright>=1.40.0"
        "selenium>=4.15.0"
        "flask>=2.3.0"
        "requests>=2.31.0"
        "dogtail>=1.0.0"
        "psutil>=5.9.0"
        "pathlib2>=2.3.0"
    )
    
    for dep in "${python_deps[@]}"; do
        log "Installing Python package: $dep"
        python3 -m pip install --user "$dep" || warning "Failed to install $dep"
    done
    
    # Install Playwright browsers
    log "Installing Playwright browsers..."
    python3 -m playwright install firefox || warning "Failed to install Playwright Firefox"
    python3 -m playwright install chromium || warning "Failed to install Playwright Chromium"
}

# Setup environment variables
setup_environment_variables() {
    log "Setting up environment variables..."
    
    cat > "$CONFIG_FILE" << EOF
# KDE Memory Guardian Environment Configuration
# Generated on $(date)

# Project paths
PROJECT_ROOT="$PROJECT_ROOT"
TESTING_DIR="$PROJECT_ROOT/testing"
DATABASE_TOOLS_DIR="$PROJECT_ROOT/database-tools"
LOGS_DIR="$PROJECT_ROOT/logs"
TEMP_DIR="/tmp/kde-memory-guardian"

# Application settings
CRASH_ANALYZER_PORT=9000
DATABASE_MANAGER_PORT=5000
DEFAULT_CRASH_FILE="/home/owner/Documents/2025_06_26_vcscode_crash.txt"

# Database settings
CLIPBOARD_DB_PATH="$HOME/.local/share/clipboard_daemon/clipboard.sqlite"
GUARDIAN_DB_PATH="$HOME/.local/share/kde-memory-guardian/guardian.sqlite"

# Testing settings
PLAYWRIGHT_HEADLESS=false
SELENIUM_HEADLESS=false
TEST_TIMEOUT=30
SCREENSHOT_DIR="$PROJECT_ROOT/testing/screenshots"
REPORTS_DIR="$PROJECT_ROOT/testing/reports"

# Accessibility settings
AT_SPI_BUS_TYPE=session
QT_ACCESSIBILITY=1
GTK_MODULES=gail:atk-bridge

# System settings
DISPLAY=:0
SUDO_TIMEOUT=300
TERMINAL_TIMEOUT=30

# Logging settings
LOG_LEVEL=INFO
LOG_FILE="$PROJECT_ROOT/logs/kde-memory-guardian.log"
DEBUG_MODE=false
EOF

    chmod 600 "$CONFIG_FILE"
    log "Environment configuration saved to $CONFIG_FILE"
}

# Setup systemd user service for clipboard daemon
setup_systemd_service() {
    log "Setting up systemd user service..."
    
    local service_dir="$HOME/.config/systemd/user"
    mkdir -p "$service_dir"
    
    cat > "$service_dir/kde-memory-guardian.service" << EOF
[Unit]
Description=KDE Memory Guardian Clipboard Manager
After=graphical-session.target

[Service]
Type=simple
ExecStart=$PROJECT_ROOT/database-tools/crash-analysis-correlator.py
Restart=always
RestartSec=10
Environment=DISPLAY=:0
Environment=QT_ACCESSIBILITY=1
EnvironmentFile=$CONFIG_FILE

[Install]
WantedBy=default.target
EOF

    # Reload systemd and enable service
    systemctl --user daemon-reload
    systemctl --user enable kde-memory-guardian.service
    log "Systemd service configured and enabled"
}

# Setup file permissions
setup_permissions() {
    log "Setting up file permissions..."
    
    # Make scripts executable
    find "$PROJECT_ROOT" -name "*.sh" -exec chmod +x {} \;
    find "$PROJECT_ROOT" -name "*.py" -exec chmod +x {} \;
    
    # Set proper permissions for sensitive files
    chmod 600 "$CONFIG_FILE" 2>/dev/null || true
    chmod 700 "$HOME/.local/share/kde-memory-guardian" 2>/dev/null || true
    chmod 755 "$PROJECT_ROOT/testing"
    chmod 755 "$PROJECT_ROOT/database-tools"
    
    # Setup sudo permissions for specific commands
    local sudoers_file="/etc/sudoers.d/kde-memory-guardian"
    if [[ ! -f "$sudoers_file" ]]; then
        log "Setting up sudo permissions..."
        echo "# KDE Memory Guardian sudo permissions" | sudo tee "$sudoers_file" > /dev/null
        echo "$USER ALL=(ALL) NOPASSWD: /usr/bin/journalctl, /usr/bin/dmesg" | sudo tee -a "$sudoers_file" > /dev/null
        sudo chmod 440 "$sudoers_file"
        log "Sudo permissions configured"
    else
        info "Sudo permissions already configured"
    fi
}

# Verify installation
verify_installation() {
    log "Verifying installation..."
    
    local errors=0
    
    # Check Python packages
    local python_packages=("playwright" "selenium" "flask" "requests")
    for package in "${python_packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            info "✅ Python package $package: OK"
        else
            error "❌ Python package $package: MISSING"
            ((errors++))
        fi
    done
    
    # Check system commands
    local commands=("firefox" "konsole" "xdotool" "wmctrl" "sqlite3")
    for cmd in "${commands[@]}"; do
        if command -v "$cmd" >/dev/null 2>&1; then
            info "✅ Command $cmd: OK"
        else
            error "❌ Command $cmd: MISSING"
            ((errors++))
        fi
    done
    
    # Check directories
    local required_dirs=("$PROJECT_ROOT/testing" "$PROJECT_ROOT/database-tools" "$HOME/.local/share/kde-memory-guardian")
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            info "✅ Directory $dir: OK"
        else
            error "❌ Directory $dir: MISSING"
            ((errors++))
        fi
    done
    
    # Check permissions
    if [[ -r "$CONFIG_FILE" ]]; then
        info "✅ Configuration file: OK"
    else
        error "❌ Configuration file: MISSING"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        log "🎉 Installation verification completed successfully!"
        return 0
    else
        error "❌ Installation verification failed with $errors errors"
        return 1
    fi
}

# Main setup function
main() {
    log "🚀 Starting KDE Memory Guardian environment setup..."
    
    check_root
    detect_system
    setup_directories
    install_system_dependencies
    install_python_dependencies
    setup_environment_variables
    setup_systemd_service
    setup_permissions
    
    if verify_installation; then
        log "🎉 Setup completed successfully!"
        log "📋 Configuration file: $CONFIG_FILE"
        log "📊 Log file: $LOG_FILE"
        log ""
        log "🚀 To start the crash analyzer:"
        log "   cd $PROJECT_ROOT/database-tools"
        log "   python3 crash-analysis-correlator.py"
        log ""
        log "🧪 To run comprehensive tests:"
        log "   cd $PROJECT_ROOT/testing"
        log "   python3 end_to_end_comprehensive_tester.py"
    else
        error "❌ Setup failed. Check $LOG_FILE for details."
        exit 1
    fi
}

# Load environment variables if config exists
load_environment() {
    if [[ -f "$CONFIG_FILE" ]]; then
        log "Loading environment variables from $CONFIG_FILE"
        set -a  # Automatically export variables
        source "$CONFIG_FILE"
        set +a
    fi
}

# Check dependencies before running
check_dependencies() {
    log "Checking dependencies..."

    local missing_deps=()

    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    fi

    # Check pip
    if ! python3 -m pip --version >/dev/null 2>&1; then
        missing_deps+=("python3-pip")
    fi

    # Check virtual environment
    if [[ ! -d "$PROJECT_ROOT/venv" ]]; then
        warning "Virtual environment not found, will create one"
    fi

    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        error "Missing dependencies: ${missing_deps[*]}"
        log "Run this script with --install-deps to install them"
        return 1
    fi

    return 0
}

# Install dependencies only
install_dependencies_only() {
    log "Installing dependencies only..."
    detect_system
    install_system_dependencies
    install_python_dependencies
}

# Quick setup for development
quick_setup() {
    log "Running quick setup for development..."
    setup_directories
    setup_environment_variables
    setup_permissions

    if ! check_dependencies; then
        install_dependencies_only
    fi

    log "Quick setup completed!"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --full-setup)
                main
                exit $?
                ;;
            --quick-setup)
                quick_setup
                exit $?
                ;;
            --install-deps)
                install_dependencies_only
                exit $?
                ;;
            --check-deps)
                check_dependencies
                exit $?
                ;;
            --verify)
                verify_installation
                exit $?
                ;;
            --help|-h)
                echo "KDE Memory Guardian Environment Setup"
                echo ""
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --full-setup     Complete environment setup"
                echo "  --quick-setup    Quick setup for development"
                echo "  --install-deps   Install dependencies only"
                echo "  --check-deps     Check if dependencies are installed"
                echo "  --verify         Verify installation"
                echo "  --help, -h       Show this help message"
                echo ""
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
        shift
    done
}

# If no arguments provided, run full setup
if [[ $# -eq 0 ]]; then
    main
else
    parse_arguments "$@"
fi
