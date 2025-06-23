#!/usr/bin/env bash
# Real-time Klipper System Message Monitor
# Captures actual system messages showing WHY widget returns

set -euo pipefail
IFS=$'\n\t'

LOG_FILE="/tmp/klipper-system-monitor-$(date +%Y%m%d_%H%M%S).log"
NOW="$(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "[START] 🔍 Klipper System Monitor Started — $NOW" | tee -a "$LOG_FILE"

# Kill any existing monitoring
pkill -f "journalctl.*klipper" 2>/dev/null || true
pkill -f "dbus-monitor" 2>/dev/null || true

echo "[STEP] 📡 Starting system message capture streams..." | tee -a "$LOG_FILE"

# 1. Journal monitoring for Klipper/Plasma messages
echo "[MONITOR] Starting journal monitor for klipper/plasma messages..." | tee -a "$LOG_FILE"
journalctl --user --follow --since now | grep -i -E "(klipper|plasma|systemtray)" 2>&1 | while read line; do
    echo "[JOURNAL] $line" | tee -a "$LOG_FILE"
done &
JOURNAL_PID=$!

# 2. DBus monitoring for system tray events
echo "[MONITOR] Starting dbus monitor for system tray events..." | tee -a "$LOG_FILE"
dbus-monitor --session "interface='org.kde.StatusNotifierWatcher'" 2>&1 | while read line; do
    echo "[DBUS] $line" | tee -a "$LOG_FILE"
done &
DBUS_PID=$!

# 3. Process monitoring with actual system messages
echo "[MONITOR] Starting process lifecycle monitoring..." | tee -a "$LOG_FILE"
while true; do
    # Check for new klipper processes (exclude this script)
    if pgrep -f klipper | grep -v $$ >/dev/null 2>&1; then
        echo "[PROCESS] 🚨 Klipper process detected:" | tee -a "$LOG_FILE"
        ps aux | grep klipper | grep -v grep 2>&1 | tee -a "$LOG_FILE"
        
        echo "[ACTION] Killing klipper processes..." | tee -a "$LOG_FILE"
        pkill -9 -f klipper 2>&1 | tee -a "$LOG_FILE"
        
        echo "[VERIFY] Process kill result:" | tee -a "$LOG_FILE"
        ps aux | grep klipper | grep -v grep 2>&1 | tee -a "$LOG_FILE" || echo "[OK] No klipper processes remaining" | tee -a "$LOG_FILE"
    fi
    
    # Check for klipper config files
    KLIPPER_CONFIGS=$(find ~/.config -name "*klipper*" -type f 2>/dev/null)
    if [[ -n "$KLIPPER_CONFIGS" ]]; then
        echo "[CONFIG] 🚨 Klipper config files detected:" | tee -a "$LOG_FILE"
        echo "$KLIPPER_CONFIGS" | tee -a "$LOG_FILE"
        
        echo "[ACTION] Removing klipper config files..." | tee -a "$LOG_FILE"
        find ~/.config -name "*klipper*" -type f -delete -print 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # Check system tray widget status
    WIDGET_STATUS=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    var result = '';
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type.indexOf('klipper') !== -1) {
                result += 'WIDGET_PRESENT:' + widgets[j].type + ';';
            }
            if (widgets[j].type == 'org.kde.plasma.systemtray') {
                widget = widgets[j];
                widget.currentConfigGroup = ['General'];
                var hidden = widget.readConfig('hiddenItems', '');
                var extra = widget.readConfig('extraItems', '');
                result += 'HIDDEN:' + hidden + ';EXTRA:' + extra + ';';
            }
        }
    }
    print(result);
    " 2>&1)
    
    if [[ "$WIDGET_STATUS" == *"WIDGET_PRESENT"* ]]; then
        echo "[WIDGET] 🚨 Klipper widget detected in system tray:" | tee -a "$LOG_FILE"
        echo "[WIDGET] Status: $WIDGET_STATUS" | tee -a "$LOG_FILE"
        
        echo "[ACTION] Attempting to hide widget..." | tee -a "$LOG_FILE"
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
                        print('Klipper added to hidden items');
                    }
                }
            }
        }
        " 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # Status summary every 10 cycles
    CYCLE_COUNT=$((${CYCLE_COUNT:-0} + 1))
    if (( CYCLE_COUNT % 10 == 0 )); then
        echo "[STATUS] Cycle $CYCLE_COUNT - Monitoring active" | tee -a "$LOG_FILE"
        echo "[STATUS] Processes: $(pgrep -f klipper | wc -l), Configs: $(find ~/.config -name "*klipper*" -type f 2>/dev/null | wc -l)" | tee -a "$LOG_FILE"
    fi
    
    sleep 1
done &
MONITOR_PID=$!

echo "[INFO] 📊 Monitoring PIDs: Journal=$JOURNAL_PID, DBus=$DBUS_PID, Monitor=$MONITOR_PID" | tee -a "$LOG_FILE"
echo "[INFO] 📄 Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "[INFO] ⏱️ Monitoring for 300 seconds (5 minutes)..." | tee -a "$LOG_FILE"

# Run for 5 minutes
sleep 300

echo "[STOP] 🛑 Stopping monitoring..." | tee -a "$LOG_FILE"
kill $JOURNAL_PID $DBUS_PID $MONITOR_PID 2>/dev/null || true

echo "[DONE] ✅ Monitoring complete. Log saved to: $LOG_FILE" | tee -a "$LOG_FILE"
echo "[SUMMARY] 📋 Final status:" | tee -a "$LOG_FILE"
echo "Processes: $(pgrep -f klipper | wc -l)" | tee -a "$LOG_FILE"
echo "Configs: $(find ~/.config -name "*klipper*" -type f 2>/dev/null | wc -l)" | tee -a "$LOG_FILE"

# Show recent log entries
echo ""
echo "=== RECENT LOG ENTRIES ==="
tail -20 "$LOG_FILE"
