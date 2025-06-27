#!/bin/bash

# Automated Memory Guardian - Master Controller
# Coordinates all memory management tools with intelligent decision making
# Based on official documentation and best practices from multiple sources

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/automated-memory-guardian.log"
readonly CONFIG_FILE="$HOME/.config/automated-memory-guardian.conf"
readonly LOCK_FILE="/tmp/memory-guardian.lock"

# Load configuration or set defaults
if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    # Default configuration based on best practices
    MONITOR_INTERVAL=30           # seconds
    CRITICAL_MEMORY_THRESHOLD=90  # %
    HIGH_MEMORY_THRESHOLD=80      # %
    SWAP_THRESHOLD=70            # %
    PRESSURE_THRESHOLD=50        # PSI threshold
    ENABLE_BROWSER_OPTIMIZATION=true
    ENABLE_KDE_OPTIMIZATION=true
    ENABLE_EMERGENCY_ACTIONS=true
    ENABLE_PROACTIVE_CLEANUP=true
fi

log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

acquire_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        local lock_pid=$(cat "$LOCK_FILE" 2>/dev/null || echo "")
        if [[ -n "$lock_pid" ]] && kill -0 "$lock_pid" 2>/dev/null; then
            log_message "INFO" "Another instance is running (PID: $lock_pid), exiting"
            exit 0
        else
            log_message "WARN" "Stale lock file found, removing"
            rm -f "$LOCK_FILE"
        fi
    fi
    echo $$ > "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"; exit' INT TERM EXIT
}

get_comprehensive_memory_stats() {
    # Get detailed memory statistics
    local mem_total=$(awk '/MemTotal:/ {print $2}' /proc/meminfo)
    local mem_available=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
    local swap_total=$(awk '/SwapTotal:/ {print $2}' /proc/meminfo)
    local swap_free=$(awk '/SwapFree:/ {print $2}' /proc/meminfo)
    local buffers=$(awk '/Buffers:/ {print $2}' /proc/meminfo)
    local cached=$(awk '/^Cached:/ {print $2}' /proc/meminfo)
    
    local mem_used=$((mem_total - mem_available))
    local swap_used=$((swap_total - swap_free))
    
    local mem_percent=$((mem_used * 100 / mem_total))
    local swap_percent=0
    [[ $swap_total -gt 0 ]] && swap_percent=$((swap_used * 100 / swap_total))
    
    # Get memory pressure if available
    local pressure_some=0
    local pressure_full=0
    if [[ -f /proc/pressure/memory ]]; then
        pressure_some=$(awk '/some/ {gsub(/avg10=/, "", $2); print $2}' /proc/pressure/memory)
        pressure_full=$(awk '/full/ {gsub(/avg10=/, "", $2); print $2}' /proc/pressure/memory)
    fi
    
    echo "$mem_percent $swap_percent $mem_used $swap_used $pressure_some $pressure_full $buffers $cached"
}

analyze_memory_situation() {
    local stats=($(get_comprehensive_memory_stats))
    local mem_percent=${stats[0]}
    local swap_percent=${stats[1]}
    local pressure_some=${stats[4]}
    local pressure_full=${stats[5]}
    
    # Determine severity level based on multiple factors
    local severity="normal"
    
    if [[ $mem_percent -gt $CRITICAL_MEMORY_THRESHOLD ]] || [[ $swap_percent -gt $SWAP_THRESHOLD ]]; then
        severity="critical"
    elif [[ $mem_percent -gt $HIGH_MEMORY_THRESHOLD ]] || [[ $(echo "$pressure_some > $PRESSURE_THRESHOLD" | bc -l 2>/dev/null || echo 0) -eq 1 ]]; then
        severity="high"
    elif [[ $mem_percent -gt 60 ]] || [[ $(echo "$pressure_some > 10" | bc -l 2>/dev/null || echo 0) -eq 1 ]]; then
        severity="moderate"
    fi
    
    echo "$severity"
}

get_top_memory_consumers() {
    # Get top 10 memory consuming processes with detailed info
    ps aux --sort=-%mem | head -11 | tail -10 | while read line; do
        local pid=$(echo "$line" | awk '{print $2}')
        local mem_percent=$(echo "$line" | awk '{print $4}')
        local command=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
        echo "$pid:$mem_percent:$command"
    done
}

execute_optimization_strategy() {
    local severity="$1"
    local stats=($(get_comprehensive_memory_stats))
    
    log_message "INFO" "Executing $severity severity optimization strategy"
    log_message "INFO" "Memory: ${stats[0]}%, Swap: ${stats[1]}%, Pressure: ${stats[4]}/${stats[5]}"
    
    case "$severity" in
        "critical")
            execute_critical_response "${stats[@]}"
            ;;
        "high")
            execute_high_response "${stats[@]}"
            ;;
        "moderate")
            execute_moderate_response "${stats[@]}"
            ;;
        "normal")
            execute_normal_maintenance "${stats[@]}"
            ;;
    esac
}

execute_critical_response() {
    log_message "CRITICAL" "Critical memory situation detected - executing emergency procedures"
    
    # Emergency response based on official documentation
    
    # 1. Immediate kernel-level interventions
    "$SCRIPT_DIR/intelligent-memory-guardian.sh" emergency
    
    # 2. Browser emergency cleanup
    if [[ "$ENABLE_BROWSER_OPTIMIZATION" == "true" ]]; then
        "$SCRIPT_DIR/browser-memory-optimizer.sh" emergency
    fi
    
    # 3. KDE emergency cleanup
    if [[ "$ENABLE_KDE_OPTIMIZATION" == "true" ]]; then
        "$SCRIPT_DIR/kde-memory-optimizer.sh" emergency
    fi
    
    # 4. Force memory reclaim
    sync
    echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
    
    # 5. Restart memory protection services
    systemctl restart earlyoom.service 2>/dev/null || true
    systemctl restart nohang.service 2>/dev/null || true
    
    log_message "CRITICAL" "Emergency procedures completed"
}

execute_high_response() {
    log_message "WARN" "High memory pressure detected - applying comprehensive optimizations"
    
    # High-priority optimizations
    
    # 1. Intelligent memory management
    "$SCRIPT_DIR/intelligent-memory-guardian.sh" monitor
    
    # 2. Browser optimization
    if [[ "$ENABLE_BROWSER_OPTIMIZATION" == "true" ]]; then
        "$SCRIPT_DIR/browser-memory-optimizer.sh" monitor
    fi
    
    # 3. KDE optimization
    if [[ "$ENABLE_KDE_OPTIMIZATION" == "true" ]]; then
        "$SCRIPT_DIR/kde-memory-optimizer.sh" monitor
    fi
    
    # 4. Selective cache clearing
    if [[ "$ENABLE_PROACTIVE_CLEANUP" == "true" ]]; then
        echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true
    fi
    
    log_message "WARN" "High-priority optimizations completed"
}

execute_moderate_response() {
    log_message "INFO" "Moderate memory pressure detected - applying preventive measures"
    
    # Preventive optimizations
    
    # 1. Browser optimization only
    if [[ "$ENABLE_BROWSER_OPTIMIZATION" == "true" ]]; then
        "$SCRIPT_DIR/browser-memory-optimizer.sh" monitor
    fi
    
    # 2. KDE maintenance
    if [[ "$ENABLE_KDE_OPTIMIZATION" == "true" ]]; then
        "$SCRIPT_DIR/kde-memory-optimizer.sh" plasma
    fi
    
    # 3. Gentle memory pressure relief
    echo 60 > /proc/sys/vm/swappiness 2>/dev/null || true
    
    log_message "INFO" "Preventive measures completed"
}

execute_normal_maintenance() {
    log_message "INFO" "Normal memory usage - performing routine maintenance"
    
    # Routine maintenance
    
    # 1. Check service status
    "$SCRIPT_DIR/unified-memory-manager.sh" status
    
    # 2. Light cleanup if enabled
    if [[ "$ENABLE_PROACTIVE_CLEANUP" == "true" ]]; then
        # Clear only page cache, keep dentries and inodes
        echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true
    fi
    
    log_message "INFO" "Routine maintenance completed"
}

generate_memory_report() {
    local stats=($(get_comprehensive_memory_stats))
    local top_consumers=($(get_top_memory_consumers))
    
    cat << EOF
=== MEMORY GUARDIAN REPORT ===
Timestamp: $(date)
Memory Usage: ${stats[0]}%
Swap Usage: ${stats[1]}%
Memory Pressure: ${stats[4]}/${stats[5]}
Buffers: $((${stats[6]} / 1024))MB
Cache: $((${stats[7]} / 1024))MB

Top Memory Consumers:
EOF
    
    for consumer in "${top_consumers[@]}"; do
        local pid="${consumer%%:*}"
        local rest="${consumer#*:}"
        local mem_percent="${rest%%:*}"
        local command="${rest#*:}"
        echo "  PID $pid: ${mem_percent}% - $command"
    done
    
    echo ""
    echo "Services Status:"
    systemctl is-active earlyoom.service && echo "  ✅ earlyoom: ACTIVE" || echo "  ❌ earlyoom: INACTIVE"
    systemctl is-active nohang.service && echo "  ✅ nohang: ACTIVE" || echo "  ❌ nohang: INACTIVE"
    systemctl is-active systemd-oomd.service && echo "  ✅ systemd-oomd: ACTIVE" || echo "  ❌ systemd-oomd: INACTIVE"
}

continuous_monitoring() {
    log_message "INFO" "Starting continuous memory monitoring (interval: ${MONITOR_INTERVAL}s)"
    
    while true; do
        local severity=$(analyze_memory_situation)
        execute_optimization_strategy "$severity"
        
        # Generate report every 10 cycles for normal/moderate, every cycle for high/critical
        if [[ "$severity" == "critical" ]] || [[ "$severity" == "high" ]] || [[ $(($(date +%s) % 300)) -eq 0 ]]; then
            generate_memory_report >> "$LOG_FILE"
        fi
        
        sleep "$MONITOR_INTERVAL"
    done
}

install_automation() {
    log_message "INFO" "Installing automated memory guardian"
    
    # Make all scripts executable
    chmod +x "$SCRIPT_DIR"/*.sh
    
    # Install individual components
    "$SCRIPT_DIR/intelligent-memory-guardian.sh" install
    "$SCRIPT_DIR/browser-memory-optimizer.sh" install
    "$SCRIPT_DIR/kde-memory-optimizer.sh" install
    
    # Create systemd service for continuous monitoring
    cat > /tmp/automated-memory-guardian.service << EOF
[Unit]
Description=Automated Memory Guardian
After=multi-user.target

[Service]
Type=simple
ExecStart=$SCRIPT_DIR/automated-memory-guardian.sh monitor
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    sudo mv /tmp/automated-memory-guardian.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable automated-memory-guardian.service
    
    # Create configuration file
    cat > "$CONFIG_FILE" << EOF
# Automated Memory Guardian Configuration
MONITOR_INTERVAL=30
CRITICAL_MEMORY_THRESHOLD=90
HIGH_MEMORY_THRESHOLD=80
SWAP_THRESHOLD=70
PRESSURE_THRESHOLD=50
ENABLE_BROWSER_OPTIMIZATION=true
ENABLE_KDE_OPTIMIZATION=true
ENABLE_EMERGENCY_ACTIONS=true
ENABLE_PROACTIVE_CLEANUP=true
EOF
    
    log_message "INFO" "Automated memory guardian installed successfully"
}

main() {
    case "${1:-monitor}" in
        "install")
            install_automation
            ;;
        "monitor")
            acquire_lock
            continuous_monitoring
            ;;
        "once")
            acquire_lock
            local severity=$(analyze_memory_situation)
            execute_optimization_strategy "$severity"
            generate_memory_report
            ;;
        "report")
            generate_memory_report
            ;;
        "emergency")
            acquire_lock
            execute_critical_response
            ;;
        *)
            echo "Usage: $0 [install|monitor|once|report|emergency]"
            echo "  install   - Install automated memory guardian system"
            echo "  monitor   - Start continuous monitoring (default)"
            echo "  once      - Run single optimization cycle"
            echo "  report    - Generate memory usage report"
            echo "  emergency - Force emergency memory recovery"
            ;;
    esac
}

# Ensure log directory exists
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo touch "$LOG_FILE"
sudo chmod 666 "$LOG_FILE"

main "$@"
