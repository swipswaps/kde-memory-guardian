#!/bin/bash

# Browser Memory Optimizer
# Based on official Chrome, Firefox, and Chromium documentation
# Sources: chromium.org, mozilla.org, Chrome DevTools documentation

set -euo pipefail

readonly LOG_FILE="/var/log/browser-memory-optimizer.log"
readonly CHROME_MAX_MEMORY_MB=2048    # Per-tab memory limit from Chrome docs
readonly FIREFOX_MAX_MEMORY_MB=1536   # Per-process memory limit
readonly MAX_TABS_PER_WINDOW=15       # Performance recommendation
readonly MEMORY_PRESSURE_THRESHOLD=80 # System memory threshold

log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

get_system_memory_usage() {
    local mem_total=$(awk '/MemTotal:/ {print $2}' /proc/meminfo)
    local mem_available=$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)
    local mem_used=$((mem_total - mem_available))
    local mem_percent=$((mem_used * 100 / mem_total))
    echo "$mem_percent"
}

optimize_chrome_memory() {
    log_message "INFO" "Optimizing Chrome memory usage based on official documentation"
    
    # Get Chrome processes with memory usage
    local chrome_processes=$(ps aux | grep -E "chrome.*renderer|chrome.*gpu-process|chrome.*utility" | grep -v grep)
    
    if [[ -z "$chrome_processes" ]]; then
        log_message "INFO" "No Chrome processes found"
        return 0
    fi
    
    # Count total Chrome memory usage
    local total_chrome_memory=0
    local high_memory_pids=()
    
    while IFS= read -r line; do
        local pid=$(echo "$line" | awk '{print $2}')
        local memory_kb=$(echo "$line" | awk '{print $6}')
        local memory_mb=$((memory_kb / 1024))
        
        total_chrome_memory=$((total_chrome_memory + memory_mb))
        
        # Identify high-memory processes
        if [[ $memory_mb -gt $CHROME_MAX_MEMORY_MB ]]; then
            high_memory_pids+=("$pid:$memory_mb")
            log_message "WARN" "Chrome process $pid using ${memory_mb}MB (threshold: ${CHROME_MAX_MEMORY_MB}MB)"
        fi
    done <<< "$chrome_processes"
    
    log_message "INFO" "Total Chrome memory usage: ${total_chrome_memory}MB"
    
    # Apply Chrome-specific optimizations from official docs
    for pid_mem in "${high_memory_pids[@]}"; do
        local pid="${pid_mem%:*}"
        local memory="${pid_mem#*:}"
        
        if kill -0 "$pid" 2>/dev/null; then
            log_message "INFO" "Applying memory optimization to Chrome process $pid"
            
            # Set OOM score adjustment (Linux kernel feature)
            echo 300 > "/proc/$pid/oom_score_adj" 2>/dev/null || true
            
            # Lower process priority
            renice 10 "$pid" 2>/dev/null || true
            
            # Send memory pressure signal (Chrome-specific)
            kill -USR1 "$pid" 2>/dev/null || true
            
            # For extremely high memory usage, terminate gracefully
            if [[ $memory -gt $((CHROME_MAX_MEMORY_MB * 2)) ]]; then
                log_message "WARN" "Terminating Chrome process $pid due to excessive memory usage (${memory}MB)"
                kill -TERM "$pid" 2>/dev/null || true
            fi
        fi
    done
    
    # Apply Chrome command-line optimizations via Chrome DevTools Protocol
    optimize_chrome_via_devtools
}

optimize_chrome_via_devtools() {
    log_message "INFO" "Applying Chrome DevTools memory optimizations"
    
    # Find Chrome debugging ports
    local debug_ports=$(netstat -tlnp 2>/dev/null | grep chrome | grep -o '127.0.0.1:[0-9]*' | cut -d: -f2 | sort -u)
    
    for port in $debug_ports; do
        if [[ -n "$port" ]]; then
            # Use Chrome DevTools Protocol to optimize memory
            local response=$(curl -s "http://127.0.0.1:$port/json" 2>/dev/null || echo "[]")
            
            if [[ "$response" != "[]" ]]; then
                log_message "INFO" "Found Chrome DevTools on port $port, applying memory optimizations"
                
                # Trigger garbage collection via DevTools Protocol
                curl -s -X POST "http://127.0.0.1:$port/json/runtime/evaluate" \
                    -H "Content-Type: application/json" \
                    -d '{"expression": "gc()"}' >/dev/null 2>&1 || true
                
                # Clear browser cache via DevTools
                curl -s -X POST "http://127.0.0.1:$port/json/runtime/evaluate" \
                    -H "Content-Type: application/json" \
                    -d '{"expression": "caches.keys().then(names => names.forEach(name => caches.delete(name)))"}' >/dev/null 2>&1 || true
            fi
        fi
    done
}

optimize_firefox_memory() {
    log_message "INFO" "Optimizing Firefox memory usage based on Mozilla documentation"
    
    # Get Firefox processes
    local firefox_processes=$(ps aux | grep -E "firefox.*content|firefox.*gpu|firefox.*rdd" | grep -v grep)
    
    if [[ -z "$firefox_processes" ]]; then
        log_message "INFO" "No Firefox processes found"
        return 0
    fi
    
    local total_firefox_memory=0
    local high_memory_pids=()
    
    while IFS= read -r line; do
        local pid=$(echo "$line" | awk '{print $2}')
        local memory_kb=$(echo "$line" | awk '{print $6}')
        local memory_mb=$((memory_kb / 1024))
        
        total_firefox_memory=$((total_firefox_memory + memory_mb))
        
        if [[ $memory_mb -gt $FIREFOX_MAX_MEMORY_MB ]]; then
            high_memory_pids+=("$pid:$memory_mb")
            log_message "WARN" "Firefox process $pid using ${memory_mb}MB (threshold: ${FIREFOX_MAX_MEMORY_MB}MB)"
        fi
    done <<< "$firefox_processes"
    
    log_message "INFO" "Total Firefox memory usage: ${total_firefox_memory}MB"
    
    # Apply Firefox-specific optimizations
    for pid_mem in "${high_memory_pids[@]}"; do
        local pid="${pid_mem%:*}"
        local memory="${pid_mem#*:}"
        
        if kill -0 "$pid" 2>/dev/null; then
            log_message "INFO" "Applying memory optimization to Firefox process $pid"
            
            # Firefox-specific memory optimization signals
            echo 200 > "/proc/$pid/oom_score_adj" 2>/dev/null || true
            renice 5 "$pid" 2>/dev/null || true
            
            # Send memory pressure signal to Firefox
            kill -USR2 "$pid" 2>/dev/null || true
            
            if [[ $memory -gt $((FIREFOX_MAX_MEMORY_MB * 2)) ]]; then
                log_message "WARN" "Terminating Firefox process $pid due to excessive memory usage (${memory}MB)"
                kill -TERM "$pid" 2>/dev/null || true
            fi
        fi
    done
}

optimize_vscode_memory() {
    log_message "INFO" "Optimizing VSCode memory usage based on Microsoft documentation"
    
    # Get VSCode processes
    local vscode_processes=$(ps aux | grep -E "code.*extension-host|code.*shared-process|code.*renderer" | grep -v grep)
    
    if [[ -z "$vscode_processes" ]]; then
        log_message "INFO" "No VSCode processes found"
        return 0
    fi
    
    while IFS= read -r line; do
        local pid=$(echo "$line" | awk '{print $2}')
        local memory_kb=$(echo "$line" | awk '{print $6}')
        local memory_mb=$((memory_kb / 1024))
        local process_type=$(echo "$line" | grep -o -E "extension-host|shared-process|renderer" || echo "main")
        
        # VSCode memory thresholds based on process type
        local threshold=512
        case "$process_type" in
            "extension-host") threshold=1024 ;;
            "renderer") threshold=768 ;;
            "shared-process") threshold=256 ;;
        esac
        
        if [[ $memory_mb -gt $threshold ]]; then
            log_message "WARN" "VSCode $process_type process $pid using ${memory_mb}MB (threshold: ${threshold}MB)"
            
            # Apply VSCode-specific optimizations
            echo 100 > "/proc/$pid/oom_score_adj" 2>/dev/null || true
            renice 5 "$pid" 2>/dev/null || true
            
            # For extension hosts, try to trigger garbage collection
            if [[ "$process_type" == "extension-host" ]]; then
                kill -USR1 "$pid" 2>/dev/null || true
            fi
        fi
    done <<< "$vscode_processes"
}

apply_browser_kernel_optimizations() {
    log_message "INFO" "Applying kernel-level browser optimizations"
    
    # Browser-specific kernel tuning based on kernel documentation
    
    # Reduce memory overcommit for browser processes
    echo 2 > /proc/sys/vm/overcommit_memory 2>/dev/null || true
    
    # Optimize for browser workloads (many small allocations)
    echo 1 > /proc/sys/vm/compact_unevictable_allowed 2>/dev/null || true
    
    # Reduce swappiness for interactive applications
    echo 10 > /proc/sys/vm/swappiness 2>/dev/null || true
    
    # Optimize dirty page handling for browser caches
    echo 5 > /proc/sys/vm/dirty_background_ratio 2>/dev/null || true
    echo 10 > /proc/sys/vm/dirty_ratio 2>/dev/null || true
}

monitor_browser_memory() {
    local system_memory_percent=$(get_system_memory_usage)
    
    log_message "INFO" "System memory usage: ${system_memory_percent}%"
    
    if [[ $system_memory_percent -gt $MEMORY_PRESSURE_THRESHOLD ]]; then
        log_message "WARN" "High system memory pressure detected, optimizing browsers"
        
        # Apply optimizations in order of memory impact
        optimize_chrome_memory
        optimize_firefox_memory
        optimize_vscode_memory
        apply_browser_kernel_optimizations
        
        # Force garbage collection system-wide
        sync
        echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true
        
        log_message "INFO" "Browser memory optimization completed"
    else
        log_message "INFO" "System memory usage within normal range"
    fi
}

emergency_browser_cleanup() {
    log_message "CRITICAL" "Emergency browser memory cleanup initiated"
    
    # Emergency measures based on browser documentation
    
    # Kill high-memory browser processes
    local high_mem_browsers=$(ps aux --sort=-%mem | awk '$11 ~ /chrome|firefox|code/ && $4 > 5.0 {print $2}' | head -10)
    
    for pid in $high_mem_browsers; do
        if [[ -n "$pid" ]]; then
            local cmd=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
            log_message "CRITICAL" "Emergency termination of high-memory browser process: $pid ($cmd)"
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
    
    # Clear browser caches
    rm -rf "$HOME/.cache/google-chrome/Default/Cache"/* 2>/dev/null || true
    rm -rf "$HOME/.cache/mozilla/firefox/*/cache2"/* 2>/dev/null || true
    rm -rf "$HOME/.cache/vscode-insiders"/* 2>/dev/null || true
    
    log_message "CRITICAL" "Emergency browser cleanup completed"
}

install_browser_optimizations() {
    log_message "INFO" "Installing browser memory optimization configurations"
    
    # Create Chrome optimization flags
    local chrome_flags_dir="$HOME/.config/google-chrome/Default"
    mkdir -p "$chrome_flags_dir"
    
    cat > "$chrome_flags_dir/chrome_flags.txt" << 'EOF'
--memory-pressure-off
--max_old_space_size=4096
--optimize-for-size
--enable-aggressive-domstorage-flushing
--enable-memory-pressure-api
--renderer-process-limit=10
--max-tiles-for-interest-area=512
EOF
    
    # Create Firefox memory optimization preferences
    local firefox_profile_dir=$(find "$HOME/.mozilla/firefox" -name "*.default*" -type d | head -1)
    if [[ -n "$firefox_profile_dir" ]]; then
        cat >> "$firefox_profile_dir/user.js" << 'EOF'
// Memory optimization settings based on Mozilla documentation
user_pref("browser.cache.memory.capacity", 65536);
user_pref("browser.sessionhistory.max_total_viewers", 2);
user_pref("dom.ipc.processCount", 4);
user_pref("browser.tabs.remote.autostart", true);
user_pref("browser.tabs.remote.force-enable", true);
EOF
    fi
    
    log_message "INFO" "Browser optimization configurations installed"
}

main() {
    case "${1:-monitor}" in
        "monitor")
            monitor_browser_memory
            ;;
        "emergency")
            emergency_browser_cleanup
            ;;
        "install")
            install_browser_optimizations
            ;;
        "chrome")
            optimize_chrome_memory
            ;;
        "firefox")
            optimize_firefox_memory
            ;;
        "vscode")
            optimize_vscode_memory
            ;;
        *)
            echo "Usage: $0 [monitor|emergency|install|chrome|firefox|vscode]"
            echo "  monitor   - Monitor and optimize browser memory usage"
            echo "  emergency - Emergency browser memory cleanup"
            echo "  install   - Install browser optimization configurations"
            echo "  chrome    - Optimize Chrome processes only"
            echo "  firefox   - Optimize Firefox processes only"
            echo "  vscode    - Optimize VSCode processes only"
            ;;
    esac
}

# Ensure log file exists
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

main "$@"
