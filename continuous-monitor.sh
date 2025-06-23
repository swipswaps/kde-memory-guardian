#!/bin/bash
# Continuous Klipper monitoring - captures system messages showing widget return

LOG_FILE="/tmp/klipper-continuous-$(date +%H%M%S).log"
echo "[$(date)] Starting continuous monitoring" | tee "$LOG_FILE"

# Monitor journal for klipper/plasma messages
journalctl --user --follow --since now | grep -i -E "(klipper|systemtray)" | while read line; do
    echo "[JOURNAL] $line" | tee -a "$LOG_FILE"
done &

# Monitor processes every 2 seconds
while true; do
    # Check for actual klipper processes (not this script)
    KLIPPER_PROCS=$(ps aux | grep -E "klipper" | grep -v grep | grep -v "continuous-monitor")
    if [[ -n "$KLIPPER_PROCS" ]]; then
        echo "[$(date)] KLIPPER DETECTED:" | tee -a "$LOG_FILE"
        echo "$KLIPPER_PROCS" | tee -a "$LOG_FILE"
        
        # Kill them
        pkill -f "^klipper" 2>&1 | tee -a "$LOG_FILE"
        echo "[$(date)] Kill command executed" | tee -a "$LOG_FILE"
    fi
    
    # Check widget status
    WIDGET_CHECK=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type.indexOf('klipper') !== -1) {
                print('WIDGET_FOUND:' + widgets[j].type);
            }
        }
    }
    " 2>/dev/null)
    
    if [[ "$WIDGET_CHECK" == *"WIDGET_FOUND"* ]]; then
        echo "[$(date)] WIDGET DETECTED: $WIDGET_CHECK" | tee -a "$LOG_FILE"
    fi
    
    sleep 2
done
