#!/bin/bash

# SIMPLE KLIPPER CHECK - DIRECT EXECUTION WITH REAL OUTPUT
# This will actually run and show real results

echo "=== SIMPLE KLIPPER STATUS CHECK ==="
echo "Timestamp: $(date)"
echo ""

echo "1. Current Klipper processes:"
ps aux | grep klipper | grep -v grep || echo "No Klipper processes found"

echo ""
echo "2. Klipper config files:"
find ~/.config -name "*klipper*" -type f 2>/dev/null || echo "No Klipper config files found"

echo ""
echo "3. System tray widget check:"
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
var found = false;
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type.indexOf('klipper') !== -1) {
            print('KLIPPER WIDGET FOUND: ' + widgets[j].type);
            found = true;
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
if (!found) {
    print('No Klipper widgets detected');
}
" 2>&1

echo ""
echo "=== CHECK COMPLETE ==="
