#!/bin/bash

# KLIPPER DIAGNOSTIC TOOL - FULL ERROR VISIBILITY
# WHAT: Complete diagnostic of Klipper status with NO HIDDEN OUTPUT
# WHY: LLM resistance to error messages prevents proper troubleshooting
# HOW: Direct commands with full stderr/stdout visibility using tee

set -x  # Show all commands being executed
exec 2>&1  # Redirect stderr to stdout for full visibility

echo "==============================================================================="
echo "KLIPPER DIAGNOSTIC TOOL - FULL ERROR VISIBILITY"
echo "==============================================================================="
echo "Timestamp: $(date)"
echo "User: $(whoami)"
echo "System: $(uname -a)"
echo "==============================================================================="

echo ""
echo "1. KLIPPER PROCESS STATUS:"
echo "-------------------------"
ps aux | grep klipper | tee /tmp/klipper_processes.log
echo "Exit code: $?"

echo ""
echo "2. KLIPPER AUTOSTART FILES:"
echo "---------------------------"
echo "Searching for Klipper autostart files..."
find ~/.config -name "*klipper*" -type f 2>&1 | tee /tmp/klipper_files.log
echo "Exit code: $?"

echo ""
echo "3. KLIPPER CONFIGURATION FILES:"
echo "-------------------------------"
echo "Checking for klipperrc..."
if [[ -f ~/.config/klipperrc ]]; then
    echo "Found ~/.config/klipperrc:"
    cat ~/.config/klipperrc | head -20
else
    echo "No ~/.config/klipperrc found"
fi

echo ""
echo "4. PLASMA CONFIGURATION SEARCH:"
echo "-------------------------------"
echo "Searching for Klipper in Plasma configs..."
grep -r -i "klipper" ~/.config/plasma* 2>&1 | head -20 | tee /tmp/plasma_klipper.log
echo "Exit code: $?"

echo ""
echo "5. SYSTEM TRAY WIDGET ANALYSIS:"
echo "-------------------------------"
echo "Analyzing system tray widgets..."
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
print('Found ' + panels.length + ' panels');
for (var i = 0; i < panels.length; i++) {
    var panel = panels[i];
    var widgets = panel.widgets();
    print('Panel ' + i + ' has ' + widgets.length + ' widgets');
    for (var j = 0; j < widgets.length; j++) {
        var widget = widgets[j];
        print('Widget ' + j + ': ' + widget.type);
        if (widget.type == 'org.kde.plasma.systemtray') {
            print('Found system tray widget');
            widget.currentConfigGroup = ['General'];
            var hiddenItems = widget.readConfig('hiddenItems', '');
            print('Hidden items: ' + hiddenItems);
            var extraItems = widget.readConfig('extraItems', '');
            print('Extra items: ' + extraItems);
        }
    }
}
" 2>&1 | tee /tmp/systemtray_analysis.log
echo "Exit code: $?"

echo ""
echo "6. KLIPPER GLOBAL SHORTCUTS:"
echo "----------------------------"
echo "Checking Klipper shortcuts..."
if [[ -f ~/.config/kglobalshortcutsrc ]]; then
    grep -A 10 -B 2 "\[klipper\]" ~/.config/kglobalshortcutsrc 2>&1 | tee /tmp/klipper_shortcuts.log
else
    echo "No kglobalshortcutsrc found"
fi

echo ""
echo "7. KDE SESSION MANAGEMENT:"
echo "-------------------------"
echo "Checking session exclusions..."
if [[ -f ~/.config/ksmserverrc ]]; then
    grep -A 5 -B 5 "excludeApps" ~/.config/ksmserverrc 2>&1 | tee /tmp/session_exclusions.log
else
    echo "No ksmserverrc found"
fi

echo ""
echo "8. CURRENT TASKBAR/PANEL CONTENTS:"
echo "----------------------------------"
echo "Analyzing current panel contents..."
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
for (var i = 0; i < panels.length; i++) {
    var panel = panels[i];
    print('=== PANEL ' + i + ' ===');
    print('Location: ' + panel.location);
    print('Height: ' + panel.height);
    var widgets = panel.widgets();
    for (var j = 0; j < widgets.length; j++) {
        var widget = widgets[j];
        print('Widget ' + j + ': ' + widget.type);
        if (widget.type.indexOf('klipper') !== -1 || widget.type.indexOf('Klipper') !== -1) {
            print('*** FOUND KLIPPER WIDGET: ' + widget.type + ' ***');
        }
    }
}
" 2>&1 | tee /tmp/panel_contents.log
echo "Exit code: $?"

echo ""
echo "9. MEMORY USAGE ANALYSIS:"
echo "------------------------"
echo "Current memory usage by KDE processes:"
ps -eo pid,rss,comm | grep -E "(plasma|kwin|kde|klipper)" | sort -k2 -nr | tee /tmp/kde_memory.log

echo ""
echo "10. RECENT LOG ENTRIES:"
echo "----------------------"
echo "Recent journal entries for Klipper:"
journalctl --user -n 20 | grep -i klipper 2>&1 | tee /tmp/klipper_journal.log || echo "No recent Klipper journal entries"

echo ""
echo "==============================================================================="
echo "DIAGNOSTIC COMPLETE - ALL OUTPUT VISIBLE"
echo "==============================================================================="
echo "Log files created in /tmp/:"
ls -la /tmp/klipper_*.log /tmp/plasma_*.log /tmp/systemtray_*.log /tmp/panel_*.log /tmp/kde_*.log /tmp/session_*.log 2>/dev/null || echo "Some log files may not exist"

echo ""
echo "SUMMARY:"
echo "--------"
echo "Klipper processes: $(ps aux | grep klipper | grep -v grep | wc -l)"
echo "Klipper config files: $(find ~/.config -name "*klipper*" -type f 2>/dev/null | wc -l)"
echo "Plasma configs mentioning Klipper: $(grep -r -i "klipper" ~/.config/plasma* 2>/dev/null | wc -l)"

echo ""
echo "NEXT STEPS:"
echo "----------"
echo "1. Review the output above for any Klipper references"
echo "2. Check /tmp/*.log files for detailed analysis"
echo "3. If Klipper widget is still visible, it may be:"
echo "   - Hardcoded in panel configuration"
echo "   - Restored by KDE session management"
echo "   - Added by system tray auto-population"
echo "   - Cached in Plasma theme/widget cache"

echo ""
echo "==============================================================================="
