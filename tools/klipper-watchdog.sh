#!/bin/bash

# KLIPPER WATCHDOG - EXTENDED MONITORING OF HIDDEN MESSAGES
# WHAT: Comprehensive monitoring system that captures ALL normally hidden system messages
# WHY: Widget persistence indicates hidden system processes are restoring Klipper
# HOW: Multi-layer monitoring with complete message capture and logging

set -x  # Show all commands
exec 2>&1  # Redirect stderr to stdout for full visibility

# Configuration
readonly WATCHDOG_LOG="/tmp/klipper-watchdog-$(date +%Y%m%d_%H%M%S).log"
readonly SYSTEM_LOG="/tmp/system-messages-$(date +%Y%m%d_%H%M%S).log"
readonly PLASMA_LOG="/tmp/plasma-messages-$(date +%Y%m%d_%H%M%S).log"

echo "==============================================================================="
echo "KLIPPER WATCHDOG - EXTENDED MONITORING SYSTEM"
echo "==============================================================================="
echo "Timestamp: $(date)"
echo "Watchdog Log: $WATCHDOG_LOG"
echo "System Log: $SYSTEM_LOG"
echo "Plasma Log: $PLASMA_LOG"
echo "==============================================================================="

# Function to log with timestamp
log_watchdog() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$WATCHDOG_LOG"
}

log_watchdog "Starting extended Klipper watchdog monitoring"

# 1. CAPTURE ALL SYSTEM MESSAGES
log_watchdog "=== CAPTURING ALL SYSTEM MESSAGES ==="

# Monitor systemd user services
log_watchdog "Monitoring systemd user services for Klipper references:"
systemctl --user list-units --all | grep -i klipper 2>&1 | tee -a "$SYSTEM_LOG"

# Monitor dbus messages
log_watchdog "Monitoring dbus messages:"
timeout 5 dbus-monitor --session 2>&1 | grep -i klipper | tee -a "$SYSTEM_LOG" &
DBUS_PID=$!

# Monitor journal for Klipper messages
log_watchdog "Checking recent journal entries:"
journalctl --user --since "5 minutes ago" | grep -i klipper 2>&1 | tee -a "$SYSTEM_LOG"

# 2. DETAILED PLASMA SYSTEM TRAY ANALYSIS
log_watchdog "=== DETAILED PLASMA SYSTEM TRAY ANALYSIS ==="

log_watchdog "Current system tray configuration:"
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type == 'org.kde.plasma.systemtray') {
            widget = widgets[j];
            widget.currentConfigGroup = ['General'];
            print('=== SYSTEM TRAY WIDGET ===');
            print('Hidden items: ' + widget.readConfig('hiddenItems', ''));
            print('Extra items: ' + widget.readConfig('extraItems', ''));
            print('Shown items: ' + widget.readConfig('shownItems', ''));
            print('Known items: ' + widget.readConfig('knownItems', ''));
            
            // Check all configuration groups
            var groups = widget.configGroups;
            for (var k = 0; k < groups.length; k++) {
                widget.currentConfigGroup = [groups[k]];
                var keys = widget.configKeys;
                for (var l = 0; l < keys.length; l++) {
                    var value = widget.readConfig(keys[l], '');
                    if (value.indexOf('klipper') !== -1 || value.indexOf('Klipper') !== -1) {
                        print('FOUND KLIPPER REFERENCE: ' + groups[k] + '/' + keys[l] + ' = ' + value);
                    }
                }
            }
        }
    }
}
" 2>&1 | tee -a "$PLASMA_LOG"

# 3. MONITOR PLASMA CONFIGURATION FILES
log_watchdog "=== MONITORING PLASMA CONFIGURATION FILES ==="

log_watchdog "Searching all Plasma configs for Klipper references:"
find ~/.config -name "plasma*" -type f -exec grep -l -i klipper {} \; 2>&1 | tee -a "$PLASMA_LOG"

log_watchdog "Detailed Klipper references in Plasma configs:"
find ~/.config -name "plasma*" -type f -exec grep -H -i klipper {} \; 2>&1 | tee -a "$PLASMA_LOG"

# 4. MONITOR AUTOSTART AND SESSION RESTORATION
log_watchdog "=== MONITORING AUTOSTART AND SESSION RESTORATION ==="

log_watchdog "Checking all autostart files:"
find ~/.config/autostart -name "*.desktop" -exec grep -l -i klipper {} \; 2>&1 | tee -a "$SYSTEM_LOG"

log_watchdog "Checking session management:"
if [[ -f ~/.config/ksmserverrc ]]; then
    grep -A 10 -B 10 -i klipper ~/.config/ksmserverrc 2>&1 | tee -a "$SYSTEM_LOG"
fi

# 5. REAL-TIME MONITORING OF WIDGET CHANGES
log_watchdog "=== REAL-TIME MONITORING OF WIDGET CHANGES ==="

log_watchdog "Starting real-time monitoring for 30 seconds..."
for i in {1..30}; do
    echo "=== MONITORING CYCLE $i ===" >> "$PLASMA_LOG"
    
    # Check if Klipper widget appears
    WIDGET_CHECK=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    var klipperFound = false;
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type.indexOf('klipper') !== -1) {
                klipperFound = true;
                print('KLIPPER WIDGET DETECTED: ' + widgets[j].type);
            }
        }
    }
    if (!klipperFound) {
        print('No Klipper widgets detected');
    }
    " 2>&1)
    
    echo "[$(date '+%H:%M:%S')] $WIDGET_CHECK" >> "$PLASMA_LOG"
    
    # Check for new processes
    if pgrep -f klipper >/dev/null 2>&1; then
        echo "[$(date '+%H:%M:%S')] KLIPPER PROCESS DETECTED!" >> "$SYSTEM_LOG"
        ps aux | grep klipper >> "$SYSTEM_LOG"
    fi
    
    sleep 1
done

# 6. CAPTURE PLASMA SHELL LOGS
log_watchdog "=== CAPTURING PLASMA SHELL LOGS ==="

log_watchdog "Plasma shell error messages:"
journalctl --user -u plasma-plasmashell.service --since "10 minutes ago" 2>&1 | tee -a "$PLASMA_LOG"

# 7. MONITOR KDED MODULES
log_watchdog "=== MONITORING KDED MODULES ==="

log_watchdog "Checking kded modules for clipboard/klipper:"
qdbus org.kde.kded6 /kded org.kde.kded6.loadedModules 2>&1 | grep -i -E "(clip|klipper)" | tee -a "$SYSTEM_LOG"

# 8. FINAL COMPREHENSIVE STATUS
log_watchdog "=== FINAL COMPREHENSIVE STATUS ==="

log_watchdog "Current Klipper status:"
echo "Processes: $(pgrep -f klipper | wc -l)" | tee -a "$WATCHDOG_LOG"
echo "Config files: $(find ~/.config -name "*klipper*" -type f | wc -l)" | tee -a "$WATCHDOG_LOG"
echo "Autostart files: $(find ~/.config/autostart -name "*klipper*" | wc -l)" | tee -a "$WATCHDOG_LOG"

# Kill background dbus monitor
kill $DBUS_PID 2>/dev/null || true

log_watchdog "Extended watchdog monitoring completed"

echo ""
echo "==============================================================================="
echo "WATCHDOG MONITORING COMPLETE"
echo "==============================================================================="
echo "Log files created:"
echo "  Watchdog Log: $WATCHDOG_LOG"
echo "  System Log: $SYSTEM_LOG"
echo "  Plasma Log: $PLASMA_LOG"
echo ""
echo "To view logs:"
echo "  cat $WATCHDOG_LOG"
echo "  cat $SYSTEM_LOG"
echo "  cat $PLASMA_LOG"
echo ""
echo "To search for specific issues:"
echo "  grep -i 'klipper' $SYSTEM_LOG $PLASMA_LOG"
echo "  grep -i 'error' $SYSTEM_LOG $PLASMA_LOG"
echo "==============================================================================="
