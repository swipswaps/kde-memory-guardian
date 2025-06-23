#!/bin/bash

# Simple Klipper Widget Removal Tool
# WHAT: Removes Klipper widget from KDE taskbar/system tray
# WHY: Addresses the issue where Klipper widget persists even after process termination
# HOW: Direct manipulation of Plasma configuration and widget removal

set -euo pipefail

echo "🔄 Removing Klipper widget from KDE taskbar..."

# Step 1: Kill any running Klipper processes
echo "🔄 Stopping Klipper processes..."
pkill -f klipper 2>/dev/null || echo "ℹ️ No Klipper processes found"

# Step 2: Remove Klipper autostart
echo "🔄 Disabling Klipper autostart..."
AUTOSTART_FILE="$HOME/.config/autostart/org.kde.klipper.desktop"
if [[ -f "$AUTOSTART_FILE" ]]; then
    echo "Hidden=true" >> "$AUTOSTART_FILE"
    echo "✅ Klipper autostart disabled"
else
    echo "ℹ️ No Klipper autostart file found"
fi

# Step 3: Remove from KDE session management
echo "🔄 Removing from KDE session management..."
if command -v kwriteconfig5 >/dev/null 2>&1; then
    kwriteconfig5 --file ksmserverrc --group General --key excludeApps "klipper"
    echo "✅ Klipper excluded from session management"
fi

# Step 4: Disable Klipper global shortcuts
echo "🔄 Disabling Klipper global shortcuts..."
if command -v kwriteconfig5 >/dev/null 2>&1; then
    kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "clipboard_action" "none"
    kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "cycleNextAction" "none"
    kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "cyclePrevAction" "none"
    echo "✅ Klipper shortcuts disabled"
fi

# Step 5: Use Plasma scripting to hide Klipper from system tray
echo "🔄 Hiding Klipper from system tray..."
if command -v qdbus >/dev/null 2>&1; then
    qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
        var panels = panels();
        for (var i = 0; i < panels.length; i++) {
            var panel = panels[i];
            var widgets = panel.widgets();
            for (var j = 0; j < widgets.length; j++) {
                var widget = widgets[j];
                if (widget.type == 'org.kde.plasma.systemtray') {
                    widget.currentConfigGroup = ['General'];
                    var hiddenItems = widget.readConfig('hiddenItems', '').split(',');
                    if (hiddenItems.indexOf('org.kde.klipper') == -1) {
                        hiddenItems.push('org.kde.klipper');
                        widget.writeConfig('hiddenItems', hiddenItems.join(','));
                        print('Klipper hidden from system tray');
                    }
                }
            }
        }
    " 2>/dev/null && echo "✅ Klipper hidden from system tray" || echo "⚠️ Could not hide from system tray"
fi

# Step 6: Clean Plasma configuration cache
echo "🔄 Cleaning Plasma configuration cache..."
if [[ -d "$HOME/.cache/plasma" ]]; then
    rm -rf "$HOME/.cache/plasma/plasma-svgelements" 2>/dev/null || true
    rm -f "$HOME/.cache/plasma/plasma_theme_*.kcache" 2>/dev/null || true
    echo "✅ Plasma cache cleaned"
fi

# Step 7: Restart plasmashell to apply changes
echo "🔄 Restarting plasmashell to apply changes..."
pkill plasmashell 2>/dev/null || true
sleep 2

if command -v kstart >/dev/null 2>&1; then
    nohup kstart plasmashell >/dev/null 2>&1 &
else
    nohup plasmashell >/dev/null 2>&1 &
fi

echo "⏳ Waiting for plasmashell to restart..."
sleep 5

if pgrep plasmashell >/dev/null 2>&1; then
    echo "✅ Plasmashell restarted successfully"
else
    echo "❌ Failed to restart plasmashell"
    exit 1
fi

echo ""
echo "🎉 Klipper widget removal completed!"
echo "📋 Klipper should no longer appear in the taskbar/system tray"
echo "🔄 If Klipper returns, it may be due to KDE session restoration"
echo "💡 Consider using the advanced clipboard system from KDE Memory Guardian"

# Final status check
echo ""
echo "📊 Final status:"
if pgrep -f klipper >/dev/null 2>&1; then
    echo "⚠️ Klipper process still running"
else
    echo "✅ No Klipper processes running"
fi

if [[ -f "$HOME/.config/autostart/org.kde.klipper.desktop" ]] && grep -q "Hidden=true" "$HOME/.config/autostart/org.kde.klipper.desktop" 2>/dev/null; then
    echo "✅ Klipper autostart disabled"
else
    echo "ℹ️ Klipper autostart status unclear"
fi

echo "✅ Klipper widget removal process complete!"
