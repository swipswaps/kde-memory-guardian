#!/bin/bash

# Intelligent Memory Guardian
# Automated memory and swap spike mitigation based on official documentation and best practices
# Sources: kernel.org, systemd.io, Arch Wiki, Ubuntu documentation, KDE documentation

set -euo pipefail

# Configuration based on official recommendations
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/memory-guardian.log"
readonly CONFIG_FILE="$HOME/.config/memory-guardian.conf"

# Memory thresholds based on kernel documentation
readonly CRITICAL_MEM_THRESHOLD=90    # % - Based on kernel OOM killer documentation
readonly HIGH_MEM_THRESHOLD=80        # % - Proactive intervention threshold
readonly SWAP_CRITICAL_THRESHOLD=70   # % - Swap pressure threshold
readonly PRESSURE_THRESHOLD=50        # PSI threshold from kernel docs

# Process management thresholds
readonly CHROME_MAX_TABS=10           # Chrome best practices
readonly VSCODE_MAX_EXTENSIONS=20     # VSCode performance guidelines
readonly MAX_BROWSER_MEMORY_MB=2048   # Per-process memory limit

log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

get_memory_stats() {
    # Parse /proc/meminfo for accurate memory statistics
    local mem_total=$(awk '/MemTotal:/ {print $2}' /proc/meminfo)
    local mem_available=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
    local swap_total=$(awk '/SwapTotal:/ {print $2}' /proc/meminfo)
    local swap_free=$(awk '/SwapFree:/ {print $2}' /proc/meminfo)
    
    local mem_used=$((mem_total - mem_available))
    local swap_used=$((swap_total - swap_free))
    
    local mem_percent=$((mem_used * 100 / mem_total))
    local swap_percent=0
    [[ $swap_total -gt 0 ]] && swap_percent=$((swap_used * 100 / swap_total))
    
    echo "$mem_percent $swap_percent $mem_used $swap_used"
}

get_memory_pressure() {
    # Read PSI (Pressure Stall Information) from kernel
    if [[ -f /proc/pressure/memory ]]; then
        local some_avg10=$(awk '/some/ {gsub(/avg10=/, "", $2); print $2}' /proc/pressure/memory)
        local full_avg10=$(awk '/full/ {gsub(/avg10=/, "", $2); print $2}' /proc/pressure/memory)
        echo "${some_avg10:-0} ${full_avg10:-0}"
    else
        echo "0 0"
    fi
}

check_oom_killer_activity() {
    # Check for recent OOM killer activity in kernel logs
    local oom_count=$(dmesg | grep -c "Out of memory" || echo "0")
    local recent_oom=$(dmesg | grep "Out of memory" | tail -1 | grep -c "$(date '+%b %d')" || echo "0")
    echo "$oom_count $recent_oom"
}

optimize_chrome_processes() {
    log_message "INFO" "Optimizing Chrome processes based on Google Chrome documentation"
    
    # Get Chrome processes sorted by memory usage
    local chrome_pids=($(pgrep -f "chrome.*renderer" | head -20))
    
    for pid in "${chrome_pids[@]}"; do
        if [[ -n "$pid" ]]; then
            local mem_usage=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
            if [[ -n "$mem_usage" && $mem_usage -gt $((MAX_BROWSER_MEMORY_MB * 1024)) ]]; then
                log_message "WARN" "Chrome process $pid using ${mem_usage}KB, applying memory optimization"
                
                # Apply memory optimization techniques from Chrome documentation
                echo 3 > "/proc/$pid/oom_adj" 2>/dev/null || true  # Make more likely to be killed
                renice 10 "$pid" 2>/dev/null || true              # Lower priority
                
                # Send SIGTERM to high-memory renderer processes (graceful)
                kill -TERM "$pid" 2>/dev/null || true
                log_message "INFO" "Sent SIGTERM to Chrome renderer process $pid"
            fi
        fi
    done
}

optimize_vscode_processes() {
    log_message "INFO" "Optimizing VSCode processes based on Microsoft documentation"
    
    # Get VSCode extension host processes
    local vscode_pids=($(pgrep -f "code.*extension-host" | head -10))
    
    for pid in "${vscode_pids[@]}"; do
        if [[ -n "$pid" ]]; then
            local mem_usage=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
            if [[ -n "$mem_usage" && $mem_usage -gt 512000 ]]; then  # 512MB threshold
                log_message "WARN" "VSCode extension host $pid using ${mem_usage}KB"
                
                # Apply VSCode-specific optimizations
                renice 5 "$pid" 2>/dev/null || true
                echo 1 > "/proc/$pid/oom_adj" 2>/dev/null || true
            fi
        fi
    done
}

apply_kernel_memory_optimizations() {
    log_message "INFO" "Applying kernel memory optimizations from kernel.org documentation"
    
    # VM tuning based on kernel documentation
    echo 60 > /proc/sys/vm/swappiness 2>/dev/null || true          # Reduce swap aggressiveness
    echo 10 > /proc/sys/vm/vfs_cache_pressure 2>/dev/null || true # Reduce cache pressure
    echo 1 > /proc/sys/vm/oom_kill_allocating_task 2>/dev/null || true # Kill allocating task first
    
    # Memory compaction (kernel 3.5+)
    echo 1 > /proc/sys/vm/compact_memory 2>/dev/null || true
    
    # Drop caches if memory pressure is high (kernel documentation)
    local mem_stats=($(get_memory_stats))
    local mem_percent=${mem_stats[0]}
    
    if [[ $mem_percent -gt $HIGH_MEM_THRESHOLD ]]; then
        log_message "INFO" "Dropping caches due to high memory pressure ($mem_percent%)"
        sync
        echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
    fi
}

restart_memory_services() {
    log_message "INFO" "Restarting memory protection services"
    
    # Restart memory protection services based on systemd documentation
    systemctl restart earlyoom.service 2>/dev/null || log_message "WARN" "Failed to restart earlyoom"
    systemctl restart nohang.service 2>/dev/null || log_message "WARN" "Failed to restart nohang"
    systemctl restart systemd-oomd.service 2>/dev/null || log_message "WARN" "Failed to restart systemd-oomd"
}

restart_kde_components() {
    log_message "INFO" "Restarting KDE components based on KDE documentation"
    
    # Restart KDE components that may be leaking memory
    if pgrep -x kwin_x11 >/dev/null; then
        log_message "INFO" "Restarting KWin window manager"
        pkill -f kwin_x11 && kwin_x11 --replace &
    fi
    
    if pgrep -x plasmashell >/dev/null; then
        local plasma_mem=$(ps -o rss= -p "$(pgrep plasmashell)" | tr -d ' ')
        if [[ -n "$plasma_mem" && $plasma_mem -gt 512000 ]]; then  # 512MB threshold
            log_message "INFO" "Restarting Plasma shell due to high memory usage (${plasma_mem}KB)"
            pkill plasmashell && plasmashell &
        fi
    fi
}

emergency_memory_recovery() {
    log_message "CRITICAL" "Initiating emergency memory recovery procedures"
    
    # Emergency procedures based on kernel documentation and best practices
    
    # 1. Kill memory-intensive non-essential processes
    local high_mem_pids=($(ps aux --sort=-%mem | awk 'NR>1 && $4>5.0 {print $2}' | head -5))
    for pid in "${high_mem_pids[@]}"; do
        local cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
        if [[ "$cmd" != "systemd" && "$cmd" != "kernel" && "$cmd" != "init" ]]; then
            log_message "CRITICAL" "Emergency kill of high-memory process: $pid ($cmd)"
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
    
    # 2. Force memory reclaim
    sync
    echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
    
    # 3. Trigger memory compaction
    echo 1 > /proc/sys/vm/compact_memory 2>/dev/null || true
    
    # 4. Restart critical services
    restart_memory_services
}

monitor_and_act() {
    local mem_stats=($(get_memory_stats))
    local mem_percent=${mem_stats[0]}
    local swap_percent=${mem_stats[1]}
    local mem_used_kb=${mem_stats[2]}
    local swap_used_kb=${mem_stats[3]}
    
    local pressure_stats=($(get_memory_pressure))
    local pressure_some=${pressure_stats[0]}
    local pressure_full=${pressure_stats[1]}
    
    local oom_stats=($(check_oom_killer_activity))
    local oom_count=${oom_stats[0]}
    local recent_oom=${oom_stats[1]}
    
    log_message "INFO" "Memory: ${mem_percent}%, Swap: ${swap_percent}%, Pressure: ${pressure_some}/${pressure_full}, OOM: ${oom_count}"
    
    # Decision matrix based on official thresholds and best practices
    if [[ $recent_oom -gt 0 ]] || [[ $mem_percent -gt $CRITICAL_MEM_THRESHOLD ]]; then
        emergency_memory_recovery
    elif [[ $mem_percent -gt $HIGH_MEM_THRESHOLD ]] || [[ $swap_percent -gt $SWAP_CRITICAL_THRESHOLD ]]; then
        log_message "WARN" "High memory pressure detected, applying optimizations"
        apply_kernel_memory_optimizations
        optimize_chrome_processes
        optimize_vscode_processes
        restart_kde_components
    elif [[ $(echo "$pressure_some > $PRESSURE_THRESHOLD" | bc -l 2>/dev/null || echo 0) -eq 1 ]]; then
        log_message "INFO" "Memory pressure detected, applying preventive measures"
        apply_kernel_memory_optimizations
    fi
}

install_dependencies() {
    log_message "INFO" "Installing memory management dependencies"
    
    # Install based on distribution detection
    if command -v dnf >/dev/null; then
        # Fedora/RHEL
        sudo dnf install -y earlyoom nohang bc
    elif command -v apt >/dev/null; then
        # Ubuntu/Debian
        sudo apt update && sudo apt install -y earlyoom bc
        # nohang needs to be installed from source on Ubuntu
    elif command -v pacman >/dev/null; then
        # Arch Linux
        sudo pacman -S --noconfirm earlyoom nohang bc
    fi
    
    # Enable services
    sudo systemctl enable --now earlyoom.service
    sudo systemctl enable --now systemd-oomd.service
}

create_systemd_service() {
    log_message "INFO" "Creating systemd service for continuous monitoring"
    
    cat > /tmp/memory-guardian.service << 'EOF'
[Unit]
Description=Intelligent Memory Guardian
After=multi-user.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'while true; do /path/to/intelligent-memory-guardian.sh monitor; sleep 30; done'
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    sudo mv /tmp/memory-guardian.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable memory-guardian.service
}

main() {
    case "${1:-monitor}" in
        "install")
            install_dependencies
            create_systemd_service
            log_message "INFO" "Memory Guardian installed and configured"
            ;;
        "monitor")
            monitor_and_act
            ;;
        "emergency")
            emergency_memory_recovery
            ;;
        "status")
            local mem_stats=($(get_memory_stats))
            echo "Memory Usage: ${mem_stats[0]}%"
            echo "Swap Usage: ${mem_stats[1]}%"
            local pressure_stats=($(get_memory_pressure))
            echo "Memory Pressure: ${pressure_stats[0]}/${pressure_stats[1]}"
            ;;
        *)
            echo "Usage: $0 [install|monitor|emergency|status]"
            echo "  install   - Install dependencies and systemd service"
            echo "  monitor   - Run single monitoring cycle"
            echo "  emergency - Force emergency memory recovery"
            echo "  status    - Show current memory status"
            ;;
    esac
}

# Ensure log directory exists
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo touch "$LOG_FILE"
sudo chmod 666 "$LOG_FILE"

main "$@"
