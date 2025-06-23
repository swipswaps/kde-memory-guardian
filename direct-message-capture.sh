#!/bin/bash
# Direct system message capture - same approach that worked from console

echo "=== DIRECT SYSTEM MESSAGE CAPTURE ==="
echo "Started: $(date)"
echo ""

# Direct journal access for KDE/Plasma messages
echo "1. SYSTEMD JOURNAL MESSAGES (last 10 minutes):"
echo "----------------------------------------------"
journalctl --user --since "10 minutes ago" --no-pager | grep -E "(klipper|plasma|systemtray|clipboard|widget)" | tail -20

echo ""
echo "2. SYSTEM JOURNAL MESSAGES (last 10 minutes):"
echo "---------------------------------------------"
sudo journalctl --since "10 minutes ago" --no-pager | grep -E "(klipper|plasma|systemtray|clipboard|widget)" | tail -20

echo ""
echo "3. DBUS SYSTEM MESSAGES:"
echo "-----------------------"
# Capture dbus messages for 5 seconds
timeout 5 dbus-monitor --session 2>&1 | grep -E "(klipper|clipboard|systemtray)" || echo "No dbus messages in 5 seconds"

echo ""
echo "4. CURRENT PROCESS STATE:"
echo "------------------------"
ps aux | grep -E "(klipper|plasma)" | grep -v grep

echo ""
echo "5. CONFIGURATION FILES:"
echo "----------------------"
find ~/.config -name "*klipper*" -type f 2>/dev/null | head -10

echo ""
echo "6. PLASMA WIDGET QUERY:"
echo "----------------------"
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    for (var j = 0; j < widgets.length; j++) {
        if (widgets[j].type.indexOf('klipper') !== -1 || widgets[j].type == 'org.kde.plasma.systemtray') {
            print('Panel ' + i + ' Widget ' + j + ': ' + widgets[j].type);
            if (widgets[j].type == 'org.kde.plasma.systemtray') {
                widgets[j].currentConfigGroup = ['General'];
                var hidden = widgets[j].readConfig('hiddenItems', '');
                var extra = widgets[j].readConfig('extraItems', '');
                print('  Hidden: ' + hidden);
                print('  Extra: ' + extra);
            }
        }
    }
}
" 2>&1

echo ""
echo "7. RECENT PLASMA SHELL ACTIVITY:"
echo "-------------------------------"
journalctl --user -u plasma-plasmashell.service --since "5 minutes ago" --no-pager | tail -10

echo ""
echo "8. KDED5 SERVICE MESSAGES:"
echo "-------------------------"
journalctl --user --since "5 minutes ago" --no-pager | grep kded | tail -10

echo ""
echo "=== CAPTURE COMPLETE ==="
echo "Finished: $(date)"
