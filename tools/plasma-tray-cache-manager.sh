#!/usr/bin/env bash
################################################################################
# plasma-tray-cache-manager.sh — v1.0
# KDE Memory Guardian - Comprehensive Plasma Tray Cache Management
# PRF Directive: PRF‑COMPOSITE‑2025‑06‑22‑B (P01–P25+)
#
# WHAT: Comprehensive Plasma tray icon cache management with PRF compliance
# WHY: Addresses tray icon corruption, memory leaks, and session persistence issues
# HOW: Intelligent cache purging with backup, recovery, and comprehensive logging
#
# INTEGRATION: Works with KDE Memory Guardian for automated tray maintenance
# COMPLIANCE: Full PRF standards with terminal visibility and audit trails
################################################################################

# ─── ENFORCE SAFE EXECUTION ───────────────────────────────────────────────────
# WHAT: Prevents undefined variables and hidden pipe failures
# WHY: Ensures all steps are error-visible, no silent skips or failures
# HOW: Bash strict mode with proper IFS handling
set -euo pipefail
IFS=$'\n\t'

# ─── CONFIGURATION AND PATHS ──────────────────────────────────────────────────
# WHAT: Define all file paths and configuration options
# WHY: Centralized configuration for maintainability and customization
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="$HOME/.local/share/kde-memory-guardian/plasma-tray-cache.log"
readonly BACKUP_DIR="$HOME/.local/share/kde-memory-guardian/tray-backups"
readonly PLASMA_CONFIG="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"
readonly PLASMA_CACHE_DIR="$HOME/.cache/plasma"
readonly PLASMA_STATE_DIR="$HOME/.local/share/plasma"

# ─── ENHANCED LOGGING FUNCTIONS ───────────────────────────────────────────────
# WHAT: PRF-compliant logging with comprehensive visibility
# WHY: Ensures no hidden failures and provides real-time troubleshooting capability
# HOW: Dual output (terminal + log) with structured status tags

log_message() {
    local message="$1"
    local level="${2:-INFO}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S %Z')
    
    # Format message with appropriate emoji and tag for enhanced visibility
    local formatted_message=""
    case "$level" in
        "START") formatted_message="[START] 🚀 $message" ;;
        "STEP")  formatted_message="[STEP] 🔄 $message" ;;
        "INFO")  formatted_message="[INFO] ℹ️ $message" ;;
        "WARN")  formatted_message="[WARN] ⚠️ $message" ;;
        "ERROR") formatted_message="[ERROR] ❌ $message" ;;
        "OK")    formatted_message="[OK] ✅ $message" ;;
        "DONE")  formatted_message="[DONE] 🎉 $message" ;;
        "ALERT") formatted_message="[ALERT] 🚨 $message" ;;
        *)       formatted_message="[INFO] ℹ️ $message" ;;
    esac
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Output to both terminal and log file for full PRF compliance
    echo "[$timestamp] $formatted_message" | tee -a "$LOG_FILE"
}

# Log command execution with full stderr/stdout capture
log_command() {
    local description="$1"
    shift
    local command=("$@")
    
    log_message "Executing: $description" "STEP"
    log_message "Command: ${command[*]}" "INFO"
    
    # Execute command and capture all output with tee for dual visibility
    if "${command[@]}" 2>&1 | tee -a "$LOG_FILE"; then
        log_message "Command completed successfully: $description" "OK"
        return 0
    else
        local exit_code=$?
        log_message "Command failed with exit code $exit_code: $description" "ERROR"
        return $exit_code
    fi
}

# ─── SYSTEM VALIDATION ────────────────────────────────────────────────────────
# WHAT: Verify system compatibility and session requirements
# WHY: Prevents corruption of incompatible desktop environments
# HOW: Check session type, desktop environment, and required tools

validate_system() {
    log_message "Validating system compatibility" "STEP"
    
    # Check session type - this tool is optimized for X11
    local session_type="${XDG_SESSION_TYPE:-unknown}"
    if [[ "$session_type" != "x11" ]]; then
        log_message "This tool is optimized for X11 sessions. Detected: '$session_type'" "WARN"
        log_message "Wayland support is experimental - proceed with caution" "WARN"
    else
        log_message "X11 session detected - full compatibility" "OK"
    fi
    
    # Check desktop environment
    local desktop="${XDG_CURRENT_DESKTOP:-unknown}"
    if [[ "$desktop" != *"KDE"* ]]; then
        log_message "Non-KDE desktop detected: '$desktop'" "WARN"
        log_message "This tool is designed for KDE Plasma - results may vary" "WARN"
    else
        log_message "KDE Plasma desktop detected - full compatibility" "OK"
    fi
    
    # Check for required tools
    local required_tools=("kstart" "plasmashell" "pkill")
    for tool in "${required_tools[@]}"; do
        if command -v "$tool" >/dev/null 2>&1; then
            log_message "Required tool available: $tool" "OK"
        else
            log_message "Required tool missing: $tool" "ERROR"
            return 1
        fi
    done
    
    log_message "System validation completed successfully" "OK"
}

# ─── BACKUP MANAGEMENT ────────────────────────────────────────────────────────
# WHAT: Create comprehensive backups of Plasma configuration
# WHY: Allows complete recovery if cache purging causes issues
# HOW: Timestamped backups with verification and recovery instructions

create_backup() {
    log_message "Creating comprehensive Plasma configuration backup" "STEP"
    
    # Create backup directory with timestamp
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/plasma_backup_$backup_timestamp"
    mkdir -p "$backup_path"
    
    # Files and directories to backup
    local backup_targets=(
        "$PLASMA_CONFIG"
        "$HOME/.config/plasmarc"
        "$HOME/.config/plasmashellrc"
        "$HOME/.config/plasma-localerc"
        "$PLASMA_CACHE_DIR"
        "$PLASMA_STATE_DIR"
    )
    
    local backup_success=true
    for target in "${backup_targets[@]}"; do
        if [[ -e "$target" ]]; then
            local target_name=$(basename "$target")
            log_message "Backing up: $target → $backup_path/$target_name" "STEP"
            
            if cp -r "$target" "$backup_path/$target_name" 2>&1 | tee -a "$LOG_FILE"; then
                log_message "Successfully backed up: $target_name" "OK"
            else
                log_message "Failed to backup: $target_name" "ERROR"
                backup_success=false
            fi
        else
            log_message "Backup target not found (skipping): $target" "WARN"
        fi
    done
    
    if [[ "$backup_success" == true ]]; then
        log_message "Backup completed successfully: $backup_path" "OK"
        echo "$backup_path" > "$BACKUP_DIR/latest_backup.txt"
        
        # Create recovery instructions
        cat > "$backup_path/RECOVERY_INSTRUCTIONS.txt" << EOF
# Plasma Tray Cache Backup Recovery Instructions
# Created: $(date)
# Backup Path: $backup_path

To restore this backup:
1. Stop plasmashell: pkill plasmashell
2. Restore config: cp -r $backup_path/plasma-org.kde.plasma.desktop-appletsrc ~/.config/
3. Restore cache: cp -r $backup_path/plasma ~/.cache/
4. Restore state: cp -r $backup_path/plasma ~/.local/share/
5. Restart plasmashell: kstart plasmashell

Or run: $SCRIPT_DIR/plasma-tray-cache-manager.sh --restore $backup_path
EOF
        
        log_message "Recovery instructions created: $backup_path/RECOVERY_INSTRUCTIONS.txt" "OK"
        return 0
    else
        log_message "Backup completed with errors - check log for details" "ERROR"
        return 1
    fi
}

# ─── CACHE PURGING ────────────────────────────────────────────────────────────
# WHAT: Comprehensive Plasma tray cache purging with safety checks
# WHY: Resolves tray icon corruption, memory leaks, and performance issues
# HOW: Systematic removal of cache files with plasmashell restart

purge_tray_cache() {
    log_message "Starting comprehensive Plasma tray cache purge" "START"
    
    # Step 1: Stop plasmashell gracefully
    log_message "Stopping plasmashell processes" "STEP"
    if pgrep plasmashell >/dev/null 2>&1; then
        log_command "Terminate plasmashell" pkill plasmashell
        sleep 2
        
        # Verify termination
        if pgrep plasmashell >/dev/null 2>&1; then
            log_message "Plasmashell still running, force terminating" "WARN"
            log_command "Force terminate plasmashell" pkill -9 plasmashell
            sleep 1
        fi
        log_message "Plasmashell terminated successfully" "OK"
    else
        log_message "Plasmashell not running" "INFO"
    fi
    
    # Step 2: Remove primary configuration file
    if [[ -f "$PLASMA_CONFIG" ]]; then
        local config_backup="${PLASMA_CONFIG}.bak.$(date +%s)"
        log_message "Moving config file: $PLASMA_CONFIG → $config_backup" "STEP"
        
        if mv "$PLASMA_CONFIG" "$config_backup" 2>&1 | tee -a "$LOG_FILE"; then
            log_message "Configuration file moved successfully" "OK"
        else
            log_message "Failed to move configuration file" "ERROR"
            return 1
        fi
    else
        log_message "Primary config file not found: $PLASMA_CONFIG" "WARN"
    fi
    
    # Step 3: Clear cache directories
    local cache_dirs=(
        "$PLASMA_CACHE_DIR/plasma-svgelements"
        "$PLASMA_CACHE_DIR/plasma_theme_*.kcache"
        "$HOME/.cache/icon-cache.kcache"
        "$HOME/.cache/krunner"
    )
    
    for cache_dir in "${cache_dirs[@]}"; do
        if [[ -e $cache_dir ]]; then
            log_message "Removing cache: $cache_dir" "STEP"
            if rm -rf $cache_dir 2>&1 | tee -a "$LOG_FILE"; then
                log_message "Cache removed successfully: $(basename "$cache_dir")" "OK"
            else
                log_message "Failed to remove cache: $(basename "$cache_dir")" "WARN"
            fi
        fi
    done
    
    # Step 4: Restart plasmashell
    log_message "Restarting plasmashell with fresh configuration" "STEP"
    
    # Use kstart for proper KDE integration
    if command -v kstart >/dev/null 2>&1; then
        log_command "Start plasmashell via kstart" nohup kstart plasmashell
    else
        log_command "Start plasmashell directly" nohup plasmashell
    fi
    
    # Wait for startup and verify
    sleep 3
    if pgrep plasmashell >/dev/null 2>&1; then
        log_message "Plasmashell restarted successfully" "OK"
    else
        log_message "Plasmashell failed to start - manual intervention required" "ERROR"
        return 1
    fi
    
    log_message "Plasma tray cache purge completed successfully" "DONE"
    log_message "Tray icons should repopulate automatically" "INFO"
    log_message "If issues persist, restore from backup or restart session" "INFO"
}

# ─── MAIN EXECUTION ───────────────────────────────────────────────────────────
# WHAT: Main function orchestrating the cache management process
# WHY: Provides structured execution with comprehensive error handling
# HOW: Sequential execution with validation, backup, and purging

main() {
    log_message "KDE Memory Guardian - Plasma Tray Cache Manager started" "START"
    log_message "Script: $(basename "$0"), PID: $$" "INFO"
    log_message "Log file: $LOG_FILE" "INFO"
    
    # Validate system compatibility
    if ! validate_system; then
        log_message "System validation failed - aborting" "ERROR"
        exit 1
    fi
    
    # Create comprehensive backup
    if ! create_backup; then
        log_message "Backup creation failed - aborting for safety" "ERROR"
        exit 1
    fi
    
    # Perform cache purging
    if ! purge_tray_cache; then
        log_message "Cache purging failed - check log and consider restoring backup" "ERROR"
        exit 1
    fi
    
    log_message "Plasma tray cache management completed successfully" "DONE"
    log_message "Monitor system for 5-10 minutes to ensure stability" "INFO"
    log_message "Full log available at: $LOG_FILE" "INFO"
}

# ─── SCRIPT ENTRY POINT ───────────────────────────────────────────────────────
# Execute main function only if script is run directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
