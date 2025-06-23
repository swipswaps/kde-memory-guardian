#!/bin/bash
# Capture real user-space system messages for Klipper activity

echo "=== REAL USER-SPACE SYSTEM MESSAGES ==="
echo "Timestamp: $(date)"
echo ""

# Kill GitHub CLI to free terminals
sudo pkill -f "gh release" 2>/dev/null || true

echo "1. SYSTEMD USER JOURNAL (last 30 minutes):"
echo "----------------------------------------"
journalctl --user --since "30 minutes ago" --no-pager | grep -i -E "(klipper|plasma|systemtray|clipboard)" | tail -20

echo ""
echo "2. CURRENT SYSTEMD USER SERVICES:"
echo "--------------------------------"
systemctl --user list-units | grep -i -E "(klipper|plasma|clipboard)"

echo ""
echo "3. DBUS SESSION ACTIVITY (last 5 minutes):"
echo "------------------------------------------"
# Start dbus monitoring in background for 10 seconds
timeout 10 dbus-monitor --session 2>/dev/null | grep -i -E "(klipper|clipboard|systemtray)" &
DBUS_PID=$!
sleep 10
kill $DBUS_PID 2>/dev/null || true

echo ""
echo "4. PLASMA SHELL PROCESS STATUS:"
echo "------------------------------"
ps aux | grep plasmashell | grep -v grep

echo ""
echo "5. ACTUAL KLIPPER PROCESSES:"
echo "---------------------------"
ps aux | grep klipper | grep -v grep

echo ""
echo "6. KLIPPER CONFIG FILES:"
echo "-----------------------"
find ~/.config -name "*klipper*" -type f 2>/dev/null | head -10

echo ""
echo "7. PLASMA CONFIGURATION STATE:"
echo "-----------------------------"
ls -la ~/.config/plasma* | head -10

echo ""
echo "8. RECENT PLASMA SHELL LOGS:"
echo "---------------------------"
journalctl --user -u plasma-plasmashell.service --since "10 minutes ago" --no-pager | tail -10

echo ""
echo "9. SYSTEM TRAY WIDGET QUERY:"
echo "---------------------------"
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var panels = panels();
print('=== SYSTEM TRAY ANALYSIS ===');
for (var i = 0; i < panels.length; i++) {
    var widgets = panels[i].widgets();
    print('Panel ' + i + ' has ' + widgets.length + ' widgets');
    for (var j = 0; j < widgets.length; j++) {
        var widget = widgets[j];
        print('Widget ' + j + ': ' + widget.type);
        if (widget.type == 'org.kde.plasma.systemtray') {
            widget.currentConfigGroup = ['General'];
            var hidden = widget.readConfig('hiddenItems', '');
            var extra = widget.readConfig('extraItems', '');
            print('  Hidden items: ' + hidden);
            print('  Extra items: ' + extra);
            if (hidden.indexOf('klipper') !== -1) {
                print('  *** KLIPPER IN HIDDEN ITEMS ***');
            }
            if (extra.indexOf('klipper') !== -1) {
                print('  *** KLIPPER IN EXTRA ITEMS ***');
            }
        }
        if (widget.type.indexOf('klipper') !== -1) {
            print('  *** KLIPPER WIDGET FOUND: ' + widget.type + ' ***');
        }
    }
}
print('=== END ANALYSIS ===');
" 2>&1

echo ""
echo "10. AUTOSTART SERVICES:"
echo "---------------------"
ls -la ~/.config/autostart/ | grep -i klipper

echo ""
echo "=== CAPTURE COMPLETE ==="
echo "Real system messages captured at: $(date)"
