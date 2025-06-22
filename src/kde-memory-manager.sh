#!/bin/bash

# KDE Memory Guardian - Core Memory Management Script
#
# This script continuously monitors KDE Plasma memory usage and automatically
# restarts problematic services when memory consumption exceeds safe thresholds.
# It prevents system freezes and performance degradation caused by KDE memory leaks.
#
# WHAT IT MONITORS:
# - plasmashell memory usage (main KDE shell process)
# - kglobalacceld memory usage (global keyboard shortcuts daemon)  
# - Overall system memory usage and swap pressure
#
# WHY IT'S NECESSARY:
# KDE Plasma has documented memory leaks where these processes can grow from
# ~100MB to 2GB+ over time, causing system instability. This script provides
# automatic remediation before problems occur.
#
# HOW IT WORKS:
# 1. Runs as a systemd user service with configurable check intervals
# 2. Uses ps to monitor process memory usage (RSS - Resident Set Size)
# 3. Uses free to monitor overall system memory pressure
# 4. Gracefully restarts services using killall + kstart
# 5. Logs all activities with timestamps for troubleshooting

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# =============================================================================
# CONFIGURATION SECTION
# These values can be adjusted based on your system's memory capacity and
# performance requirements. Defaults are conservative for 8-16GB systems.
# =============================================================================

# System memory threshold (percentage) - restart Plasma if exceeded
# WHY: High system memory usage indicates overall memory pressure
readonly MEMORY_THRESHOLD=${MEMORY_THRESHOLD:-80}

# Plasma memory threshold (KB) - restart plasmashell if exceeded  
# WHY: plasmashell normally uses 100-300MB, >1.5GB indicates memory leak
readonly PLASMA_MEMORY_THRESHOLD=${PLASMA_MEMORY_THRESHOLD:-1500000}

# KGlobalAccel memory threshold (KB) - restart kglobalacceld if exceeded
# WHY: kglobalacceld normally uses 20-50MB, >1GB indicates severe leak
readonly KGLOBAL_MEMORY_THRESHOLD=${KGLOBAL_MEMORY_THRESHOLD:-1000000}

# KWin memory threshold (KB) - restart kwin if exceeded
# WHY: kwin normally uses 100-300MB, >800MB indicates memory leak or accumulation
readonly KWIN_MEMORY_THRESHOLD=${KWIN_MEMORY_THRESHOLD:-800000}

# Klipper monitoring and replacement
# WHY: Klipper has memory leaks and conflicts with advanced clipboard systems
readonly MONITOR_KLIPPER=${MONITOR_KLIPPER:-true}
readonly KLIPPER_MEMORY_THRESHOLD=${KLIPPER_MEMORY_THRESHOLD:-200000}

# Akonadi service management
# WHY: Akonadi services consume excessive memory and often aren't needed
readonly MONITOR_AKONADI=${MONITOR_AKONADI:-true}
readonly AKONADI_MEMORY_THRESHOLD=${AKONADI_MEMORY_THRESHOLD:-100000}

# System optimization settings
# WHY: Default Fedora settings are too aggressive for desktop use
readonly TARGET_SWAPPINESS=${TARGET_SWAPPINESS:-10}
readonly AUTO_OPTIMIZE_SYSTEM=${AUTO_OPTIMIZE_SYSTEM:-true}

# Check interval (seconds) - how often to monitor memory usage
# WHY: 5 minutes balances responsiveness with system resource usage
readonly CHECK_INTERVAL=${CHECK_INTERVAL:-300}

# Log file location - where to store monitoring and action logs
readonly LOG_FILE="$HOME/.local/share/kde-memory-manager.log"

# Maximum log file size (bytes) - rotate when exceeded
readonly MAX_LOG_SIZE=${MAX_LOG_SIZE:-10485760}  # 10MB

# =============================================================================
# UTILITY FUNCTIONS
# These functions provide logging, process monitoring, and system operations
# =============================================================================

# Logging function with timestamp and structured format
# PARAMETERS: $1 = log message
# OUTPUT: Timestamped log entry to both file and stdout (if interactive)
log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_entry="[$timestamp] $message"
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Write to log file
    echo "$log_entry" >> "$LOG_FILE"
    
    # Also output to stdout if running interactively (for debugging)
    if [[ -t 1 ]]; then
        echo "$log_entry"
    fi
    
    # Rotate log file if it gets too large
    if [[ -f "$LOG_FILE" ]]; then
        local file_size=$(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
        if [[ $file_size -gt $MAX_LOG_SIZE ]]; then
            mv "$LOG_FILE" "${LOG_FILE}.old"
            log_message "Log file rotated due to size limit"
        fi
    fi
}

# Get memory usage for a specific process name
# PARAMETERS: $1 = process name (e.g., "plasmashell")
# OUTPUT: Total memory usage in KB for all matching processes
# RETURNS: 0 if no processes found, sum of RSS values if found
get_process_memory() {
    local process_name="$1"
    
    # Use ps to get RSS (Resident Set Size) for all matching processes
    # RSS is the actual physical memory currently used by the process
    # awk sums all matching processes and returns 0 if none found
    ps -eo pid,rss,comm | grep "$process_name" | grep -v grep | awk '{sum+=$2} END {print sum+0}'
}

# Get current system memory usage percentage
# OUTPUT: Integer percentage of system memory in use
# CALCULATION: (used memory / total memory) * 100
get_system_memory_usage() {
    # Parse /proc/meminfo for accurate memory statistics
    # MemTotal: Total usable RAM
    # MemAvailable: Memory available for new processes (includes cache that can be freed)
    local mem_total=$(grep '^MemTotal:' /proc/meminfo | awk '{print $2}')
    local mem_available=$(grep '^MemAvailable:' /proc/meminfo | awk '{print $2}')
    
    # Calculate used memory and percentage
    local mem_used=$((mem_total - mem_available))
    local usage_percent=$((mem_used * 100 / mem_total))
    
    echo "$usage_percent"
}

# Restart plasmashell with proper error handling and user notification
# WHY: plasmashell is the main KDE desktop shell - needs careful restart
# HOW: Kill existing process, wait for cleanup, start new instance
restart_plasmashell() {
    log_message "Restarting plasmashell due to high memory usage"
    
    # Send desktop notification if notify-send is available
    # This alerts the user that a restart is happening
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "KDE Memory Guardian" "Restarting Plasma Shell to free memory" --icon=dialog-information --urgency=low &
    fi
    
    # Kill all plasmashell processes
    # Using killall is safer than kill -9 as it allows graceful shutdown
    if killall plasmashell 2>/dev/null; then
        log_message "Successfully terminated plasmashell processes"
    else
        log_message "No plasmashell processes found to terminate"
    fi
    
    # Wait for processes to fully terminate
    # This prevents race conditions where new process starts before old one exits
    sleep 2
    
    # Start new plasmashell instance using kstart
    # kstart is the KDE-recommended way to start desktop components
    # Start in background and check if command succeeded
    if kstart plasmashell >/dev/null 2>&1; then
        log_message "Successfully started new plasmashell instance"
    else
        log_message "ERROR: Failed to start new plasmashell instance"
        # Send error notification
        if command -v notify-send >/dev/null 2>&1; then
            notify-send "KDE Memory Guardian" "Failed to restart Plasma Shell - manual intervention required" --icon=dialog-error --urgency=critical &
        fi
    fi
}

# Restart kglobalacceld (global keyboard shortcuts daemon)
# WHY: kglobalacceld handles global keyboard shortcuts - less critical than plasmashell
# HOW: Kill process and let KDE auto-restart it (standard KDE behavior)
restart_kglobalacceld() {
    log_message "Restarting kglobalacceld due to high memory usage"

    # Kill kglobalacceld processes
    if killall kglobalacceld 2>/dev/null; then
        log_message "Successfully terminated kglobalacceld processes"
        # KDE will automatically restart kglobalacceld when needed
        # No manual restart required unlike plasmashell
    else
        log_message "No kglobalacceld processes found to terminate"
    fi
}

# Restart KWin window manager (X11 or Wayland)
# WHY: KWin can accumulate memory from compositor effects, window decorations, and screen edges
# HOW: Use --replace flag for safe restart without losing window state
restart_kwin() {
    log_message "Restarting KWin due to high memory usage"

    # Send desktop notification if notify-send is available
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "KDE Memory Guardian" "Restarting KWin window manager to free memory" --icon=dialog-information --urgency=low &
    fi

    # Detect session type and restart appropriate KWin variant
    if [[ "${XDG_SESSION_TYPE:-x11}" == "wayland" ]]; then
        # Wayland session - restart kwin_wayland
        log_message "Detected Wayland session, restarting kwin_wayland"
        if kwin_wayland --replace >/dev/null 2>&1; then
            log_message "Successfully restarted kwin_wayland"
        else
            log_message "ERROR: Failed to restart kwin_wayland"
        fi
    else
        # X11 session - restart kwin_x11
        log_message "Detected X11 session, restarting kwin_x11"
        if kwin_x11 --replace >/dev/null 2>&1; then
            log_message "Successfully restarted kwin_x11"
        else
            log_message "ERROR: Failed to restart kwin_x11"
        fi
    fi
}

# Optimize system memory settings
# WHY: Default Fedora settings cause excessive swapping on desktop systems
# HOW: Adjust swappiness and other memory management parameters
optimize_system_memory() {
    log_message "Checking system memory optimization settings"

    # Check current swappiness
    local current_swappiness=$(cat /proc/sys/vm/swappiness)

    if [[ $current_swappiness -gt $TARGET_SWAPPINESS ]]; then
        log_message "Current swappiness ($current_swappiness) too high, setting to $TARGET_SWAPPINESS"

        # Set immediately
        if echo "$TARGET_SWAPPINESS" > /proc/sys/vm/swappiness 2>/dev/null; then
            log_message "Successfully set swappiness to $TARGET_SWAPPINESS"
        else
            log_message "WARNING: Could not set swappiness (need root access)"
        fi

        # Make persistent if possible
        local sysctl_file="/etc/sysctl.d/99-kde-memory-guardian.conf"
        if [[ -w "$(dirname "$sysctl_file")" ]] || sudo -n true 2>/dev/null; then
            echo "# KDE Memory Guardian - Optimized memory settings" | sudo tee "$sysctl_file" >/dev/null
            echo "vm.swappiness=$TARGET_SWAPPINESS" | sudo tee -a "$sysctl_file" >/dev/null
            echo "vm.vfs_cache_pressure=50" | sudo tee -a "$sysctl_file" >/dev/null
            echo "vm.dirty_writeback_centisecs=1500" | sudo tee -a "$sysctl_file" >/dev/null
            log_message "Persistent memory optimizations applied to $sysctl_file"
        fi
    fi
}

# Manage Akonadi services
# WHY: Akonadi services often consume excessive memory and may not be needed
# HOW: Monitor memory usage and disable if excessive or unused
manage_akonadi() {
    if [[ "$MONITOR_AKONADI" != "true" ]]; then
        return 0
    fi

    # Get total Akonadi memory usage
    local akonadi_memory=$(get_process_memory "akonadi")

    if [[ $akonadi_memory -gt $AKONADI_MEMORY_THRESHOLD ]]; then
        log_message "ALERT: Akonadi services using ${akonadi_memory}KB > ${AKONADI_MEMORY_THRESHOLD}KB"

        # Check if Akonadi is actually being used
        local akonadi_active=false
        if pgrep -f "kmail\|kontact\|kalendar" >/dev/null 2>&1; then
            akonadi_active=true
        fi

        if [[ "$akonadi_active" == "false" ]]; then
            log_message "Akonadi not actively used, stopping services"

            # Stop Akonadi services
            if command -v akonadictl >/dev/null 2>&1; then
                akonadictl stop 2>/dev/null || true
                log_message "Akonadi services stopped"

                # Send notification
                if command -v notify-send >/dev/null 2>&1; then
                    notify-send "KDE Memory Guardian" \
                        "Stopped Akonadi services (${akonadi_memory}KB freed)" \
                        --icon=dialog-information --urgency=low &
                fi
            fi
        else
            log_message "Akonadi in use by active applications, not stopping"
        fi
    fi
}

# Manage Klipper memory usage and offer replacement
# WHY: Klipper has memory leaks and limited functionality compared to modern alternatives
# HOW: Monitor memory usage and offer to replace with advanced clipboard system
manage_klipper() {
    local klipper_memory="$1"

    # Check if Klipper memory usage is excessive
    if [[ $klipper_memory -gt $KLIPPER_MEMORY_THRESHOLD ]]; then
        log_message "ALERT: Klipper memory usage high: ${klipper_memory}KB > ${KLIPPER_MEMORY_THRESHOLD}KB"

        # Check if replacement script exists
        local replacement_script="$(dirname "${BASH_SOURCE[0]}")/klipper-replacement.sh"
        if [[ -f "$replacement_script" ]]; then
            log_message "Klipper replacement available - consider running: $replacement_script"

            # Send notification about Klipper replacement option
            if command -v notify-send >/dev/null 2>&1; then
                notify-send "KDE Memory Guardian" \
                    "Klipper using ${klipper_memory}KB memory. Advanced clipboard replacement available." \
                    --icon=dialog-information --urgency=normal &
            fi
        else
            log_message "High Klipper memory usage detected but no replacement script found"
        fi
    fi

    # Always log Klipper status for monitoring
    if [[ $klipper_memory -eq 0 ]]; then
        log_message "Klipper not running - advanced clipboard system may be active"
    else
        log_message "Klipper running normally with ${klipper_memory}KB memory usage"
    fi
}

# Clear system caches to free memory
# WHY: When system memory is high, clearing caches can provide immediate relief
# HOW: Use sysctl to drop page cache, dentries, and inodes
clear_system_caches() {
    log_message "Clearing system caches due to high memory usage"
    
    # Sync filesystem to ensure data integrity before clearing caches
    sync
    
    # Clear page cache, dentries and inodes
    # This is safe and will not cause data loss
    # Cache will be rebuilt as needed
    if echo 3 > /proc/sys/vm/drop_caches 2>/dev/null; then
        log_message "Successfully cleared system caches"
    elif command -v sysctl >/dev/null 2>&1; then
        # Fallback method using sysctl (may require sudo)
        if sysctl vm.drop_caches=3 >/dev/null 2>&1; then
            log_message "Successfully cleared system caches using sysctl"
        else
            log_message "WARNING: Could not clear system caches (insufficient permissions)"
        fi
    else
        log_message "WARNING: Could not clear system caches (no method available)"
    fi
}

# =============================================================================
# MAIN MONITORING FUNCTION
# This function performs the actual memory monitoring and takes corrective
# actions when thresholds are exceeded. It's called periodically by the main loop.
# =============================================================================

check_and_manage_memory() {
    # Optimize system settings on first run or periodically
    if [[ "$AUTO_OPTIMIZE_SYSTEM" == "true" ]]; then
        optimize_system_memory
    fi

    # Get current memory statistics
    local system_mem_usage=$(get_system_memory_usage)
    local plasma_memory=$(get_process_memory "plasmashell")
    local kglobal_memory=$(get_process_memory "kglobalacceld")
    local kwin_memory=$(get_process_memory "kwin")
    local klipper_memory=0
    local akonadi_memory=0

    # Check Klipper if monitoring is enabled
    if [[ "$MONITOR_KLIPPER" == "true" ]]; then
        klipper_memory=$(get_process_memory "klipper")
    fi

    # Check Akonadi if monitoring is enabled
    if [[ "$MONITOR_AKONADI" == "true" ]]; then
        akonadi_memory=$(get_process_memory "akonadi")
    fi

    # Log current status for monitoring and debugging
    local log_msg="Memory check - System: ${system_mem_usage}%, Plasma: ${plasma_memory}KB, KGlobal: ${kglobal_memory}KB, KWin: ${kwin_memory}KB"
    if [[ "$MONITOR_KLIPPER" == "true" ]]; then
        log_msg="$log_msg, Klipper: ${klipper_memory}KB"
    fi
    if [[ "$MONITOR_AKONADI" == "true" ]]; then
        log_msg="$log_msg, Akonadi: ${akonadi_memory}KB"
    fi
    log_message "$log_msg"
    
    # Track if any restart actions were taken
    local restart_needed=false
    
    # Check plasmashell memory usage against threshold
    if [[ $plasma_memory -gt $PLASMA_MEMORY_THRESHOLD ]]; then
        log_message "ALERT: Plasmashell memory usage too high: ${plasma_memory}KB > ${PLASMA_MEMORY_THRESHOLD}KB"
        restart_plasmashell
        restart_needed=true
    fi
    
    # Check kglobalacceld memory usage against threshold
    if [[ $kglobal_memory -gt $KGLOBAL_MEMORY_THRESHOLD ]]; then
        log_message "ALERT: kglobalacceld memory usage too high: ${kglobal_memory}KB > ${KGLOBAL_MEMORY_THRESHOLD}KB"
        restart_kglobalacceld
        restart_needed=true
    fi

    # Check KWin memory usage against threshold
    if [[ $kwin_memory -gt $KWIN_MEMORY_THRESHOLD ]]; then
        log_message "ALERT: KWin memory usage too high: ${kwin_memory}KB > ${KWIN_MEMORY_THRESHOLD}KB"
        restart_kwin
        restart_needed=true
    fi

    # Check Klipper if monitoring is enabled
    if [[ "$MONITOR_KLIPPER" == "true" ]] && [[ $klipper_memory -gt 0 ]]; then
        manage_klipper "$klipper_memory"
    fi

    # Check Akonadi services
    if [[ "$MONITOR_AKONADI" == "true" ]]; then
        manage_akonadi
    fi
    
    # Check overall system memory usage
    if [[ $system_mem_usage -gt $MEMORY_THRESHOLD ]]; then
        log_message "ALERT: System memory usage too high: ${system_mem_usage}% > ${MEMORY_THRESHOLD}%"
        
        # If we haven't already restarted plasmashell, do it now
        # High system memory often indicates plasmashell leak even if under individual threshold
        if [[ "$restart_needed" == false ]]; then
            log_message "Restarting plasmashell due to high system memory usage"
            restart_plasmashell
        fi
        
        # Always clear caches when system memory is high
        clear_system_caches
    fi
}

# =============================================================================
# SIGNAL HANDLING AND CLEANUP
# Proper signal handling ensures graceful shutdown and cleanup
# =============================================================================

# Cleanup function called on script exit
cleanup() {
    log_message "KDE Memory Guardian stopped (PID: $$)"
    exit 0
}

# Set up signal handlers for graceful shutdown
# SIGTERM: Standard termination signal from systemd
# SIGINT: Interrupt signal (Ctrl+C) for manual testing
trap cleanup SIGTERM SIGINT

# =============================================================================
# MAIN EXECUTION LOOP
# This is the primary execution path that runs continuously as a service
# =============================================================================

main() {
    # Log startup information for debugging and monitoring
    log_message "KDE Memory Guardian started (PID: $$)"
    log_message "Configuration: Memory threshold: ${MEMORY_THRESHOLD}%, Plasma threshold: ${PLASMA_MEMORY_THRESHOLD}KB, KGlobal threshold: ${KGLOBAL_MEMORY_THRESHOLD}KB"
    log_message "Check interval: ${CHECK_INTERVAL} seconds"
    
    # Perform initial memory check
    check_and_manage_memory
    
    # Main monitoring loop
    # Runs indefinitely until service is stopped or system shuts down
    while true; do
        # Sleep for the configured interval
        # Using sleep allows the script to be interrupted by signals
        sleep "$CHECK_INTERVAL"
        
        # Perform memory check and management
        # Any errors in this function are logged but don't stop the service
        check_and_manage_memory || log_message "ERROR: Memory check failed, continuing monitoring"
    done
}

# =============================================================================
# SCRIPT ENTRY POINT
# Execute main function only if script is run directly (not sourced)
# =============================================================================

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
