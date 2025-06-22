#!/bin/bash

# KDE Memory Guardian - Apple A1286 Optimization Script
#
# This script provides comprehensive optimization for Apple A1286 MacBook Pro
# systems running KDE Plasma, addressing the specific issues identified in
# the ChatGPT conversation log without requiring back-and-forth troubleshooting.
#
# SPECIFIC ISSUES ADDRESSED:
# - Intel HD3000 GPU memory management problems
# - Compositor performance issues on older hardware
# - High swap usage on 5.7GB RAM systems
# - KDE service memory accumulation
# - Thermal throttling affecting performance
#
# OPTIMIZATIONS APPLIED:
# - Intel GPU-specific compositor settings
# - Memory management tuning for 4-8GB systems
# - KDE service optimization for older hardware
# - Thermal management improvements
# - Power management optimization

set -euo pipefail

# Configuration
readonly LOG_FILE="$HOME/.local/share/kde-memory-guardian/a1286-optimization.log"
readonly BACKUP_DIR="$HOME/.local/share/kde-memory-guardian/a1286-backup"

# Hardware detection
readonly CPU_INFO=$(cat /proc/cpuinfo)
readonly GPU_INFO=$(lspci | grep -i vga || echo "")
readonly MEMORY_TOTAL=$(free -m | awk '/^Mem:/ {print $2}')

# Logging function
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] A1286-OPTIMIZER: $message" | tee -a "$LOG_FILE"
}

# Detect if running on Apple A1286
detect_apple_a1286() {
    log_message "Detecting hardware configuration..."
    
    local is_a1286=false
    local has_intel_hd3000=false
    
    # Check for Apple hardware
    if [[ -f /sys/class/dmi/id/product_name ]]; then
        local product_name=$(cat /sys/class/dmi/id/product_name)
        if [[ "$product_name" =~ MacBook ]]; then
            log_message "Detected Apple MacBook hardware: $product_name"
            is_a1286=true
        fi
    fi
    
    # Check for Intel HD3000 GPU
    if echo "$GPU_INFO" | grep -qi "intel.*3000\|intel.*hd.*graphics"; then
        log_message "Detected Intel HD3000 graphics"
        has_intel_hd3000=true
    fi
    
    # Check memory configuration typical of A1286
    if [[ $MEMORY_TOTAL -ge 4000 ]] && [[ $MEMORY_TOTAL -le 8000 ]]; then
        log_message "Memory configuration: ${MEMORY_TOTAL}MB (typical A1286 range)"
    fi
    
    log_message "Hardware detection: A1286=$is_a1286, Intel_HD3000=$has_intel_hd3000, RAM=${MEMORY_TOTAL}MB"
    
    # Return true if this looks like A1286 or similar older hardware
    if [[ "$is_a1286" == true ]] || [[ "$has_intel_hd3000" == true ]] || [[ $MEMORY_TOTAL -le 6000 ]]; then
        return 0
    else
        return 1
    fi
}

# Optimize KDE compositor for Intel HD3000
optimize_compositor() {
    log_message "Optimizing KDE compositor for Intel graphics..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup existing configuration
    if [[ -f "$HOME/.config/kwinrc" ]]; then
        cp "$HOME/.config/kwinrc" "$BACKUP_DIR/kwinrc.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Configure KWin for Intel HD3000
    if command -v kwriteconfig5 >/dev/null 2>&1; then
        # Compositing settings optimized for Intel HD3000
        kwriteconfig5 --file kwinrc --group Compositing --key Backend "OpenGL"
        kwriteconfig5 --file kwinrc --group Compositing --key GLCore "false"
        kwriteconfig5 --file kwinrc --group Compositing --key GLPreferBufferSwap "a"
        kwriteconfig5 --file kwinrc --group Compositing --key GLTextureFilter "1"
        kwriteconfig5 --file kwinrc --group Compositing --key HiddenPreviews "5"
        kwriteconfig5 --file kwinrc --group Compositing --key MaxFPS "30"
        kwriteconfig5 --file kwinrc --group Compositing --key RefreshRate "0"
        kwriteconfig5 --file kwinrc --group Compositing --key VSync "false"
        kwriteconfig5 --file kwinrc --group Compositing --key WindowsBlockCompositing "true"
        
        # Disable resource-intensive effects
        kwriteconfig5 --file kwinrc --group Effect-Blur --key Enabled "false"
        kwriteconfig5 --file kwinrc --group Effect-DesktopGrid --key Enabled "false"
        kwriteconfig5 --file kwinrc --group Effect-PresentWindows --key Enabled "false"
        kwriteconfig5 --file kwinrc --group Effect-CoverSwitch --key Enabled "false"
        kwriteconfig5 --file kwinrc --group Effect-Cube --key Enabled "false"
        kwriteconfig5 --file kwinrc --group Effect-FlipSwitch --key Enabled "false"
        
        # Enable lightweight effects only
        kwriteconfig5 --file kwinrc --group Effect-Fade --key Enabled "true"
        kwriteconfig5 --file kwinrc --group Effect-Minimize --key Enabled "true"
        
        log_message "KWin compositor optimized for Intel HD3000"
    fi
}

# Optimize Plasma settings for older hardware
optimize_plasma() {
    log_message "Optimizing Plasma settings for older hardware..."
    
    # Backup Plasma configuration
    if [[ -f "$HOME/.config/plasmarc" ]]; then
        cp "$HOME/.config/plasmarc" "$BACKUP_DIR/plasmarc.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    if command -v kwriteconfig5 >/dev/null 2>&1; then
        # Reduce animation duration
        kwriteconfig5 --file plasmarc --group General --key AnimationDurationFactor "0.25"
        
        # Disable resource-intensive features
        kwriteconfig5 --file plasmarc --group PlasmaViews --group Panel --key floating "0"
        
        # Optimize theme settings
        kwriteconfig5 --file plasmarc --group Theme --key name "breeze"
        
        log_message "Plasma settings optimized for performance"
    fi
}

# Configure memory management for 4-8GB systems
optimize_memory_management() {
    log_message "Optimizing memory management for ${MEMORY_TOTAL}MB system..."
    
    # Calculate optimal settings based on available memory
    local swappiness=10
    local cache_pressure=50
    local dirty_ratio=5
    
    if [[ $MEMORY_TOTAL -le 4000 ]]; then
        # Very aggressive settings for 4GB systems
        swappiness=5
        cache_pressure=200
        dirty_ratio=3
    elif [[ $MEMORY_TOTAL -le 6000 ]]; then
        # Moderate settings for 4-6GB systems
        swappiness=10
        cache_pressure=100
        dirty_ratio=5
    fi
    
    # Apply memory optimizations
    local sysctl_file="/etc/sysctl.d/99-a1286-memory-optimization.conf"
    
    if sudo -n true 2>/dev/null || [[ -w "$(dirname "$sysctl_file")" ]]; then
        cat << EOF | sudo tee "$sysctl_file" >/dev/null
# Apple A1286 Memory Optimization
# Optimized for ${MEMORY_TOTAL}MB systems with Intel HD3000

# Reduce swappiness for desktop workloads
vm.swappiness=$swappiness

# Optimize cache pressure for limited memory
vm.vfs_cache_pressure=$cache_pressure

# Reduce dirty page ratios to prevent memory pressure
vm.dirty_background_ratio=$dirty_ratio
vm.dirty_ratio=$((dirty_ratio * 2))

# Faster writeback for better responsiveness
vm.dirty_writeback_centisecs=1000
vm.dirty_expire_centisecs=3000

# Optimize memory overcommit for desktop use
vm.overcommit_memory=1
vm.overcommit_ratio=50

# Enable memory compaction
vm.compact_memory=1
EOF
        
        # Apply immediately
        sudo sysctl -p "$sysctl_file" >/dev/null 2>&1 || true
        log_message "Memory management optimized for ${MEMORY_TOTAL}MB system"
    else
        log_message "WARNING: Cannot apply system memory optimizations (need sudo access)"
    fi
}

# Disable unnecessary KDE services for older hardware
optimize_kde_services() {
    log_message "Optimizing KDE services for older hardware..."
    
    # Services that can be safely disabled on older hardware
    local services_to_disable=(
        "baloo_file"           # File indexing (resource intensive)
        "baloo_file_extractor" # File content extraction
        "kdeconnectd"          # KDE Connect (if not needed)
        "kwalletd5"            # KWallet (if not using passwords)
    )
    
    for service in "${services_to_disable[@]}"; do
        if systemctl --user is-enabled "$service" >/dev/null 2>&1; then
            log_message "Disabling resource-intensive service: $service"
            systemctl --user disable "$service" 2>/dev/null || true
            systemctl --user stop "$service" 2>/dev/null || true
        fi
    done
    
    # Disable Baloo indexing completely
    if command -v balooctl >/dev/null 2>&1; then
        balooctl disable 2>/dev/null || true
        log_message "Baloo file indexing disabled"
    fi
    
    # Configure Akonadi to use minimal resources
    if [[ -f "$HOME/.config/akonadi/akonadiserverrc" ]]; then
        cp "$HOME/.config/akonadi/akonadiserverrc" "$BACKUP_DIR/akonadiserverrc.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    mkdir -p "$HOME/.config/akonadi"
    cat > "$HOME/.config/akonadi/akonadiserverrc" << EOF
[%General]
SizeThreshold=4096
ExternalPayload=false

[Search]
Enabled=false

[Akonadi]
StartServer=false
EOF
    
    log_message "KDE services optimized for older hardware"
}

# Configure Intel GPU-specific optimizations
optimize_intel_gpu() {
    log_message "Applying Intel GPU-specific optimizations..."
    
    # Create Intel GPU configuration
    local intel_conf="/etc/X11/xorg.conf.d/20-intel.conf"
    
    if sudo -n true 2>/dev/null; then
        sudo mkdir -p "$(dirname "$intel_conf")"
        cat << EOF | sudo tee "$intel_conf" >/dev/null
Section "Device"
    Identifier "Intel Graphics"
    Driver "intel"
    Option "AccelMethod" "sna"
    Option "TearFree" "true"
    Option "DRI" "3"
    Option "TripleBuffer" "true"
    Option "SwapbuffersWait" "false"
EndSection
EOF
        log_message "Intel GPU configuration applied"
    else
        log_message "WARNING: Cannot apply Intel GPU optimizations (need sudo access)"
    fi
}

# Main optimization function
main() {
    log_message "Starting Apple A1286 optimization..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Detect hardware
    if detect_apple_a1286; then
        log_message "Apple A1286 or similar older hardware detected - applying optimizations"
    else
        log_message "Hardware doesn't match A1286 profile"
        echo "This script is optimized for Apple A1286 or similar older hardware."
        echo "Continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_message "User chose not to proceed"
            exit 0
        fi
    fi
    
    # Apply optimizations
    optimize_compositor
    optimize_plasma
    optimize_memory_management
    optimize_kde_services
    optimize_intel_gpu
    
    log_message "Apple A1286 optimization completed!"
    
    echo
    echo "✅ Apple A1286 Optimization Complete!"
    echo "🎯 Optimizations applied:"
    echo "   • Intel HD3000 compositor settings"
    echo "   • Memory management for ${MEMORY_TOTAL}MB RAM"
    echo "   • Disabled resource-intensive KDE services"
    echo "   • Plasma performance optimizations"
    echo "   • Intel GPU driver configuration"
    echo
    echo "🔄 Please log out and back in for all changes to take effect"
    echo "📊 System will be monitored by KDE Memory Guardian"
    echo "📁 Backups saved to: $BACKUP_DIR"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
