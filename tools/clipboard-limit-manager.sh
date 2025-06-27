#!/usr/bin/env bash
################################################################################
# clipboard-limit-manager.sh
# WHAT: Safely manage clipboard entry limits to prevent KCM failures
# WHY: 2500+ entries cause KCM clipboard to fail, need safe limit management
# HOW: Interactive tool with tested safe presets and validation
################################################################################

set -euo pipefail

KLIPPER_CONFIG="$HOME/.config/klipperrc"

echo "🔧 Clipboard Entry Limit Manager"
echo "================================"
echo "Prevents KCM clipboard failures from large entry limits"
echo ""

if [[ ! -f "$KLIPPER_CONFIG" ]]; then
    echo "❌ Klipper configuration not found: $KLIPPER_CONFIG"
    echo "💡 Run clipboard widget fix first"
    exit 1
fi

current_limit=$(grep "^MaxClipItems=" "$KLIPPER_CONFIG" | cut -d'=' -f2 || echo "20")
echo "📊 Current limit: $current_limit entries"

# Determine status based on current limit
if [[ "$current_limit" -le 100 ]]; then
    status="🟢 SAFE - Always works, fast performance"
elif [[ "$current_limit" -le 500 ]]; then
    status="🟡 GOOD - Good performance, reasonable history"
elif [[ "$current_limit" -le 1000 ]]; then
    status="🟠 LARGE - Large history, acceptable performance"
elif [[ "$current_limit" -le 2048 ]]; then
    status="🔴 MAXIMUM - Your tested working limit"
else
    status="💥 DANGEROUS - May cause KCM failures!"
fi

echo "Status: $status"
echo ""

echo "🎯 Safe Presets (Based on Testing):"
echo "1. Conservative (100 entries) - 🟢 Always works, fast"
echo "2. Balanced (500 entries) - 🟡 Good performance, reasonable history"
echo "3. Large (1000 entries) - 🟠 Large history, acceptable performance"
echo "4. Maximum (2048 entries) - 🔴 Your tested working limit"
echo "5. Custom limit (1-2048)"
echo "6. Show current configuration"
echo "7. Test KCM clipboard"
echo "8. Reset to KDE defaults (20 entries)"
echo ""

read -p "Choose option (1-8): " choice

case $choice in
    1)
        new_limit=100
        description="Conservative - Always works"
        ;;
    2)
        new_limit=500
        description="Balanced - Good performance"
        ;;
    3)
        new_limit=1000
        description="Large - Acceptable performance"
        ;;
    4)
        new_limit=2048
        description="Maximum - Your tested limit"
        ;;
    5)
        read -p "Enter custom limit (1-2048): " new_limit
        if [[ ! "$new_limit" =~ ^[0-9]+$ ]] || [[ "$new_limit" -lt 1 ]] || [[ "$new_limit" -gt 2048 ]]; then
            echo "❌ Invalid limit. Must be 1-2048"
            echo "💡 Limits above 2048 cause KCM clipboard to fail"
            exit 1
        fi
        description="Custom limit"
        ;;
    6)
        echo "📋 Current Klipper configuration:"
        echo "=================================="
        cat "$KLIPPER_CONFIG"
        echo ""
        echo "📊 Key settings:"
        echo "• MaxClipItems: $(grep "^MaxClipItems=" "$KLIPPER_CONFIG" | cut -d'=' -f2)"
        echo "• KeepClipboardContents: $(grep "^KeepClipboardContents=" "$KLIPPER_CONFIG" | cut -d'=' -f2)"
        echo "• PreventEmptyClipboard: $(grep "^PreventEmptyClipboard=" "$KLIPPER_CONFIG" | cut -d'=' -f2)"
        exit 0
        ;;
    7)
        echo "🧪 Testing KCM clipboard..."
        echo "Attempting to launch kcmshell6 clipboard..."
        
        if kcmshell6 clipboard 2>&1 | grep -q "Could not find plugin"; then
            echo "❌ KCM clipboard plugin not found"
            echo "💡 Use alternative: ~/.local/bin/configure-clipboard"
        else
            echo "✅ KCM clipboard launched (check if window opened)"
            echo "💡 If it's slow or unresponsive, try a lower limit"
        fi
        exit 0
        ;;
    8)
        new_limit=20
        description="KDE Default"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🔄 Setting clipboard limit to $new_limit entries ($description)..."

# Backup current config
backup_file="$KLIPPER_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
cp "$KLIPPER_CONFIG" "$backup_file"
echo "📋 Backed up current config to: $backup_file"

# Update MaxClipItems
sed -i "s/^MaxClipItems=.*/MaxClipItems=$new_limit/" "$KLIPPER_CONFIG"

echo "✅ Clipboard limit updated to $new_limit entries"
echo ""

# Show new status
if [[ "$new_limit" -le 100 ]]; then
    new_status="🟢 SAFE - Always works, fast performance"
elif [[ "$new_limit" -le 500 ]]; then
    new_status="🟡 GOOD - Good performance, reasonable history"
elif [[ "$new_limit" -le 1000 ]]; then
    new_status="🟠 LARGE - Large history, acceptable performance"
elif [[ "$new_limit" -le 2048 ]]; then
    new_status="🔴 MAXIMUM - Your tested working limit"
else
    new_status="💥 DANGEROUS - May cause KCM failures!"
fi

echo "New status: $new_status"
echo ""

echo "🔄 Restarting clipboard service..."

# Restart klipper
if pgrep -f klipper >/dev/null; then
    pkill -f klipper 2>/dev/null || true
    sleep 2
fi

if command -v klipper >/dev/null; then
    klipper &
    sleep 2
    
    if pgrep -f klipper >/dev/null; then
        echo "✅ Clipboard service restarted successfully"
    else
        echo "❌ Failed to restart clipboard service"
        echo "💡 Try manually: klipper &"
    fi
else
    echo "⚠️ Klipper command not found"
    echo "💡 Clipboard service may restart automatically"
fi

echo ""
echo "🧪 TESTING RECOMMENDATIONS:"
echo "• Test KCM clipboard: kcmshell6 clipboard"
echo "• If KCM fails: Try option 7 in this script"
echo "• Alternative config: ~/.local/bin/configure-clipboard"
echo ""

if [[ "$new_limit" -gt 1000 ]]; then
    echo "⚠️  PERFORMANCE NOTE:"
    echo "Large clipboard histories may cause:"
    echo "• Slower KCM clipboard loading"
    echo "• Increased memory usage"
    echo "• Potential KCM timeouts"
    echo ""
    echo "💡 If you experience issues, run this script again"
    echo "   and choose a lower limit (options 1-3)"
fi

echo "✅ Clipboard limit management complete!"
echo "📄 Configuration file: $KLIPPER_CONFIG"
echo "📋 Backup saved: $backup_file"
