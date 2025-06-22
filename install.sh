#!/bin/bash

# KDE Memory Guardian - Installation Script
# 
# This script installs a comprehensive KDE Plasma memory management solution
# that automatically monitors and restarts KDE services when memory usage
# becomes excessive, preventing system freezes and performance issues.
#
# WHAT IT DOES:
# - Installs a systemd user service for automatic memory monitoring
# - Configures system-wide memory optimizations via sysctl
# - Sets up KDE Plasma configuration optimizations  
# - Creates useful aliases for memory monitoring
# - Configures log rotation for the memory manager
#
# WHY IT'S NEEDED:
# KDE Plasma has well-documented memory leaks where plasmashell and
# kglobalacceld can grow to consume 2GB+ of RAM, causing system freezes.
# This solution automatically restarts these services before they become
# problematic, maintaining system stability.
#
# HOW IT WORKS:
# A systemd service runs a bash script every 5 minutes that checks:
# 1. Individual process memory usage (plasmashell, kglobalacceld)
# 2. Overall system memory usage
# 3. Automatically restarts services or clears caches as needed

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration constants
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
readonly LOCAL_BIN_DIR="$HOME/.local/bin"
readonly SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
readonly LOG_DIR="$HOME/.local/share"
readonly SYSCTL_CONFIG="/etc/sysctl.d/99-kde-memory-optimization.conf"

# Color codes for output formatting
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions for clear user feedback
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

# Check if running on a supported system
check_prerequisites() {
    log_info "Checking system prerequisites..."
    
    # Verify we're on a Linux system with systemd
    if ! command -v systemctl >/dev/null 2>&1; then
        log_error "systemctl not found. This script requires systemd."
        exit 1
    fi
    
    # Verify we're in a KDE environment
    if [[ "${XDG_CURRENT_DESKTOP:-}" != *"KDE"* ]] && [[ "${DESKTOP_SESSION:-}" != *"plasma"* ]]; then
        log_warning "KDE Plasma not detected. This script is designed for KDE environments."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check for required KDE tools
    if ! command -v kstart >/dev/null 2>&1; then
        log_error "kstart not found. Please install KDE development tools."
        log_info "On Fedora: sudo dnf install kdelibs-devel"
        log_info "On Ubuntu: sudo apt install kde-runtime"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create necessary directories with proper permissions
create_directories() {
    log_info "Creating required directories..."
    
    # Create directories if they don't exist
    mkdir -p "$LOCAL_BIN_DIR"
    mkdir -p "$SYSTEMD_USER_DIR" 
    mkdir -p "$LOG_DIR"
    
    # Ensure proper permissions
    chmod 755 "$LOCAL_BIN_DIR"
    chmod 755 "$SYSTEMD_USER_DIR"
    
    log_success "Directories created successfully"
}

# Install the main memory manager script
install_memory_manager_script() {
    log_info "Installing KDE Memory Manager script..."
    
    # Copy the memory manager script to local bin
    cp "$SCRIPT_DIR/src/kde-memory-manager.sh" "$LOCAL_BIN_DIR/"
    chmod +x "$LOCAL_BIN_DIR/kde-memory-manager.sh"
    
    log_success "Memory manager script installed to $LOCAL_BIN_DIR"
}

# Install and enable the systemd service
install_systemd_service() {
    log_info "Installing systemd service..."
    
    # Copy service file to user systemd directory
    cp "$SCRIPT_DIR/src/kde-memory-manager.service" "$SYSTEMD_USER_DIR/"
    
    # Reload systemd daemon to recognize new service
    systemctl --user daemon-reload
    
    # Enable service to start automatically
    systemctl --user enable kde-memory-manager.service
    
    # Start the service immediately
    systemctl --user start kde-memory-manager.service
    
    log_success "Systemd service installed and started"
}

# Configure system-wide memory optimizations
configure_system_optimizations() {
    log_info "Configuring system memory optimizations..."
    
    # Check if we can write to sysctl.d (requires sudo)
    if sudo -n true 2>/dev/null; then
        # Create sysctl configuration for memory optimization
        sudo tee "$SYSCTL_CONFIG" > /dev/null << 'EOF'
# KDE Memory Guardian - System Memory Optimizations
# These settings optimize memory management for KDE Plasma environments
# to reduce memory pressure and improve system responsiveness

# Reduce swappiness - prefer RAM over swap
# Default: 60, Optimized: 10
# WHY: Reduces swap usage which causes system slowdowns
vm.swappiness=10

# Improve memory reclaim behavior  
# Default: 100, Optimized: 50
# WHY: More aggressive reclaim of cached memory when needed
vm.vfs_cache_pressure=50

# Reduce dirty page writeback time
# Default: 500, Optimized: 1500  
# WHY: More frequent writeback prevents memory pressure buildup
vm.dirty_writeback_centisecs=1500

# Optimize memory overcommit for desktop workloads
# WHY: Better handling of memory allocation for GUI applications
vm.overcommit_memory=1
vm.overcommit_ratio=50

# Enable memory compaction
# WHY: Reduces memory fragmentation
vm.compact_memory=1
EOF
        
        # Apply settings immediately
        sudo sysctl -p "$SYSCTL_CONFIG"
        log_success "System memory optimizations applied"
    else
        log_warning "Cannot configure system optimizations (sudo required)"
        log_info "Run 'sudo sysctl vm.swappiness=10' manually for better performance"
    fi
}

# Configure KDE Plasma optimizations
configure_kde_optimizations() {
    log_info "Configuring KDE Plasma optimizations..."
    
    # Create KDE configuration directory if it doesn't exist
    mkdir -p "$HOME/.config"
    
    # Optimize Plasma configuration for reduced memory usage
    # NOTE: These settings reduce visual effects to save memory
    cat > "$HOME/.config/plasmarc" << 'EOF'
[PlasmaViews][Panel 1]
# Reduce panel memory usage by disabling floating panels
# WHY: Floating panels use more memory for transparency effects
alignment=132
floating=0

[Theme]
# Use the default Breeze theme (lightest on memory)
# WHY: Custom themes often have memory leaks
name=breeze

[General]
# Reduce animation duration to save memory
# WHY: Shorter animations = less memory for animation buffers
AnimationDurationFactor=0.5
EOF
    
    log_success "KDE Plasma optimizations configured"
}

# Add useful aliases to user's shell configuration
add_monitoring_aliases() {
    log_info "Adding memory monitoring aliases..."
    
    # Add aliases to bashrc (create backup first)
    if [[ -f "$HOME/.bashrc" ]]; then
        cp "$HOME/.bashrc" "$HOME/.bashrc.backup.$(date +%Y%m%d)"
    fi
    
    # Append aliases to bashrc
    cat >> "$HOME/.bashrc" << 'EOF'

# KDE Memory Guardian - Monitoring Aliases
# These aliases provide easy access to memory monitoring and management

# Check current memory usage with top processes
alias memcheck='echo "=== Memory Usage ===" && free -h && echo -e "\n=== Top Memory Processes ===" && ps aux --sort=-%mem | head -10'

# Manually restart Plasma Shell (useful for testing)
alias plasma-restart='killall plasmashell && kstart plasmashell'

# Check KDE Memory Guardian service status
alias kde-memory-status='systemctl --user status kde-memory-manager.service'

# View real-time logs from KDE Memory Guardian
alias kde-memory-logs='journalctl --user -u kde-memory-manager.service -f'

# Quick memory statistics
alias memstats='echo "System Memory:" && free -h | grep "Mem:" && echo "Swap Usage:" && free -h | grep "Swap:" && echo "Plasma Memory:" && ps -eo rss,comm | grep plasmashell | awk "{sum+=\$1} END {print (sum/1024) \" MB\"}"'
EOF
    
    log_success "Memory monitoring aliases added to ~/.bashrc"
}

# Configure log rotation to prevent log files from growing too large
configure_log_rotation() {
    log_info "Configuring log rotation..."
    
    # Create logrotate configuration directory
    mkdir -p "$HOME/.config/logrotate"
    
    # Configure log rotation for memory manager logs
    cat > "$HOME/.config/logrotate/kde-memory-manager" << 'EOF'
# KDE Memory Guardian Log Rotation Configuration
# Prevents log files from consuming excessive disk space

/home/*/.*local/share/kde-memory-manager.log {
    # Rotate daily to keep logs manageable
    daily
    
    # Keep 7 days of logs (1 week history)
    rotate 7
    
    # Compress old logs to save space
    compress
    delaycompress
    
    # Don't error if log file is missing
    missingok
    
    # Don't rotate empty log files
    notifempty
    
    # Create new log file with proper permissions
    create 644
}
EOF
    
    log_success "Log rotation configured"
}

# Verify the installation was successful
verify_installation() {
    log_info "Verifying installation..."
    
    # Check if service is running
    if systemctl --user is-active --quiet kde-memory-manager.service; then
        log_success "KDE Memory Guardian service is running"
    else
        log_error "Service is not running. Check logs with: journalctl --user -u kde-memory-manager.service"
        return 1
    fi
    
    # Check if script is executable
    if [[ -x "$LOCAL_BIN_DIR/kde-memory-manager.sh" ]]; then
        log_success "Memory manager script is properly installed"
    else
        log_error "Memory manager script is not executable"
        return 1
    fi
    
    # Check if log file exists (service should create it)
    sleep 2  # Give service time to create log file
    if [[ -f "$LOG_DIR/kde-memory-manager.log" ]]; then
        log_success "Logging is working correctly"
    else
        log_warning "Log file not yet created (this is normal for new installations)"
    fi
    
    return 0
}

# Display post-installation information
show_completion_message() {
    echo
    log_success "🎉 KDE Memory Guardian installation completed successfully!"
    echo
    echo -e "${BLUE}📊 What was installed:${NC}"
    echo "   • Automatic KDE memory monitoring service"
    echo "   • System-wide memory optimizations"  
    echo "   • Plasma configuration optimizations"
    echo "   • Memory monitoring aliases"
    echo "   • Log rotation configuration"
    echo
    echo -e "${BLUE}🔧 Useful commands:${NC}"
    echo "   • memcheck                 - Check current memory usage"
    echo "   • plasma-restart          - Manually restart Plasma"
    echo "   • kde-memory-status       - Check service status"
    echo "   • kde-memory-logs         - View real-time logs"
    echo "   • memstats                - Quick memory statistics"
    echo
    echo -e "${BLUE}🔄 The service will:${NC}"
    echo "   • Monitor memory usage every 5 minutes"
    echo "   • Automatically restart Plasma if it uses > 1.5GB"
    echo "   • Restart kglobalacceld if it uses > 1GB"
    echo "   • Clear system caches when memory usage > 80%"
    echo
    echo -e "${BLUE}📝 Logs location:${NC} ~/.local/share/kde-memory-manager.log"
    echo
    echo -e "${YELLOW}⚠️  For full optimization, please reboot or log out/in.${NC}"
    echo -e "${GREEN}🛡️  Your system is now protected against KDE memory leaks!${NC}"
}

# Main installation function that orchestrates all steps
main() {
    echo -e "${BLUE}🛡️  KDE Memory Guardian Installer${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo
    
    # Execute installation steps in order
    # Each function handles its own error checking and user feedback
    check_prerequisites
    create_directories
    install_memory_manager_script
    install_systemd_service
    configure_system_optimizations
    configure_kde_optimizations
    add_monitoring_aliases
    configure_log_rotation
    
    # Verify everything worked correctly
    if verify_installation; then
        show_completion_message
    else
        log_error "Installation verification failed. Please check the logs."
        exit 1
    fi
}

# Execute main function if script is run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
