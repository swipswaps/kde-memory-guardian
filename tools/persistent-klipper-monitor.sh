#!/bin/bash

# PERSISTENT KLIPPER MONITOR - CONTINUOUS WATCHDOG
# WHAT: Continuous monitoring that prevents Klipper widget return
# WHY: Widget returned because monitoring stopped after initial removal
# HOW: Persistent background monitoring with comprehensive logging

set -x  # Show all commands
exec 2>&1  # Redirect stderr to stdout for full visibility

# Configuration
readonly MONITOR_LOG="/tmp/persistent-klipper-monitor-$(date +%Y%m%d_%H%M%S).log"
readonly MONITOR_INTERVAL=10  # Check every 10 seconds
readonly MAX_RUNTIME=3600     # Run for 1 hour (3600 seconds)

echo "==============================================================================="
echo "PERSISTENT KLIPPER MONITOR - CONTINUOUS WATCHDOG"
echo "==============================================================================="
echo "Timestamp: $(date)"
echo "Monitor Log: $MONITOR_LOG"
echo "Check Interval: ${MONITOR_INTERVAL} seconds"
echo "Max Runtime: ${MAX_RUNTIME} seconds"
echo "==============================================================================="

# Function to log with timestamp
log_monitor() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$MONITOR_LOG"
}

log_monitor "Starting persistent Klipper monitoring"

# Initial status check
log_monitor "=== INITIAL STATUS CHECK ==="
log_monitor "Current Klipper processes: $(pgrep -f klipper | wc -l)"
log_monitor "Current Klipper config files: $(find ~/.config -name "*klipper*" -type f 2>/dev/null | wc -l)"

# Check system tray status
INITIAL_TRAY_STATUS=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
var klipperFound = false;
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type.indexOf('klipper') !== -1) {
            klipperFound = true;
            print('KLIPPER WIDGET PRESENT: ' + widgets[j].type);
        }
        if (widgets[j].type == 'org.kde.plasma.systemtray') {
            widget = widgets[j];
            widget.currentConfigGroup = ['General'];
            var hidden = widget.readConfig('hiddenItems', '');
            if (hidden.indexOf('klipper') !== -1) {
                print('Klipper in hidden items: ' + hidden);
            }
        }
    }
}
if (!klipperFound) {
    print('No Klipper widgets detected');
}
" 2>&1)

log_monitor "Initial system tray status: $INITIAL_TRAY_STATUS"

# Start monitoring loop
START_TIME=$(date +%s)
CYCLE_COUNT=0

log_monitor "=== STARTING CONTINUOUS MONITORING LOOP ==="

while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
    CYCLE_COUNT=$((CYCLE_COUNT + 1))
    
    # Check if we've exceeded max runtime
    if [ $ELAPSED_TIME -gt $MAX_RUNTIME ]; then
        log_monitor "Max runtime reached (${MAX_RUNTIME}s), stopping monitor"
        break
    fi
    
    log_monitor "=== MONITORING CYCLE $CYCLE_COUNT (${ELAPSED_TIME}s elapsed) ==="
    
    # Check for Klipper processes
    KLIPPER_PROCESSES=$(pgrep -f klipper | wc -l)
    if [ $KLIPPER_PROCESSES -gt 0 ]; then
        log_monitor "🚨 ALERT: $KLIPPER_PROCESSES Klipper processes detected!"
        log_monitor "Process details:"
        ps aux | grep klipper | grep -v grep | tee -a "$MONITOR_LOG"
        
        log_monitor "Killing all Klipper processes..."
        pkill -9 -f klipper && log_monitor "✅ Klipper processes killed" || log_monitor "❌ Failed to kill processes"
        
        # Wait and verify
        sleep 2
        REMAINING_PROCESSES=$(pgrep -f klipper | wc -l)
        log_monitor "Remaining processes after kill: $REMAINING_PROCESSES"
    else
        log_monitor "✅ No Klipper processes detected"
    fi
    
    # Check for Klipper config files
    KLIPPER_CONFIGS=$(find ~/.config -name "*klipper*" -type f 2>/dev/null | wc -l)
    if [ $KLIPPER_CONFIGS -gt 0 ]; then
        log_monitor "🚨 ALERT: $KLIPPER_CONFIGS Klipper config files detected!"
        log_monitor "Config files:"
        find ~/.config -name "*klipper*" -type f 2>/dev/null | tee -a "$MONITOR_LOG"
        
        log_monitor "Removing Klipper config files..."
        find ~/.config -name "*klipper*" -type f -delete 2>/dev/null && log_monitor "✅ Config files removed" || log_monitor "❌ Failed to remove configs"
    else
        log_monitor "✅ No Klipper config files detected"
    fi
    
    # Check system tray widget status
    TRAY_STATUS=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    var klipperFound = false;
    var statusMsg = '';
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type.indexOf('klipper') !== -1) {
                klipperFound = true;
                statusMsg += 'WIDGET_PRESENT:' + widgets[j].type + ';';
            }
            if (widgets[j].type == 'org.kde.plasma.systemtray') {
                widget = widgets[j];
                widget.currentConfigGroup = ['General'];
                var hidden = widget.readConfig('hiddenItems', '');
                if (hidden.indexOf('klipper') !== -1) {
                    statusMsg += 'HIDDEN_ITEMS:' + hidden + ';';
                } else {
                    statusMsg += 'NO_KLIPPER_IN_HIDDEN;';
                }
            }
        }
    }
    if (!klipperFound && statusMsg.indexOf('KLIPPER') === -1) {
        statusMsg = 'CLEAN';
    }
    print(statusMsg);
    " 2>&1)
    
    if [[ "$TRAY_STATUS" == "CLEAN" ]]; then
        log_monitor "✅ System tray clean - no Klipper references"
    else
        log_monitor "🚨 ALERT: System tray status: $TRAY_STATUS"
        
        # If widget returned, try to hide it again
        if [[ "$TRAY_STATUS" == *"WIDGET_PRESENT"* ]]; then
            log_monitor "Attempting to hide Klipper widget again..."
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
                            print('Klipper re-hidden');
                        }
                    }
                }
            }
            " 2>&1 | tee -a "$MONITOR_LOG"
        fi
    fi
    
    # Log summary for this cycle
    log_monitor "Cycle $CYCLE_COUNT summary: Processes=$KLIPPER_PROCESSES, Configs=$KLIPPER_CONFIGS, Tray=$TRAY_STATUS"
    
    # Wait for next cycle
    sleep $MONITOR_INTERVAL
done

log_monitor "=== MONITORING COMPLETED ==="
log_monitor "Total cycles: $CYCLE_COUNT"
log_monitor "Total runtime: ${ELAPSED_TIME} seconds"
log_monitor "Monitor log saved to: $MONITOR_LOG"

echo ""
echo "==============================================================================="
echo "PERSISTENT MONITORING COMPLETED"
echo "==============================================================================="
echo "Monitor Log: $MONITOR_LOG"
echo "Total Cycles: $CYCLE_COUNT"
echo "Runtime: ${ELAPSED_TIME} seconds"
echo ""
echo "To view the complete monitoring log:"
echo "  cat $MONITOR_LOG"
echo ""
echo "To search for alerts:"
echo "  grep 'ALERT' $MONITOR_LOG"
echo "  grep 'WIDGET_PRESENT' $MONITOR_LOG"
echo "==============================================================================="
