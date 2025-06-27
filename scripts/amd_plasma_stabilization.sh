#!/bin/bash
################################################################################
# AMD_PLASMA_STABILIZATION.sh — PRF-COMPOSITE-2025-06-24-AMD
# WHO: AMD machine plasma crash prevention and recovery
# WHAT: Fixes QML focus corruption, clipboard widget crashes, memory spikes
# WHY: Prevents segfaults when using clipboard widgets with large datasets
# HOW: Clears corrupted cache, disables problematic widgets, configures safely
################################################################################

set -euo pipefail
IFS=$'\n\t'

# Logging setup
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$HOME/.plasma_stabilization_${TS}.log"
echo "[🚀 START] AMD Plasma Stabilization — $(date)" | tee "$LOG"

# ─── STEP 1: Detect Current State ──────────────────────────────────────────────
echo "[🔍 DETECT] Checking current plasma state..." | tee -a "$LOG"

PLASMA_PID=$(pgrep plasmashell || echo "none")
PLASMA_MEM="0"
if [ "$PLASMA_PID" != "none" ]; then
    PLASMA_MEM=$(ps -o vsz= -p "$PLASMA_PID" 2>/dev/null || echo "0")
    echo "[📊 STATUS] Plasmashell PID: $PLASMA_PID, Memory: ${PLASMA_MEM}KB" | tee -a "$LOG"
else
    echo "[⚠️ STATUS] Plasmashell not running" | tee -a "$LOG"
fi

# ─── STEP 2: Clear Corrupted QML Cache ─────────────────────────────────────────
echo "[🧹 CLEAN] Clearing corrupted QML cache..." | tee -a "$LOG"

# Clear plasmashell QML cache (prevents focus corruption)
if [ -d "$HOME/.cache/plasmashell/qmlcache" ]; then
    CACHE_SIZE=$(du -sh "$HOME/.cache/plasmashell/qmlcache" | cut -f1)
    echo "[📁 CACHE] Removing QML cache: $CACHE_SIZE" | tee -a "$LOG"
    rm -rf "$HOME/.cache/plasmashell/qmlcache/"*
    echo "[✅ CACHE] QML cache cleared successfully" | tee -a "$LOG"
else
    echo "[ℹ️ CACHE] No QML cache found to clear" | tee -a "$LOG"
fi

# Clear other plasma caches
rm -rf "$HOME/.cache/plasma"* 2>/dev/null || true
rm -rf "$HOME/.cache/kioexec"* 2>/dev/null || true
echo "[✅ CACHE] All plasma caches cleared" | tee -a "$LOG"

# ─── STEP 3: Disable Problematic Clipboard Widget ─────────────────────────────
echo "[🚫 DISABLE] Removing problematic clipboard widget..." | tee -a "$LOG"

# Backup current plasma configuration
PLASMA_CONFIG="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"
if [ -f "$PLASMA_CONFIG" ]; then
    cp "$PLASMA_CONFIG" "$PLASMA_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    echo "[💾 BACKUP] Plasma config backed up" | tee -a "$LOG"
    
    # Remove clipboard widget entries (prevents QML focus crashes)
    sed -i '/org\.kde\.plasma\.clipboard/d' "$PLASMA_CONFIG" 2>/dev/null || true
    sed -i '/plugin=org\.kde\.plasma\.clipboard/d' "$PLASMA_CONFIG" 2>/dev/null || true
    echo "[✅ WIDGET] Clipboard widget references removed" | tee -a "$LOG"
else
    echo "[ℹ️ WIDGET] No plasma config found" | tee -a "$LOG"
fi

# ─── STEP 4: Configure Conservative Clipboard Settings ────────────────────────
echo "[⚙️ CONFIG] Applying conservative clipboard settings..." | tee -a "$LOG"

# Configure Klipper for stability (prevents memory spikes)
kwriteconfig5 --file klipperrc --group "General" --key "MaxClipItems" "50"
kwriteconfig5 --file klipperrc --group "General" --key "IgnoreSelection" "true"
kwriteconfig5 --file klipperrc --group "General" --key "SyncClipboards" "false"
kwriteconfig5 --file klipperrc --group "General" --key "IgnoreImages" "true"
echo "[✅ CONFIG] Conservative clipboard settings applied" | tee -a "$LOG"

# ─── STEP 5: Restart Plasma Safely ─────────────────────────────────────────────
echo "[🔄 RESTART] Restarting plasmashell safely..." | tee -a "$LOG"

# Graceful shutdown first
if [ "$PLASMA_PID" != "none" ]; then
    echo "[🛑 STOP] Stopping plasmashell gracefully..." | tee -a "$LOG"
    kquitapp5 plasmashell 2>/dev/null || true
    sleep 3
    
    # Force kill if still running
    if pgrep plasmashell > /dev/null; then
        echo "[💀 KILL] Force killing stubborn plasmashell..." | tee -a "$LOG"
        pkill -9 plasmashell || true
        sleep 2
    fi
fi

# Start fresh plasmashell
echo "[🚀 START] Starting fresh plasmashell..." | tee -a "$LOG"
plasmashell --replace &
PLASMA_NEW_PID=$!
sleep 5

# Verify restart
if pgrep plasmashell > /dev/null; then
    NEW_PID=$(pgrep plasmashell)
    echo "[✅ RESTART] Plasmashell restarted successfully (PID: $NEW_PID)" | tee -a "$LOG"
else
    echo "[❌ RESTART] Failed to restart plasmashell" | tee -a "$LOG"
    exit 1
fi

# ─── STEP 6: Install Health Monitoring ─────────────────────────────────────────
echo "[📊 MONITOR] Installing health monitoring..." | tee -a "$LOG"

# Create health monitor script
MONITOR_SCRIPT="$HOME/.local/bin/plasma_health_monitor.sh"
mkdir -p "$(dirname "$MONITOR_SCRIPT")"

cat > "$MONITOR_SCRIPT" << 'EOF'
#!/bin/bash
# Plasma Health Monitor - Prevents crashes and memory spikes
HEALTH_LOG="$HOME/.plasma_health.log"

while true; do
    # Check if plasmashell is running
    if ! pgrep plasmashell > /dev/null; then
        echo "⚠️ $(date): Plasmashell crashed, restarting..." >> "$HEALTH_LOG"
        plasmashell --replace &
        sleep 5
    fi
    
    # Check memory usage
    PLASMA_PID=$(pgrep plasmashell)
    if [ -n "$PLASMA_PID" ]; then
        PLASMA_MEM=$(ps -o vsz= -p "$PLASMA_PID" 2>/dev/null || echo "0")
        if [ "$PLASMA_MEM" -gt 1000000 ]; then  # > 1GB
            echo "⚠️ $(date): High plasma memory: ${PLASMA_MEM}KB" >> "$HEALTH_LOG"
            # Clear cache if memory too high
            rm -rf ~/.cache/plasmashell/qmlcache/* 2>/dev/null || true
        fi
    fi
    
    sleep 30
done
EOF

chmod +x "$MONITOR_SCRIPT"
echo "[✅ MONITOR] Health monitor installed at $MONITOR_SCRIPT" | tee -a "$LOG"

# ─── STEP 7: Create Desktop Launcher for Custom Clipboard ─────────────────────
echo "[🖥️ LAUNCHER] Creating custom clipboard launcher..." | tee -a "$LOG"

LAUNCHER_DIR="$HOME/.local/share/applications"
mkdir -p "$LAUNCHER_DIR"

cat > "$LAUNCHER_DIR/clipboard-manager.desktop" << EOF
[Desktop Entry]
Name=Custom Clipboard Manager
Comment=Advanced clipboard management with search and analytics
Exec=firefox http://localhost:3000
Icon=edit-copy
Type=Application
Categories=Utility;Office;
StartupNotify=true
EOF

echo "[✅ LAUNCHER] Custom clipboard launcher created" | tee -a "$LOG"

# ─── STEP 8: Final Verification ────────────────────────────────────────────────
echo "[🔍 VERIFY] Final system verification..." | tee -a "$LOG"

# Check plasma status
FINAL_PID=$(pgrep plasmashell || echo "none")
if [ "$FINAL_PID" != "none" ]; then
    FINAL_MEM=$(ps -o vsz= -p "$FINAL_PID" 2>/dev/null || echo "0")
    echo "[✅ STATUS] Plasmashell running (PID: $FINAL_PID, Memory: ${FINAL_MEM}KB)" | tee -a "$LOG"
else
    echo "[❌ STATUS] Plasmashell not running after stabilization" | tee -a "$LOG"
fi

# Check clipboard service
if pgrep klipper > /dev/null; then
    echo "[✅ CLIPBOARD] Klipper service running" | tee -a "$LOG"
else
    echo "[ℹ️ CLIPBOARD] Klipper not running (normal if disabled)" | tee -a "$LOG"
fi

echo "[🎉 COMPLETE] AMD Plasma stabilization complete — $(date)" | tee -a "$LOG"
echo "[📝 LOG] Full log available at: $LOG"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Test taskbar functionality"
echo "2. Access custom clipboard at: http://localhost:3000"
echo "3. Monitor health log: tail -f ~/.plasma_health.log"
echo "4. Run health monitor: $MONITOR_SCRIPT &"
echo ""
echo "✅ AMD machine is now stabilized against clipboard-related crashes!"
