#!/bin/bash

# FINAL KLIPPER ELIMINATION - COMPLETE REMOVAL WITH FULL VISIBILITY
# WHAT: Definitive removal of all Klipper processes, configs, and widget references
# WHY: Extended watchdog revealed 5 running processes and 16 config files
# HOW: Comprehensive elimination with full error visibility

set -x  # Show all commands
exec 2>&1  # Redirect stderr to stdout for full visibility

echo "==============================================================================="
echo "FINAL KLIPPER ELIMINATION - COMPLETE REMOVAL"
echo "==============================================================================="
echo "Timestamp: $(date)"
echo "Based on extended watchdog findings:"
echo "- 5 Klipper processes running"
echo "- 16 Klipper config files found"
echo "- Widget hidden but still present in system tray"
echo "==============================================================================="

echo ""
echo "1. CURRENT KLIPPER PROCESS STATUS:"
echo "=================================="
ps aux | grep klipper | grep -v grep || echo "No Klipper processes found"

echo ""
echo "2. KILLING ALL KLIPPER PROCESSES:"
echo "================================="
pkill -9 -f klipper && echo "✅ Klipper processes killed" || echo "ℹ️ No processes to kill"
sleep 2

echo ""
echo "3. VERIFICATION - NO PROCESSES REMAINING:"
echo "========================================="
ps aux | grep klipper | grep -v grep || echo "✅ Confirmed: No Klipper processes running"

echo ""
echo "4. REMOVING ALL KLIPPER CONFIG FILES:"
echo "====================================="
echo "Finding all Klipper config files:"
find ~/.config -name "*klipper*" -type f -print

echo ""
echo "Removing all Klipper config files:"
find ~/.config -name "*klipper*" -type f -delete -print || echo "No files to delete"

echo ""
echo "5. CLEARING PLASMA SYSTEM TRAY CONFIGURATION:"
echo "=============================================="
echo "Current system tray hidden items:"
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type == 'org.kde.plasma.systemtray') {
            widget = widgets[j];
            widget.currentConfigGroup = ['General'];
            print('Before: Hidden items = ' + widget.readConfig('hiddenItems', ''));
            
            // Remove Klipper from hidden items
            var hiddenItems = widget.readConfig('hiddenItems', '').split(',');
            var newHiddenItems = [];
            for (var k = 0; k < hiddenItems.length; k++) {
                if (hiddenItems[k] !== 'org.kde.klipper' && hiddenItems[k] !== '') {
                    newHiddenItems.push(hiddenItems[k]);
                }
            }
            widget.writeConfig('hiddenItems', newHiddenItems.join(','));
            print('After: Hidden items = ' + widget.readConfig('hiddenItems', ''));
        }
    }
}
" 2>&1

echo ""
echo "6. RESTARTING PLASMASHELL TO APPLY CHANGES:"
echo "==========================================="
echo "Stopping plasmashell..."
pkill plasmashell
sleep 3

echo "Starting plasmashell..."
nohup kstart plasmashell >/dev/null 2>&1 &
sleep 5

echo "Verifying plasmashell is running:"
if pgrep plasmashell >/dev/null 2>&1; then
    echo "✅ Plasmashell restarted successfully"
else
    echo "❌ Failed to restart plasmashell"
fi

echo ""
echo "7. FINAL VERIFICATION:"
echo "====================="
echo "Klipper processes: $(pgrep -f klipper | wc -l)"
echo "Klipper config files: $(find ~/.config -name "*klipper*" -type f | wc -l)"

echo ""
echo "System tray status:"
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
var klipperFound = false;
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type.indexOf('klipper') !== -1) {
            print('❌ KLIPPER WIDGET STILL PRESENT: ' + widgets[j].type);
            klipperFound = true;
        }
        if (widgets[j].type == 'org.kde.plasma.systemtray') {
            widget = widgets[j];
            widget.currentConfigGroup = ['General'];
            var hiddenItems = widget.readConfig('hiddenItems', '');
            if (hiddenItems.indexOf('klipper') !== -1) {
                print('❌ Klipper still in hidden items: ' + hiddenItems);
                klipperFound = true;
            }
        }
    }
}
if (!klipperFound) {
    print('✅ SUCCESS: No Klipper widgets or references found in taskbar');
}
" 2>&1

echo ""
echo "==============================================================================="
echo "FINAL KLIPPER ELIMINATION COMPLETE"
echo "==============================================================================="
echo "Summary:"
echo "- All Klipper processes terminated"
echo "- All Klipper config files removed"
echo "- System tray configuration cleaned"
echo "- Plasmashell restarted to apply changes"
echo ""
echo "If Klipper widget is still visible, it indicates a deeper system integration"
echo "that may require additional KDE configuration changes or system restart."
echo "==============================================================================="
