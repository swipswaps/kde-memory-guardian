#!/usr/bin/env bash
################################################################################
# widget-removal-with-capture.sh — Active Widget Removal with Message Capture
# WHAT: Combines working widget removal with comprehensive system message capture
# WHY: Previous monitoring only watched, didn't actively remove like ChatGPT did
# HOW: Implements actual removal actions while capturing all system responses
################################################################################

set -euo pipefail
IFS=$'\n\t'

# ─── SETUP COMPREHENSIVE LOGGING ─────────────────────────────────────────────
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BASE_LOG_DIR="/tmp/widget-removal-$TIMESTAMP"
mkdir -p "$BASE_LOG_DIR"

MAIN_LOG="$BASE_LOG_DIR/main.log"
REMOVAL_LOG="$BASE_LOG_DIR/removal-actions.log"
SYSTEM_LOG="$BASE_LOG_DIR/system-messages.log"
PLASMA_LOG="$BASE_LOG_DIR/plasma-responses.log"

NOW="$(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "[START] 🔥 Widget Removal with Message Capture Started — $NOW" | tee "$MAIN_LOG"
echo "[LOGS] 📁 Log directory: $BASE_LOG_DIR" | tee -a "$MAIN_LOG"

# ─── CLEANUP FUNCTION ────────────────────────────────────────────────────────
cleanup() {
    echo "[CLEANUP] 🧹 Stopping all monitoring processes..." | tee -a "$MAIN_LOG"
    pkill -P $$ 2>/dev/null || true
    jobs -p | xargs -r kill 2>/dev/null || true
    echo "[CLEANUP] ✅ Cleanup complete" | tee -a "$MAIN_LOG"
}
trap cleanup EXIT INT TERM

# ─── START SYSTEM MESSAGE MONITORING ────────────────────────────────────────
echo "[MONITOR] 📡 Starting system message capture..." | tee -a "$MAIN_LOG"

# WHAT: Capture journal messages during widget removal operations
# WHY: Shows system-level responses to our removal actions
{
    echo "[JOURNAL-START] $(date) - Monitoring systemd journal during widget removal"
    journalctl --user --follow --since now --no-pager 2>&1 | while IFS= read -r line; do
        if [[ "$line" =~ (klipper|Klipper|plasma|systemtray|StatusNotifier|widget) ]]; then
            echo "[$(date '+%H:%M:%S')] JOURNAL: $line"
        fi
    done
} > "$SYSTEM_LOG" 2>&1 &
JOURNAL_PID=$!

# WHAT: Capture D-Bus messages during removal operations
# WHY: Shows widget destruction and system tray reconfiguration events
{
    echo "[DBUS-START] $(date) - Monitoring D-Bus during widget removal"
    dbus-monitor --session 2>&1 | while IFS= read -r line; do
        if [[ "$line" =~ (klipper|Klipper|systemtray|StatusNotifier|plasma) ]]; then
            echo "[$(date '+%H:%M:%S')] DBUS: $line"
        fi
    done
} > "$PLASMA_LOG" 2>&1 &
DBUS_PID=$!

echo "[INFO] 📊 Monitoring PIDs: Journal=$JOURNAL_PID, DBus=$DBUS_PID" | tee -a "$MAIN_LOG"

# ─── ACTIVE WIDGET REMOVAL IMPLEMENTATION ───────────────────────────────────
# WHAT: Implements the actual removal steps that worked for ChatGPT
# WHY: Previous monitoring was passive - this actively removes while capturing
# HOW: Step-by-step removal with comprehensive message capture

echo "[ACTION] 🎯 Starting active widget removal process..." | tee -a "$MAIN_LOG"

# STEP 1: Kill any Klipper processes with message capture
echo "[STEP-1] 💀 Killing Klipper processes..." | tee -a "$MAIN_LOG" | tee -a "$REMOVAL_LOG"
KLIPPER_PROCESSES=$(ps aux | grep -E "(^|\s)klipper(\s|$)" | grep -v grep | grep -v "widget-removal" || true)
if [[ -n "$KLIPPER_PROCESSES" ]]; then
    echo "[PROCESS-FOUND] Klipper processes detected:" | tee -a "$REMOVAL_LOG"
    echo "$KLIPPER_PROCESSES" | tee -a "$REMOVAL_LOG"
    
    echo "[KILL-ACTION] Executing pkill -9 -f klipper..." | tee -a "$REMOVAL_LOG"
    pkill -9 -f klipper 2>&1 | tee -a "$REMOVAL_LOG" || echo "[KILL-RESULT] No processes to kill" | tee -a "$REMOVAL_LOG"
    
    sleep 2
    echo "[KILL-VERIFY] Verification after kill:" | tee -a "$REMOVAL_LOG"
    ps aux | grep klipper | grep -v grep | tee -a "$REMOVAL_LOG" || echo "[KILL-SUCCESS] No Klipper processes remaining" | tee -a "$REMOVAL_LOG"
else
    echo "[PROCESS-NONE] No Klipper processes found" | tee -a "$REMOVAL_LOG"
fi

# STEP 2: Remove Klipper configuration files with message capture
echo "[STEP-2] 📁 Removing Klipper configuration files..." | tee -a "$MAIN_LOG" | tee -a "$REMOVAL_LOG"
KLIPPER_CONFIGS=$(find ~/.config -name "*klipper*" -type f 2>/dev/null | grep -v "Code.*workspaceStorage" || true)
if [[ -n "$KLIPPER_CONFIGS" ]]; then
    echo "[CONFIG-FOUND] Klipper config files detected:" | tee -a "$REMOVAL_LOG"
    echo "$KLIPPER_CONFIGS" | tee -a "$REMOVAL_LOG"
    
    echo "[CONFIG-ACTION] Removing configuration files..." | tee -a "$REMOVAL_LOG"
    find ~/.config -name "*klipper*" -type f ! -path "*/Code*/workspaceStorage/*" -delete -print 2>&1 | tee -a "$REMOVAL_LOG"
    
    echo "[CONFIG-VERIFY] Verification after removal:" | tee -a "$REMOVAL_LOG"
    find ~/.config -name "*klipper*" -type f 2>/dev/null | grep -v "Code.*workspaceStorage" | tee -a "$REMOVAL_LOG" || echo "[CONFIG-SUCCESS] No Klipper config files remaining" | tee -a "$REMOVAL_LOG"
else
    echo "[CONFIG-NONE] No Klipper config files found" | tee -a "$REMOVAL_LOG"
fi

# STEP 3: Clear Plasma cache with message capture
echo "[STEP-3] 🧹 Clearing Plasma cache..." | tee -a "$MAIN_LOG" | tee -a "$REMOVAL_LOG"
echo "[CACHE-ACTION] Removing Plasma cache files..." | tee -a "$REMOVAL_LOG"
rm -rfv ~/.cache/plasma/plasma-svgelements ~/.cache/plasma/plasma_theme_*.kcache 2>&1 | tee -a "$REMOVAL_LOG" || echo "[CACHE-INFO] No cache files to remove" | tee -a "$REMOVAL_LOG"

# STEP 4: Remove widget from system tray configuration with message capture
echo "[STEP-4] ⚙️ Removing widget from system tray configuration..." | tee -a "$MAIN_LOG" | tee -a "$REMOVAL_LOG"

echo "[TRAY-BEFORE] Current system tray configuration:" | tee -a "$REMOVAL_LOG"
BEFORE_CONFIG=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
var result = '';
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type == 'org.kde.plasma.systemtray') {
            widget = widgets[j];
            widget.currentConfigGroup = ['General'];
            var hidden = widget.readConfig('hiddenItems', '');
            var extra = widget.readConfig('extraItems', '');
            result += 'BEFORE-HIDDEN:' + hidden + ';BEFORE-EXTRA:' + extra + ';';
        }
    }
}
print(result);
" 2>&1)
echo "[TRAY-BEFORE] $BEFORE_CONFIG" | tee -a "$REMOVAL_LOG"

echo "[TRAY-ACTION] Removing Klipper from system tray..." | tee -a "$REMOVAL_LOG"
REMOVAL_RESULT=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
var result = '';
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type == 'org.kde.plasma.systemtray') {
            widget = widgets[j];
            widget.currentConfigGroup = ['General'];
            
            // Remove from hidden items
            var hiddenItems = widget.readConfig('hiddenItems', '').split(',');
            var newHidden = [];
            for (var k = 0; k < hiddenItems.length; k++) {
                if (hiddenItems[k] !== 'org.kde.klipper' && hiddenItems[k] !== '') {
                    newHidden.push(hiddenItems[k]);
                }
            }
            widget.writeConfig('hiddenItems', newHidden.join(','));
            
            // Remove from extra items
            var extraItems = widget.readConfig('extraItems', '').split(',');
            var newExtra = [];
            for (var k = 0; k < extraItems.length; k++) {
                if (extraItems[k] !== 'org.kde.klipper' && extraItems[k] !== '') {
                    newExtra.push(extraItems[k]);
                }
            }
            widget.writeConfig('extraItems', newExtra.join(','));
            
            result += 'REMOVED-FROM-HIDDEN-AND-EXTRA;';
        }
    }
}
print(result);
" 2>&1)
echo "[TRAY-ACTION] $REMOVAL_RESULT" | tee -a "$REMOVAL_LOG"

echo "[TRAY-AFTER] Configuration after removal:" | tee -a "$REMOVAL_LOG"
AFTER_CONFIG=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
var result = '';
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type == 'org.kde.plasma.systemtray') {
            widget = widgets[j];
            widget.currentConfigGroup = ['General'];
            var hidden = widget.readConfig('hiddenItems', '');
            var extra = widget.readConfig('extraItems', '');
            result += 'AFTER-HIDDEN:' + hidden + ';AFTER-EXTRA:' + extra + ';';
        }
    }
}
print(result);
" 2>&1)
echo "[TRAY-AFTER] $AFTER_CONFIG" | tee -a "$REMOVAL_LOG"

# STEP 5: Restart plasmashell with message capture
echo "[STEP-5] 🔄 Restarting plasmashell..." | tee -a "$MAIN_LOG" | tee -a "$REMOVAL_LOG"

echo "[PLASMA-KILL] Stopping plasmashell..." | tee -a "$REMOVAL_LOG"
pkill plasmashell 2>&1 | tee -a "$REMOVAL_LOG" || echo "[PLASMA-KILL] Plasmashell not running" | tee -a "$REMOVAL_LOG"

sleep 3

echo "[PLASMA-START] Starting plasmashell..." | tee -a "$REMOVAL_LOG"
nohup kstart plasmashell >/dev/null 2>&1 &
PLASMA_PID=$!
echo "[PLASMA-START] Started plasmashell with PID: $PLASMA_PID" | tee -a "$REMOVAL_LOG"

sleep 5

echo "[PLASMA-VERIFY] Verifying plasmashell is running..." | tee -a "$REMOVAL_LOG"
if pgrep plasmashell >/dev/null 2>&1; then
    echo "[PLASMA-SUCCESS] Plasmashell restarted successfully" | tee -a "$REMOVAL_LOG"
    pgrep plasmashell | tee -a "$REMOVAL_LOG"
else
    echo "[PLASMA-ERROR] Failed to restart plasmashell" | tee -a "$REMOVAL_LOG"
fi

# ─── CONTINUOUS MONITORING AFTER REMOVAL ────────────────────────────────────
echo "[MONITOR] 👁️ Starting continuous monitoring after removal..." | tee -a "$MAIN_LOG"

echo ""
echo "=== REAL-TIME MONITORING AFTER WIDGET REMOVAL ==="
echo "Monitoring widget status for 120 seconds to detect return..."
echo ""

# WHAT: Monitor for widget return with timestamps
# WHY: Captures the exact moment and system messages when widget returns
for i in {1..60}; do
    CURRENT_STATUS=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    var result = '';
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type.indexOf('klipper') !== -1) {
                result += 'WIDGET_RETURNED:' + widgets[j].type + ';';
            }
            if (widgets[j].type == 'org.kde.plasma.systemtray') {
                widget = widgets[j];
                widget.currentConfigGroup = ['General'];
                var hidden = widget.readConfig('hiddenItems', '');
                var extra = widget.readConfig('extraItems', '');
                if (hidden.indexOf('klipper') !== -1 || extra.indexOf('klipper') !== -1) {
                    result += 'KLIPPER_IN_CONFIG:hidden=' + hidden + ',extra=' + extra + ';';
                }
            }
        }
    }
    print(result);
    " 2>/dev/null || echo "SCRIPT_ERROR")
    
    TIMESTAMP=$(date '+%H:%M:%S')
    if [[ "$CURRENT_STATUS" != "" && "$CURRENT_STATUS" != "SCRIPT_ERROR" ]]; then
        echo "[$TIMESTAMP] WIDGET-STATUS: $CURRENT_STATUS" | tee -a "$REMOVAL_LOG"
        
        if [[ "$CURRENT_STATUS" == *"WIDGET_RETURNED"* ]]; then
            echo "[$TIMESTAMP] 🚨 WIDGET RETURNED! Capturing system state..." | tee -a "$REMOVAL_LOG"
            
            # Capture system state when widget returns
            echo "[$TIMESTAMP] PROCESSES: $(pgrep -f klipper | wc -l)" | tee -a "$REMOVAL_LOG"
            echo "[$TIMESTAMP] CONFIGS: $(find ~/.config -name "*klipper*" -type f 2>/dev/null | wc -l)" | tee -a "$REMOVAL_LOG"
            
            # Show what processes exist
            ps aux | grep klipper | grep -v grep | tee -a "$REMOVAL_LOG" || echo "[$TIMESTAMP] No klipper processes" | tee -a "$REMOVAL_LOG"
        fi
    else
        echo "[$TIMESTAMP] WIDGET-CLEAN: No Klipper widgets detected" | tee -a "$REMOVAL_LOG"
    fi
    
    sleep 2
done

# ─── FINAL SUMMARY ───────────────────────────────────────────────────────────
echo ""
echo "[COMPLETE] 🎯 Widget removal and monitoring complete" | tee -a "$MAIN_LOG"

echo ""
echo "=== REMOVAL AND MONITORING SUMMARY ==="
echo "System messages: $(wc -l < "$SYSTEM_LOG" 2>/dev/null || echo 0)"
echo "Plasma responses: $(wc -l < "$PLASMA_LOG" 2>/dev/null || echo 0)"
echo "Removal actions: $(wc -l < "$REMOVAL_LOG" 2>/dev/null || echo 0)"
echo ""
echo "=== LOG LOCATIONS ==="
echo "All logs: $BASE_LOG_DIR/"
echo "Main log: $MAIN_LOG"
echo "Removal actions: $REMOVAL_LOG"
echo "System messages: $SYSTEM_LOG"
echo "Plasma responses: $PLASMA_LOG"
echo ""
echo "=== VIEW CAPTURED MESSAGES ==="
echo "cat $REMOVAL_LOG"
echo "cat $SYSTEM_LOG"
echo "cat $PLASMA_LOG"
