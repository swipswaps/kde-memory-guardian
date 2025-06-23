#!/bin/bash

# REAL-TIME KLIPPER MONITOR - EVENT-DRIVEN MONITORING
# WHAT: Instant detection and elimination using event-driven monitoring
# WHY: Polling every 10 seconds (or even 0.5s) is inadequate for real-time protection
# HOW: Multiple parallel monitoring streams with instant response

set -x  # Show all commands
exec 2>&1  # Redirect stderr to stdout for full visibility

echo "==============================================================================="
echo "REAL-TIME KLIPPER MONITOR - EVENT-DRIVEN INSTANT DETECTION"
echo "==============================================================================="
echo "Timestamp: $(date)"
echo "This replaces the inadequate 10-second polling approach"
echo "==============================================================================="

# Configuration
LOG_DIR="$HOME/.local/share/klipper-monitoring"
mkdir -p "$LOG_DIR"

REALTIME_LOG="$LOG_DIR/realtime-monitor-$(date +%Y%m%d_%H%M%S).log"
INSTANT_ALERT_LOG="$LOG_DIR/instant-alerts-$(date +%Y%m%d_%H%M%S).log"

echo "Real-time monitoring logs:"
echo "  Main Log: $REALTIME_LOG"
echo "  Instant Alerts: $INSTANT_ALERT_LOG"
echo ""

# Logging functions
log_realtime() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S.%3N')] $1" | tee -a "$REALTIME_LOG"
}

log_instant_alert() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S.%3N')] 🚨 INSTANT ALERT: $1" | tee -a "$INSTANT_ALERT_LOG" | tee -a "$REALTIME_LOG"
}

log_realtime "=== REAL-TIME KLIPPER MONITORING STARTED ==="
log_realtime "PID: $$"

# Function to eliminate Klipper instantly
eliminate_klipper() {
    local reason="$1"
    log_instant_alert "Klipper detected via $reason - INSTANT ELIMINATION"
    
    # Kill processes immediately
    pkill -9 -f klipper 2>/dev/null && log_instant_alert "Processes killed" || log_realtime "No processes to kill"
    
    # Remove configs immediately
    local configs_removed=$(find ~/.config -name "*klipper*" -type f -delete -print 2>/dev/null | wc -l)
    if [ $configs_removed -gt 0 ]; then
        log_instant_alert "Removed $configs_removed config files"
    fi
    
    # Hide from system tray immediately
    qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type == 'org.kde.plasma.systemtray') {
                widget = widgets[j];
                widget.currentConfigGroup = ['General'];
                var hiddenItems = widget.readConfig('hiddenItems', '').split(',');
                if (hiddenItems.indexOf('org.kde.klipper') == -1) {
                    hiddenItems.push('org.kde.klipper');
                    widget.writeConfig('hiddenItems', hiddenItems.join(','));
                }
            }
        }
    }
    " 2>/dev/null && log_instant_alert "Widget hidden from system tray"
    
    log_instant_alert "INSTANT ELIMINATION COMPLETE for $reason"
}

log_realtime "Starting parallel monitoring streams..."

# 1. PROCESS MONITORING - Monitor /proc for new klipper processes
log_realtime "Starting process monitoring stream..."
(
    while true; do
        if pgrep -f klipper >/dev/null 2>&1; then
            eliminate_klipper "PROCESS_DETECTION"
        fi
        sleep 0.1  # 100ms check for processes
    done
) &
PROCESS_MONITOR_PID=$!

# 2. FILE SYSTEM MONITORING - Monitor config directory for klipper files
log_realtime "Starting filesystem monitoring stream..."
if command -v inotifywait >/dev/null 2>&1; then
    (
        inotifywait -m -r ~/.config -e create,modify,move --format '%w%f %e' 2>/dev/null | while read file event; do
            if [[ "$file" == *klipper* ]]; then
                eliminate_klipper "FILESYSTEM_DETECTION:$file:$event"
            fi
        done
    ) &
    FILESYSTEM_MONITOR_PID=$!
    log_realtime "Filesystem monitoring active (inotify)"
else
    log_realtime "inotifywait not available - using fast polling for filesystem"
    (
        while true; do
            if find ~/.config -name "*klipper*" -type f 2>/dev/null | grep -q .; then
                eliminate_klipper "FILESYSTEM_POLLING"
            fi
            sleep 0.1  # 100ms check for files
        done
    ) &
    FILESYSTEM_MONITOR_PID=$!
fi

# 3. DBUS MONITORING - Monitor for Klipper-related dbus activity
log_realtime "Starting dbus monitoring stream..."
(
    timeout 3600 dbus-monitor --session 2>/dev/null | while read line; do
        if [[ "$line" == *klipper* ]] || [[ "$line" == *Klipper* ]]; then
            eliminate_klipper "DBUS_DETECTION:$line"
        fi
    done
) &
DBUS_MONITOR_PID=$!

# 4. PLASMA WIDGET MONITORING - Monitor system tray changes
log_realtime "Starting plasma widget monitoring stream..."
(
    while true; do
        widget_check=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
        var panels = panels();
        for (var i = 0; i < panels.length; i++) {
            var widgets = panels[i].widgets();
            for (var j = 0; j < widgets.length; j++) {
                if (widgets[j].type.indexOf('klipper') !== -1) {
                    print('WIDGET_DETECTED');
                    break;
                }
            }
        }
        " 2>/dev/null)
        
        if [[ "$widget_check" == *"WIDGET_DETECTED"* ]]; then
            eliminate_klipper "WIDGET_DETECTION"
        fi
        sleep 0.1  # 100ms check for widgets
    done
) &
WIDGET_MONITOR_PID=$!

# 5. SYSTEMD SERVICE MONITORING - Monitor for klipper services
log_realtime "Starting systemd service monitoring stream..."
(
    while true; do
        if systemctl --user list-units --all 2>/dev/null | grep -i klipper | grep -q active; then
            eliminate_klipper "SYSTEMD_SERVICE_DETECTION"
        fi
        sleep 0.2  # 200ms check for services
    done
) &
SYSTEMD_MONITOR_PID=$!

log_realtime "=== ALL MONITORING STREAMS ACTIVE ==="
log_realtime "Process Monitor PID: $PROCESS_MONITOR_PID"
log_realtime "Filesystem Monitor PID: $FILESYSTEM_MONITOR_PID"
log_realtime "DBus Monitor PID: $DBUS_MONITOR_PID"
log_realtime "Widget Monitor PID: $WIDGET_MONITOR_PID"
log_realtime "Systemd Monitor PID: $SYSTEMD_MONITOR_PID"

echo ""
echo "==============================================================================="
echo "REAL-TIME MONITORING ACTIVE - INSTANT DETECTION AND ELIMINATION"
echo "==============================================================================="
echo "Monitoring Streams:"
echo "  ✅ Process monitoring (100ms intervals)"
echo "  ✅ Filesystem monitoring (event-driven or 100ms)"
echo "  ✅ DBus monitoring (event-driven)"
echo "  ✅ Widget monitoring (100ms intervals)"
echo "  ✅ Systemd service monitoring (200ms intervals)"
echo ""
echo "Log Files:"
echo "  Real-time Log: $REALTIME_LOG"
echo "  Instant Alerts: $INSTANT_ALERT_LOG"
echo ""
echo "To monitor in real-time:"
echo "  tail -f $REALTIME_LOG"
echo "  tail -f $INSTANT_ALERT_LOG"
echo ""
echo "To stop all monitoring:"
echo "  kill $PROCESS_MONITOR_PID $FILESYSTEM_MONITOR_PID $DBUS_MONITOR_PID $WIDGET_MONITOR_PID $SYSTEMD_MONITOR_PID"
echo ""
echo "MONITORING WILL RUN FOR 1 HOUR THEN AUTO-TERMINATE"
echo "==============================================================================="

# Main monitoring loop with status updates
START_TIME=$(date +%s)
while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))
    
    # Stop after 1 hour
    if [ $ELAPSED -gt 3600 ]; then
        log_realtime "1 hour monitoring completed - terminating"
        break
    fi
    
    # Status update every 60 seconds
    if [ $((ELAPSED % 60)) -eq 0 ] && [ $ELAPSED -gt 0 ]; then
        log_realtime "Status update: ${ELAPSED}s elapsed, all streams active"
    fi
    
    sleep 1
done

# Cleanup
log_realtime "Terminating all monitoring streams..."
kill $PROCESS_MONITOR_PID $FILESYSTEM_MONITOR_PID $DBUS_MONITOR_PID $WIDGET_MONITOR_PID $SYSTEMD_MONITOR_PID 2>/dev/null

log_realtime "=== REAL-TIME MONITORING COMPLETED ==="
echo ""
echo "==============================================================================="
echo "REAL-TIME MONITORING SESSION COMPLETED"
echo "==============================================================================="
echo "Duration: 1 hour"
echo "Logs saved to:"
echo "  $REALTIME_LOG"
echo "  $INSTANT_ALERT_LOG"
echo "==============================================================================="
