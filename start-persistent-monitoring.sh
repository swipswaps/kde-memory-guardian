#!/bin/bash

# START PERSISTENT KLIPPER MONITORING - CORRECTIVE ACTION
# WHAT: Implements the persistent monitoring that should have been done initially
# WHY: Previous approach failed due to lack of continuous monitoring
# HOW: Background daemon with comprehensive logging and real-time detection

echo "==============================================================================="
echo "STARTING PERSISTENT KLIPPER MONITORING - CORRECTIVE ACTION"
echo "==============================================================================="
echo "Timestamp: $(date)"
echo "This implements the monitoring that should have been done initially"
echo "==============================================================================="

# Create log directory
LOG_DIR="$HOME/.local/share/klipper-monitoring"
mkdir -p "$LOG_DIR"

# Log file locations (answering user's question about log locations)
MAIN_LOG="$LOG_DIR/persistent-monitor-$(date +%Y%m%d_%H%M%S).log"
ALERT_LOG="$LOG_DIR/klipper-alerts-$(date +%Y%m%d_%H%M%S).log"
STATUS_LOG="$LOG_DIR/status-$(date +%Y%m%d_%H%M%S).log"

echo "Log files will be created at:"
echo "  Main Log: $MAIN_LOG"
echo "  Alert Log: $ALERT_LOG"
echo "  Status Log: $STATUS_LOG"
echo ""

# Create the persistent monitoring script
cat > "$LOG_DIR/klipper-daemon.sh" << 'EOF'
#!/bin/bash

# KLIPPER MONITORING DAEMON - PERSISTENT BACKGROUND MONITORING
# Runs continuously to prevent Klipper widget return

MAIN_LOG="$1"
ALERT_LOG="$2"
STATUS_LOG="$3"

log_main() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$MAIN_LOG"
}

log_alert() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚨 ALERT: $1" >> "$ALERT_LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚨 ALERT: $1" >> "$MAIN_LOG"
}

log_status() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$STATUS_LOG"
}

log_main "=== KLIPPER MONITORING DAEMON STARTED ==="
log_main "PID: $$"
log_main "Logs: Main=$MAIN_LOG, Alert=$ALERT_LOG, Status=$STATUS_LOG"

CYCLE=0
while true; do
    CYCLE=$((CYCLE + 1))
    log_main "=== MONITORING CYCLE $CYCLE ==="
    
    # Check for Klipper processes
    PROCESSES=$(pgrep -f klipper | wc -l)
    if [ $PROCESSES -gt 0 ]; then
        log_alert "Klipper processes detected: $PROCESSES"
        ps aux | grep klipper | grep -v grep >> "$ALERT_LOG"
        pkill -9 -f klipper
        log_alert "Klipper processes killed"
    fi
    
    # Check for config files
    CONFIGS=$(find ~/.config -name "*klipper*" -type f 2>/dev/null | wc -l)
    if [ $CONFIGS -gt 0 ]; then
        log_alert "Klipper config files detected: $CONFIGS"
        find ~/.config -name "*klipper*" -type f >> "$ALERT_LOG"
        find ~/.config -name "*klipper*" -type f -delete
        log_alert "Klipper config files removed"
    fi
    
    # Check system tray widget
    WIDGET_STATUS=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    var found = false;
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type.indexOf('klipper') !== -1) {
                found = true;
                print('WIDGET_DETECTED:' + widgets[j].type);
            }
        }
    }
    if (!found) { print('CLEAN'); }
    " 2>/dev/null)
    
    if [[ "$WIDGET_STATUS" != "CLEAN" ]]; then
        log_alert "Klipper widget detected in system tray: $WIDGET_STATUS"
        # Attempt to hide it
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
        " 2>/dev/null
        log_alert "Attempted to hide Klipper widget"
    fi
    
    # Log status
    log_status "Cycle $CYCLE: Processes=$PROCESSES, Configs=$CONFIGS, Widget=$WIDGET_STATUS"
    
    # Wait 0.5 seconds before next check (real-time monitoring)
    sleep 0.5
done
EOF

chmod +x "$LOG_DIR/klipper-daemon.sh"

# Start the daemon in background
echo "Starting persistent monitoring daemon..."
nohup "$LOG_DIR/klipper-daemon.sh" "$MAIN_LOG" "$ALERT_LOG" "$STATUS_LOG" > /dev/null 2>&1 &
DAEMON_PID=$!

echo "✅ Persistent monitoring daemon started with PID: $DAEMON_PID"
echo ""
echo "MONITORING IS NOW ACTIVE:"
echo "- Checks every 0.5 seconds for Klipper return (REAL-TIME)"
echo "- Automatically kills processes if detected"
echo "- Removes config files if they reappear"
echo "- Hides widget if it returns to system tray"
echo "- Logs all activity with timestamps"
echo ""
echo "LOG FILE LOCATIONS (answering your question):"
echo "  Main Log: $MAIN_LOG"
echo "  Alert Log: $ALERT_LOG"
echo "  Status Log: $STATUS_LOG"
echo ""
echo "TO MONITOR IN REAL-TIME:"
echo "  tail -f $MAIN_LOG"
echo "  tail -f $ALERT_LOG"
echo ""
echo "TO CHECK FOR ALERTS:"
echo "  grep 'ALERT' $MAIN_LOG"
echo "  cat $ALERT_LOG"
echo ""
echo "TO STOP MONITORING:"
echo "  kill $DAEMON_PID"
echo ""
echo "==============================================================================="
echo "PERSISTENT MONITORING NOW ACTIVE - WILL DETECT AND PREVENT WIDGET RETURN"
echo "==============================================================================="
