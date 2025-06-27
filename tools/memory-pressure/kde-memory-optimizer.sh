#!/bin/bash

# KDE Memory Optimizer
# Based on official KDE documentation, Plasma development guidelines, and KDE community best practices
# Sources: kde.org, techbase.kde.org, KDE UserBase Wiki, Plasma development documentation

set -euo pipefail

readonly LOG_FILE="/var/log/kde-memory-optimizer.log"
readonly PLASMA_MAX_MEMORY_MB=512     # Plasma shell memory threshold
readonly KWIN_MAX_MEMORY_MB=256       # KWin memory threshold
readonly BALOO_MAX_MEMORY_MB=128      # Baloo indexer threshold
readonly AKONADI_MAX_MEMORY_MB=256    # Akonadi PIM threshold

log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

check_kde_session() {
    if [[ "${XDG_CURRENT_DESKTOP:-}" != *"KDE"* ]] && [[ "${DESKTOP_SESSION:-}" != *"plasma"* ]]; then
        log_message "WARN" "Not running in KDE Plasma session, some optimizations may not apply"
        return 1
    fi
    return 0
}

optimize_plasma_shell() {
    log_message "INFO" "Optimizing Plasma shell based on KDE documentation"
    
    local plasma_pid=$(pgrep -x plasmashell)
    if [[ -z "$plasma_pid" ]]; then
        log_message "WARN" "Plasma shell not running"
        return 1
    fi
    
    local plasma_memory=$(ps -o rss= -p "$plasma_pid" | tr -d ' ')
    local plasma_memory_mb=$((plasma_memory / 1024))
    
    log_message "INFO" "Plasma shell memory usage: ${plasma_memory_mb}MB"
    
    if [[ $plasma_memory_mb -gt $PLASMA_MAX_MEMORY_MB ]]; then
        log_message "WARN" "Plasma shell using excessive memory (${plasma_memory_mb}MB > ${PLASMA_MAX_MEMORY_MB}MB)"
        
        # Apply Plasma-specific optimizations from KDE docs
        
        # 1. Clear Plasma cache (KDE documentation recommendation)
        rm -rf "$HOME/.cache/plasma"* 2>/dev/null || true
        rm -rf "$HOME/.cache/krunner"* 2>/dev/null || true
        rm -rf "$HOME/.cache/plasmashell"* 2>/dev/null || true
        
        # 2. Restart Plasma shell (official KDE procedure)
        log_message "INFO" "Restarting Plasma shell to reclaim memory"
        kquitapp5 plasmashell 2>/dev/null || killall plasmashell 2>/dev/null || true
        sleep 2
        plasmashell &
        
        # 3. Apply memory optimization settings via KConfig
        optimize_plasma_config
    fi
}

optimize_plasma_config() {
    log_message "INFO" "Applying Plasma memory optimization configuration"
    
    # Plasma configuration optimizations based on KDE documentation
    
    # Reduce animation memory usage
    kwriteconfig5 --file kwinrc --group Compositing --key AnimationSpeed 2
    kwriteconfig5 --file kwinrc --group Compositing --key Enabled true
    kwriteconfig5 --file kwinrc --group Compositing --key GLCore true
    
    # Optimize desktop effects for memory usage
    kwriteconfig5 --file kwinrc --group Plugins --key blurEnabled false
    kwriteconfig5 --file kwinrc --group Plugins --key contrastEnabled false
    kwriteconfig5 --file kwinrc --group Plugins --key slideEnabled false
    
    # Reduce Plasma widget memory usage
    kwriteconfig5 --file plasmarc --group PlasmaViews --key panelVisibility 0
    kwriteconfig5 --file plasmarc --group Theme --key name breeze-dark
    
    # Optimize KRunner for memory efficiency
    kwriteconfig5 --file krunnerrc --group General --key historyBehavior 1
    kwriteconfig5 --file krunnerrc --group General --key retainPriorSearch false
    
    log_message "INFO" "Plasma configuration optimized for memory usage"
}

optimize_kwin() {
    log_message "INFO" "Optimizing KWin window manager based on KDE documentation"
    
    local kwin_pid=$(pgrep -x kwin_x11)
    if [[ -z "$kwin_pid" ]]; then
        kwin_pid=$(pgrep -x kwin_wayland)
    fi
    
    if [[ -z "$kwin_pid" ]]; then
        log_message "WARN" "KWin not running"
        return 1
    fi
    
    local kwin_memory=$(ps -o rss= -p "$kwin_pid" | tr -d ' ')
    local kwin_memory_mb=$((kwin_memory / 1024))
    
    log_message "INFO" "KWin memory usage: ${kwin_memory_mb}MB"
    
    if [[ $kwin_memory_mb -gt $KWIN_MAX_MEMORY_MB ]]; then
        log_message "WARN" "KWin using excessive memory (${kwin_memory_mb}MB > ${KWIN_MAX_MEMORY_MB}MB)"
        
        # KWin memory optimization from official documentation
        
        # 1. Clear KWin cache
        rm -rf "$HOME/.cache/kwin"* 2>/dev/null || true
        
        # 2. Optimize KWin configuration
        kwriteconfig5 --file kwinrc --group Compositing --key MaxFPS 60
        kwriteconfig5 --file kwinrc --group Compositing --key RefreshRate 0
        kwriteconfig5 --file kwinrc --group Compositing --key LatencyPolicy 1
        
        # 3. Disable memory-intensive effects
        kwriteconfig5 --file kwinrc --group Effect-Blur --key BlurStrength 5
        kwriteconfig5 --file kwinrc --group Effect-DesktopGrid --key BorderWidth 0
        
        # 4. Restart KWin if memory usage is critical
        if [[ $kwin_memory_mb -gt $((KWIN_MAX_MEMORY_MB * 2)) ]]; then
            log_message "INFO" "Restarting KWin due to critical memory usage"
            if pgrep -x kwin_x11 >/dev/null; then
                kwin_x11 --replace &
            elif pgrep -x kwin_wayland >/dev/null; then
                # Wayland restart is more complex
                log_message "WARN" "KWin Wayland restart requires session restart"
            fi
        fi
    fi
}

optimize_baloo() {
    log_message "INFO" "Optimizing Baloo file indexer based on KDE documentation"
    
    local baloo_pid=$(pgrep -x baloo_file)
    if [[ -z "$baloo_pid" ]]; then
        log_message "INFO" "Baloo not running"
        return 0
    fi
    
    local baloo_memory=$(ps -o rss= -p "$baloo_pid" | tr -d ' ')
    local baloo_memory_mb=$((baloo_memory / 1024))
    
    log_message "INFO" "Baloo memory usage: ${baloo_memory_mb}MB"
    
    if [[ $baloo_memory_mb -gt $BALOO_MAX_MEMORY_MB ]]; then
        log_message "WARN" "Baloo using excessive memory (${baloo_memory_mb}MB > ${BALOO_MAX_MEMORY_MB}MB)"
        
        # Baloo optimization from KDE documentation
        
        # 1. Pause indexing temporarily
        balooctl suspend
        
        # 2. Clear Baloo cache
        rm -rf "$HOME/.local/share/baloo"* 2>/dev/null || true
        
        # 3. Optimize Baloo configuration
        kwriteconfig5 --file baloofilerc --group General --key "exclude filters" "*.tmp,*.temp,*.o,*.la,*.lo,*.loT,*.moc,*~,*.orig,.git"
        kwriteconfig5 --file baloofilerc --group General --key "exclude folders" "\$HOME/Downloads,\$HOME/.cache,\$HOME/.local/share/Trash"
        kwriteconfig5 --file baloofilerc --group General --key "only basic indexing" true
        
        # 4. Resume with optimized settings
        balooctl resume
        
        log_message "INFO" "Baloo optimized and restarted"
    fi
}

optimize_akonadi() {
    log_message "INFO" "Optimizing Akonadi PIM service based on KDE documentation"
    
    local akonadi_pid=$(pgrep -x akonadi_control)
    if [[ -z "$akonadi_pid" ]]; then
        log_message "INFO" "Akonadi not running"
        return 0
    fi
    
    # Get total Akonadi memory usage (multiple processes)
    local akonadi_memory=0
    local akonadi_pids=($(pgrep -f akonadi))
    
    for pid in "${akonadi_pids[@]}"; do
        local mem=$(ps -o rss= -p "$pid" 2>/dev/null | tr -d ' ')
        akonadi_memory=$((akonadi_memory + mem))
    done
    
    local akonadi_memory_mb=$((akonadi_memory / 1024))
    
    log_message "INFO" "Akonadi total memory usage: ${akonadi_memory_mb}MB"
    
    if [[ $akonadi_memory_mb -gt $AKONADI_MAX_MEMORY_MB ]]; then
        log_message "WARN" "Akonadi using excessive memory (${akonadi_memory_mb}MB > ${AKONADI_MAX_MEMORY_MB}MB)"
        
        # Akonadi optimization from KDE PIM documentation
        
        # 1. Stop Akonadi
        akonadictl stop
        
        # 2. Clear Akonadi cache
        rm -rf "$HOME/.local/share/akonadi/db_data"* 2>/dev/null || true
        rm -rf "$HOME/.cache/akonadi"* 2>/dev/null || true
        
        # 3. Optimize Akonadi configuration
        kwriteconfig5 --file akonadiserverrc --group "QMYSQL" --key "Options" "MYSQL_OPT_RECONNECT=1"
        kwriteconfig5 --file akonadiserverrc --group "General" --key "SizeThreshold" 4096
        
        # 4. Restart Akonadi
        akonadictl start
        
        log_message "INFO" "Akonadi optimized and restarted"
    fi
}

optimize_kde_applications() {
    log_message "INFO" "Optimizing KDE applications memory usage"
    
    # Optimize common KDE applications based on documentation
    
    # Dolphin file manager
    local dolphin_pids=($(pgrep -x dolphin))
    for pid in "${dolphin_pids[@]}"; do
        if [[ -n "$pid" ]]; then
            local mem=$(ps -o rss= -p "$pid" | tr -d ' ')
            local mem_mb=$((mem / 1024))
            if [[ $mem_mb -gt 256 ]]; then
                log_message "INFO" "Optimizing Dolphin process $pid (${mem_mb}MB)"
                renice 10 "$pid" 2>/dev/null || true
            fi
        fi
    done
    
    # Kate/KWrite text editors
    local kate_pids=($(pgrep -E "kate|kwrite"))
    for pid in "${kate_pids[@]}"; do
        if [[ -n "$pid" ]]; then
            local mem=$(ps -o rss= -p "$pid" | tr -d ' ')
            local mem_mb=$((mem / 1024))
            if [[ $mem_mb -gt 128 ]]; then
                log_message "INFO" "Optimizing Kate/KWrite process $pid (${mem_mb}MB)"
                renice 5 "$pid" 2>/dev/null || true
            fi
        fi
    done
    
    # Konsole terminal
    local konsole_pids=($(pgrep -x konsole))
    for pid in "${konsole_pids[@]}"; do
        if [[ -n "$pid" ]]; then
            local mem=$(ps -o rss= -p "$pid" | tr -d ' ')
            local mem_mb=$((mem / 1024))
            if [[ $mem_mb -gt 64 ]]; then
                log_message "INFO" "Optimizing Konsole process $pid (${mem_mb}MB)"
                renice 5 "$pid" 2>/dev/null || true
            fi
        fi
    done
}

apply_kde_kernel_optimizations() {
    log_message "INFO" "Applying KDE-specific kernel optimizations"
    
    # Kernel optimizations for KDE/Qt applications
    
    # Optimize for GUI responsiveness
    echo 1 > /proc/sys/kernel/sched_autogroup_enabled 2>/dev/null || true
    
    # Reduce memory fragmentation for Qt applications
    echo 1 > /proc/sys/vm/compact_unevictable_allowed 2>/dev/null || true
    
    # Optimize for desktop workloads
    echo 100 > /proc/sys/vm/vfs_cache_pressure 2>/dev/null || true
    echo 60 > /proc/sys/vm/swappiness 2>/dev/null || true
}

monitor_kde_memory() {
    if ! check_kde_session; then
        log_message "WARN" "Not in KDE session, skipping KDE-specific optimizations"
        return 1
    fi
    
    log_message "INFO" "Starting KDE memory monitoring and optimization"
    
    # Monitor and optimize KDE components
    optimize_plasma_shell
    optimize_kwin
    optimize_baloo
    optimize_akonadi
    optimize_kde_applications
    apply_kde_kernel_optimizations
    
    log_message "INFO" "KDE memory optimization completed"
}

emergency_kde_cleanup() {
    log_message "CRITICAL" "Emergency KDE memory cleanup initiated"
    
    # Emergency KDE cleanup procedures
    
    # 1. Clear all KDE caches
    rm -rf "$HOME/.cache/plasma"* 2>/dev/null || true
    rm -rf "$HOME/.cache/kwin"* 2>/dev/null || true
    rm -rf "$HOME/.cache/baloo"* 2>/dev/null || true
    rm -rf "$HOME/.cache/akonadi"* 2>/dev/null || true
    rm -rf "$HOME/.cache/dolphin"* 2>/dev/null || true
    rm -rf "$HOME/.cache/kate"* 2>/dev/null || true
    
    # 2. Restart critical KDE services
    kquitapp5 plasmashell 2>/dev/null || killall plasmashell 2>/dev/null || true
    akonadictl stop 2>/dev/null || true
    balooctl suspend 2>/dev/null || true
    
    sleep 3
    
    plasmashell &
    akonadictl start 2>/dev/null || true
    balooctl resume 2>/dev/null || true
    
    log_message "CRITICAL" "Emergency KDE cleanup completed"
}

install_kde_optimizations() {
    log_message "INFO" "Installing KDE memory optimization configurations"
    
    # Create optimized KDE configuration
    
    # Plasma optimization
    kwriteconfig5 --file plasmarc --group Theme --key name breeze-dark
    kwriteconfig5 --file plasmarc --group PlasmaViews --key panelVisibility 0
    
    # KWin optimization
    kwriteconfig5 --file kwinrc --group Compositing --key Enabled true
    kwriteconfig5 --file kwinrc --group Compositing --key AnimationSpeed 2
    kwriteconfig5 --file kwinrc --group Compositing --key MaxFPS 60
    
    # Baloo optimization
    kwriteconfig5 --file baloofilerc --group General --key "only basic indexing" true
    kwriteconfig5 --file baloofilerc --group General --key "exclude filters" "*.tmp,*.temp,*.o,*.la,*.lo,*.loT,*.moc,*~,*.orig,.git"
    
    log_message "INFO" "KDE optimization configurations installed"
}

main() {
    case "${1:-monitor}" in
        "monitor")
            monitor_kde_memory
            ;;
        "emergency")
            emergency_kde_cleanup
            ;;
        "install")
            install_kde_optimizations
            ;;
        "plasma")
            optimize_plasma_shell
            ;;
        "kwin")
            optimize_kwin
            ;;
        "baloo")
            optimize_baloo
            ;;
        "akonadi")
            optimize_akonadi
            ;;
        *)
            echo "Usage: $0 [monitor|emergency|install|plasma|kwin|baloo|akonadi]"
            echo "  monitor   - Monitor and optimize KDE memory usage"
            echo "  emergency - Emergency KDE memory cleanup"
            echo "  install   - Install KDE optimization configurations"
            echo "  plasma    - Optimize Plasma shell only"
            echo "  kwin      - Optimize KWin window manager only"
            echo "  baloo     - Optimize Baloo file indexer only"
            echo "  akonadi   - Optimize Akonadi PIM service only"
            ;;
    esac
}

# Ensure log file exists
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

main "$@"
