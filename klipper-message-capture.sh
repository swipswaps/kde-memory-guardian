#!/usr/bin/env bash
################################################################################
# klipper-message-capture.sh — Real-time System Message Capture
# WHAT: Captures actual system messages showing Klipper widget restoration
# WHY: Previous attempts failed to show real system events causing widget return
# HOW: Multiple parallel streams capturing journal, dbus, and process events
################################################################################

# ─── ENFORCE SAFE EXECUTION ───────────────────────────────────────────────────
# WHAT: Prevents undefined variables and hidden pipe failures
# WHY: Ensures all steps are error-visible, no silent skips
set -euo pipefail
IFS=$'\n\t'

# ─── SETUP COMPREHENSIVE LOGGING ─────────────────────────────────────────────
# WHAT: Multiple log files for different message types
# WHY: Separates system events from script actions for clarity
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BASE_LOG_DIR="/tmp/klipper-capture-$TIMESTAMP"
mkdir -p "$BASE_LOG_DIR"

MAIN_LOG="$BASE_LOG_DIR/main.log"
JOURNAL_LOG="$BASE_LOG_DIR/journal.log"
DBUS_LOG="$BASE_LOG_DIR/dbus.log"
PROCESS_LOG="$BASE_LOG_DIR/process.log"
PLASMA_LOG="$BASE_LOG_DIR/plasma.log"

NOW="$(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "[START] 🔍 Klipper Message Capture Started — $NOW" | tee "$MAIN_LOG"
echo "[LOGS] 📁 Log directory: $BASE_LOG_DIR" | tee -a "$MAIN_LOG"

# ─── CLEANUP FUNCTION ────────────────────────────────────────────────────────
# WHAT: Ensures all background processes are terminated on exit
# WHY: Prevents orphaned monitoring processes
cleanup() {
    echo "[CLEANUP] 🧹 Stopping all monitoring processes..." | tee -a "$MAIN_LOG"
    pkill -P $$ 2>/dev/null || true
    jobs -p | xargs -r kill 2>/dev/null || true
    echo "[CLEANUP] ✅ Cleanup complete" | tee -a "$MAIN_LOG"
}
trap cleanup EXIT INT TERM

# ─── JOURNAL MESSAGE CAPTURE ─────────────────────────────────────────────────
# WHAT: Captures systemd journal messages related to KDE/Klipper
# WHY: Shows service starts, stops, and error messages from system perspective
# HOW: Uses journalctl --follow to get real-time messages
echo "[MONITOR] 📰 Starting journal message capture..." | tee -a "$MAIN_LOG"
{
    echo "[JOURNAL-START] $(date) - Monitoring systemd journal for KDE/Klipper messages"
    journalctl --user --follow --since now --no-pager 2>&1 | while IFS= read -r line; do
        # WHAT: Filter for relevant messages containing klipper, plasma, or systemtray
        # WHY: Reduces noise while capturing all relevant system events
        if [[ "$line" =~ (klipper|Klipper|plasma|systemtray|StatusNotifier) ]]; then
            echo "[$(date '+%H:%M:%S')] JOURNAL: $line"
        fi
    done
} > "$JOURNAL_LOG" 2>&1 &
JOURNAL_PID=$!

# ─── DBUS MESSAGE CAPTURE ────────────────────────────────────────────────────
# WHAT: Captures D-Bus messages for system tray and status notifier events
# WHY: Shows widget creation, destruction, and configuration changes
# HOW: Uses dbus-monitor to intercept system tray related messages
echo "[MONITOR] 🚌 Starting D-Bus message capture..." | tee -a "$MAIN_LOG"
{
    echo "[DBUS-START] $(date) - Monitoring D-Bus for system tray messages"
    dbus-monitor --session "interface='org.kde.StatusNotifierWatcher'" 2>&1 | while IFS= read -r line; do
        echo "[$(date '+%H:%M:%S')] DBUS: $line"
    done
} > "$DBUS_LOG" 2>&1 &
DBUS_PID=$!

# ─── PLASMA CONFIGURATION MONITORING ────────────────────────────────────────
# WHAT: Monitors changes to Plasma configuration files
# WHY: Detects when system tray configuration is modified
# HOW: Uses inotify to watch config directory for file changes
echo "[MONITOR] ⚙️ Starting Plasma config monitoring..." | tee -a "$MAIN_LOG"
{
    echo "[PLASMA-START] $(date) - Monitoring Plasma configuration changes"
    if command -v inotifywait >/dev/null 2>&1; then
        inotifywait -m -r ~/.config/plasma* -e modify,create,delete --format '%T %w%f %e' --timefmt '%H:%M:%S' 2>&1 | while IFS= read -r line; do
            if [[ "$line" =~ (klipper|systemtray|applet) ]]; then
                echo "[$(date '+%H:%M:%S')] PLASMA-CONFIG: $line"
            fi
        done
    else
        echo "[$(date '+%H:%M:%S')] PLASMA-CONFIG: inotifywait not available, using polling"
        while true; do
            find ~/.config/plasma* -name "*klipper*" -newer /tmp/last_check 2>/dev/null | while IFS= read -r file; do
                echo "[$(date '+%H:%M:%S')] PLASMA-CONFIG: File modified: $file"
            done
            touch /tmp/last_check
            sleep 5
        done
    fi
} > "$PLASMA_LOG" 2>&1 &
PLASMA_PID=$!

# ─── PROCESS AND WIDGET MONITORING ───────────────────────────────────────────
# WHAT: Monitors for Klipper process creation and widget appearance
# WHY: Detects exactly when Klipper returns and what triggers it
# HOW: Continuous polling with immediate action and logging
echo "[MONITOR] 🔄 Starting process and widget monitoring..." | tee -a "$MAIN_LOG"
{
    echo "[PROCESS-START] $(date) - Monitoring Klipper processes and widgets"
    CYCLE=0
    while true; do
        CYCLE=$((CYCLE + 1))
        
        # WHAT: Check for actual Klipper processes (excluding this script)
        # WHY: Detects when Klipper service starts or is launched
        KLIPPER_PROCESSES=$(ps aux | grep -E "(^|\s)klipper(\s|$)" | grep -v grep | grep -v "klipper-message-capture" || true)
        if [[ -n "$KLIPPER_PROCESSES" ]]; then
            echo "[$(date '+%H:%M:%S')] PROCESS-ALERT: Klipper process detected!"
            echo "[$(date '+%H:%M:%S')] PROCESS-DETAILS: $KLIPPER_PROCESSES"
            
            # WHAT: Immediately terminate Klipper processes
            # WHY: Prevents memory accumulation and widget persistence
            echo "[$(date '+%H:%M:%S')] PROCESS-ACTION: Terminating Klipper processes..."
            pkill -f "^klipper" 2>&1 | while IFS= read -r line; do
                echo "[$(date '+%H:%M:%S')] PROCESS-KILL: $line"
            done || echo "[$(date '+%H:%M:%S')] PROCESS-KILL: No processes to kill"
        fi
        
        # WHAT: Check for Klipper configuration files
        # WHY: Detects when config files are recreated by system
        KLIPPER_CONFIGS=$(find ~/.config -name "*klipper*" -type f 2>/dev/null || true)
        if [[ -n "$KLIPPER_CONFIGS" ]]; then
            echo "[$(date '+%H:%M:%S')] CONFIG-ALERT: Klipper config files detected!"
            echo "$KLIPPER_CONFIGS" | while IFS= read -r config; do
                echo "[$(date '+%H:%M:%S')] CONFIG-FILE: $config"
            done
            
            # WHAT: Remove configuration files to prevent service restart
            # WHY: Eliminates the source of Klipper restoration
            echo "[$(date '+%H:%M:%S')] CONFIG-ACTION: Removing Klipper config files..."
            find ~/.config -name "*klipper*" -type f -delete -print 2>&1 | while IFS= read -r file; do
                echo "[$(date '+%H:%M:%S')] CONFIG-REMOVED: $file"
            done
        fi
        
        # WHAT: Check system tray widget status using Plasma scripting
        # WHY: Detects when widget appears in system tray
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
                    if (hidden.indexOf('klipper') !== -1 || extra.indexOf('klipper') !== -1) {
                        result += 'KLIPPER_IN_TRAY:hidden=' + hidden + ',extra=' + extra + ';';
                    }
                }
            }
        }
        print(result);
        " 2>/dev/null || echo "SCRIPT_ERROR")
        
        if [[ "$WIDGET_STATUS" != "" && "$WIDGET_STATUS" != "SCRIPT_ERROR" ]]; then
            echo "[$(date '+%H:%M:%S')] WIDGET-STATUS: $WIDGET_STATUS"
            
            if [[ "$WIDGET_STATUS" == *"WIDGET_PRESENT"* ]]; then
                echo "[$(date '+%H:%M:%S')] WIDGET-ALERT: Klipper widget visible in system tray!"
                
                # WHAT: Attempt to hide the widget by modifying system tray configuration
                # WHY: Removes widget from visible area without killing plasmashell
                echo "[$(date '+%H:%M:%S')] WIDGET-ACTION: Hiding Klipper widget..."
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
                " 2>&1 | while IFS= read -r line; do
                    echo "[$(date '+%H:%M:%S')] WIDGET-HIDE: $line"
                done
            fi
        fi
        
        # WHAT: Status update every 30 cycles (approximately 1 minute)
        # WHY: Provides regular confirmation that monitoring is active
        if (( CYCLE % 30 == 0 )); then
            echo "[$(date '+%H:%M:%S')] STATUS: Cycle $CYCLE - Monitoring active"
            echo "[$(date '+%H:%M:%S')] STATUS: Processes=$(pgrep -f klipper | wc -l), Configs=$(find ~/.config -name "*klipper*" -type f 2>/dev/null | wc -l)"
        fi
        
        # WHAT: Wait 2 seconds between checks
        # WHY: Balances responsiveness with system resource usage
        sleep 2
    done
} > "$PROCESS_LOG" 2>&1 &
PROCESS_PID=$!

# ─── MONITORING STATUS AND CONTROL ───────────────────────────────────────────
# WHAT: Display monitoring status and manage execution
# WHY: Provides user feedback and controls monitoring duration
echo "[INFO] 📊 Monitoring PIDs: Journal=$JOURNAL_PID, DBus=$DBUS_PID, Plasma=$PLASMA_PID, Process=$PROCESS_PID" | tee -a "$MAIN_LOG"
echo "[INFO] 📁 Log files created in: $BASE_LOG_DIR" | tee -a "$MAIN_LOG"
echo "[INFO] ⏱️ Monitoring for 300 seconds (5 minutes)..." | tee -a "$MAIN_LOG"
echo "[INFO] 👁️ Watch real-time: tail -f $BASE_LOG_DIR/*.log" | tee -a "$MAIN_LOG"

# ─── REAL-TIME LOG DISPLAY ───────────────────────────────────────────────────
# WHAT: Shows captured messages in real-time to terminal
# WHY: Provides immediate visibility into system events as they occur
echo ""
echo "=== REAL-TIME SYSTEM MESSAGE CAPTURE ==="
echo "Monitoring started. Press Ctrl+C to stop early."
echo ""

# WHAT: Display messages from all log files as they are written
# WHY: Shows user exactly what system messages are being captured
tail -f "$JOURNAL_LOG" "$DBUS_LOG" "$PLASMA_LOG" "$PROCESS_LOG" 2>/dev/null &
TAIL_PID=$!

# WHAT: Run monitoring for specified duration
# WHY: Provides sufficient time to observe widget return behavior
sleep 300

# ─── MONITORING COMPLETION ───────────────────────────────────────────────────
# WHAT: Stop monitoring and provide summary
# WHY: Clean termination with results summary
echo ""
echo "[STOP] 🛑 Monitoring period complete" | tee -a "$MAIN_LOG"
kill $TAIL_PID 2>/dev/null || true

# WHAT: Generate summary of captured messages
# WHY: Provides overview of what was detected during monitoring
echo ""
echo "=== CAPTURE SUMMARY ==="
echo "Journal messages: $(wc -l < "$JOURNAL_LOG" 2>/dev/null || echo 0)"
echo "D-Bus messages: $(wc -l < "$DBUS_LOG" 2>/dev/null || echo 0)"
echo "Plasma config changes: $(wc -l < "$PLASMA_LOG" 2>/dev/null || echo 0)"
echo "Process events: $(wc -l < "$PROCESS_LOG" 2>/dev/null || echo 0)"
echo ""
echo "=== LOG LOCATIONS ==="
echo "All logs: $BASE_LOG_DIR/"
echo "Main log: $MAIN_LOG"
echo "Journal: $JOURNAL_LOG"
echo "D-Bus: $DBUS_LOG"
echo "Plasma: $PLASMA_LOG"
echo "Process: $PROCESS_LOG"
echo ""
echo "=== VIEW CAPTURED MESSAGES ==="
echo "cat $JOURNAL_LOG"
echo "cat $DBUS_LOG"
echo "cat $PLASMA_LOG"
echo "cat $PROCESS_LOG"

# WHAT: Final status check
# WHY: Shows current state after monitoring period
echo ""
echo "=== FINAL STATUS ==="
echo "Klipper processes: $(pgrep -f klipper | wc -l)"
echo "Klipper configs: $(find ~/.config -name "*klipper*" -type f 2>/dev/null | wc -l)"
echo "Monitoring complete: $(date)"
