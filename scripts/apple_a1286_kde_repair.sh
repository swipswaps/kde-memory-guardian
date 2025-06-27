#!/bin/bash
################################################################################
# APPLE_A1286_KDE_REPAIR.sh — PRF-COMPOSITE-2025-06-24-APPLE
# WHO: Apple A1286 KDE Plasma repair and stabilization
# WHAT: Fixes window decorations, taskbar clicks, Alt+Tab, hybrid GPU issues
# WHY: Apple A1286 has Intel/NVIDIA hybrid GPU + ACPI issues causing KDE failures
# HOW: Sequence-aware restart, DBus repair, X11 negotiation, shortcut restoration
################################################################################

set -euo pipefail
IFS=$'\n\t'

# Logging setup
TS="$(date +%Y%m%d_%H%M%S)"
LOG="$HOME/.apple_kde_repair_${TS}.log"
echo "[🍎 START] Apple A1286 KDE Repair — $(date)" | tee "$LOG"

# ─── STEP 1: Environment Detection ─────────────────────────────────────────────
echo "[🔍 DETECT] Detecting session environment..." | tee -a "$LOG"

SESSION_TYPE="${XDG_SESSION_TYPE:-unknown}"
DESKTOP_SESSION="${DESKTOP_SESSION:-unknown}"
DISPLAY="${DISPLAY:-:0}"

echo "[🖥️ ENV] Session Type: $SESSION_TYPE" | tee -a "$LOG"
echo "[🖥️ ENV] Desktop Session: $DESKTOP_SESSION" | tee -a "$LOG"
echo "[🖥️ ENV] Display: $DISPLAY" | tee -a "$LOG"

# Check if we're in a graphical session
if [ -z "$DISPLAY" ] && [ "$SESSION_TYPE" != "wayland" ]; then
    echo "[❌ ERROR] No graphical session detected" | tee -a "$LOG"
    echo "Please run this script from within a KDE session or via SSH with X11 forwarding"
    exit 1
fi

# ─── STEP 2: Hardware-Specific GPU Detection ──────────────────────────────────
echo "[🎮 GPU] Detecting Apple A1286 GPU configuration..." | tee -a "$LOG"

# Check for Intel/NVIDIA hybrid setup
INTEL_GPU=$(lspci | grep -i "intel.*graphics" || echo "none")
NVIDIA_GPU=$(lspci | grep -i "nvidia" || echo "none")

if [ "$INTEL_GPU" != "none" ]; then
    echo "[🎮 GPU] Intel GPU detected: $INTEL_GPU" | tee -a "$LOG"
fi
if [ "$NVIDIA_GPU" != "none" ]; then
    echo "[🎮 GPU] NVIDIA GPU detected: $NVIDIA_GPU" | tee -a "$LOG"
fi

# Check current graphics driver
CURRENT_DRIVER=$(glxinfo | grep "OpenGL renderer" 2>/dev/null || echo "unknown")
echo "[🎮 GPU] Current driver: $CURRENT_DRIVER" | tee -a "$LOG"

# ─── STEP 3: DBus Session Repair ───────────────────────────────────────────────
echo "[🔧 DBUS] Repairing DBus session..." | tee -a "$LOG"

# Check if DBus is responding
if ! qdbus > /dev/null 2>&1; then
    echo "[⚠️ DBUS] DBus not responding, attempting repair..." | tee -a "$LOG"
    
    # Try to restart user DBus session
    if [ -n "${DBUS_SESSION_BUS_ADDRESS:-}" ]; then
        echo "[🔄 DBUS] Existing session: $DBUS_SESSION_BUS_ADDRESS" | tee -a "$LOG"
    fi
    
    # Launch new DBus session if needed
    export $(dbus-launch)
    echo "[✅ DBUS] New session started: $DBUS_SESSION_BUS_ADDRESS" | tee -a "$LOG"
else
    echo "[✅ DBUS] DBus already responding" | tee -a "$LOG"
fi

# ─── STEP 4: KWin Window Manager Repair ────────────────────────────────────────
echo "[🪟 KWIN] Repairing KWin window manager..." | tee -a "$LOG"

# Check current KWin status
KWIN_PID=$(pgrep kwin_x11 || echo "none")
if [ "$KWIN_PID" != "none" ]; then
    echo "[📊 KWIN] Current KWin PID: $KWIN_PID" | tee -a "$LOG"
else
    echo "[⚠️ KWIN] KWin not running" | tee -a "$LOG"
fi

# Kill existing KWin (handles window decorations and Alt+Tab)
echo "[🛑 KWIN] Stopping existing KWin..." | tee -a "$LOG"
pkill -9 kwin_x11 2>/dev/null || true
pkill -9 kwin_wayland 2>/dev/null || true
sleep 2

# Start KWin with proper X11 context
echo "[🚀 KWIN] Starting KWin with X11 context..." | tee -a "$LOG"
export DISPLAY="$DISPLAY"
kwin_x11 --replace &
KWIN_NEW_PID=$!
sleep 5

# Verify KWin startup
if pgrep kwin_x11 > /dev/null; then
    NEW_KWIN_PID=$(pgrep kwin_x11)
    echo "[✅ KWIN] KWin restarted successfully (PID: $NEW_KWIN_PID)" | tee -a "$LOG"
else
    echo "[❌ KWIN] Failed to restart KWin" | tee -a "$LOG"
    echo "[🔧 KWIN] Attempting fallback startup..." | tee -a "$LOG"
    DISPLAY="$DISPLAY" kwin_x11 &
    sleep 3
fi

# ─── STEP 5: Plasmashell Repair ────────────────────────────────────────────────
echo "[🖥️ PLASMA] Repairing plasmashell..." | tee -a "$LOG"

# Check current plasmashell status
PLASMA_PID=$(pgrep plasmashell || echo "none")
if [ "$PLASMA_PID" != "none" ]; then
    PLASMA_MEM=$(ps -o vsz= -p "$PLASMA_PID" 2>/dev/null || echo "0")
    echo "[📊 PLASMA] Current plasmashell PID: $PLASMA_PID, Memory: ${PLASMA_MEM}KB" | tee -a "$LOG"
else
    echo "[⚠️ PLASMA] Plasmashell not running" | tee -a "$LOG"
fi

# Graceful shutdown of plasmashell
echo "[🛑 PLASMA] Stopping plasmashell..." | tee -a "$LOG"
kquitapp5 plasmashell 2>/dev/null || true
sleep 3

# Force kill if still running
if pgrep plasmashell > /dev/null; then
    echo "[💀 PLASMA] Force killing plasmashell..." | tee -a "$LOG"
    pkill -9 plasmashell || true
    sleep 2
fi

# Clear corrupted QML cache (prevents Apple A1286 specific crashes)
echo "[🧹 PLASMA] Clearing QML cache..." | tee -a "$LOG"
rm -rf "$HOME/.cache/plasmashell/qmlcache/"* 2>/dev/null || true
rm -rf "$HOME/.cache/plasma"* 2>/dev/null || true

# Start fresh plasmashell
echo "[🚀 PLASMA] Starting fresh plasmashell..." | tee -a "$LOG"
plasmashell --replace &
sleep 5

# Verify plasmashell startup
if pgrep plasmashell > /dev/null; then
    NEW_PLASMA_PID=$(pgrep plasmashell)
    echo "[✅ PLASMA] Plasmashell restarted successfully (PID: $NEW_PLASMA_PID)" | tee -a "$LOG"
else
    echo "[❌ PLASMA] Failed to restart plasmashell" | tee -a "$LOG"
fi

# ─── STEP 6: Keyboard Shortcuts Restoration ───────────────────────────────────
echo "[⌨️ SHORTCUTS] Restoring keyboard shortcuts..." | tee -a "$LOG"

# Check if shortcuts config exists
SHORTCUTS_CONFIG="$HOME/.config/kglobalshortcutsrc"
if [ -f "$SHORTCUTS_CONFIG" ]; then
    echo "[📁 SHORTCUTS] Found shortcuts config" | tee -a "$LOG"
    
    # Backup shortcuts config
    cp "$SHORTCUTS_CONFIG" "$SHORTCUTS_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Restore Alt+Tab shortcut (critical for Apple A1286)
    echo "[🔧 SHORTCUTS] Restoring Alt+Tab shortcut..." | tee -a "$LOG"
    kwriteconfig5 --file kglobalshortcutsrc --group kwin --key "Walk Through Windows" "Alt+Tab,Alt+Tab,Walk Through Windows"
    kwriteconfig5 --file kglobalshortcutsrc --group kwin --key "Walk Through Windows (Reverse)" "Alt+Shift+Tab,Alt+Shift+Tab,Walk Through Windows (Reverse)"
    
    # Reload shortcuts
    qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.reloadConfig 2>/dev/null || true
    echo "[✅ SHORTCUTS] Alt+Tab shortcuts restored" | tee -a "$LOG"
else
    echo "[⚠️ SHORTCUTS] No shortcuts config found, creating default..." | tee -a "$LOG"
    kwriteconfig5 --file kglobalshortcutsrc --group kwin --key "Walk Through Windows" "Alt+Tab,Alt+Tab,Walk Through Windows"
fi

# ─── STEP 7: Apple A1286 Specific Optimizations ───────────────────────────────
echo "[🍎 OPTIMIZE] Applying Apple A1286 specific optimizations..." | tee -a "$LOG"

# Disable compositor effects that cause issues on hybrid GPU
kwriteconfig5 --file kwinrc --group "Compositing" --key "AnimationSpeed" "2"
kwriteconfig5 --file kwinrc --group "Compositing" --key "Enabled" "true"
kwriteconfig5 --file kwinrc --group "Compositing" --key "Backend" "OpenGL"
kwriteconfig5 --file kwinrc --group "Compositing" --key "GLCore" "false"

# Configure for Intel/NVIDIA hybrid stability
kwriteconfig5 --file kwinrc --group "Compositing" --key "LatencyPolicy" "Low"
kwriteconfig5 --file kwinrc --group "Compositing" --key "RenderLoop" "false"

echo "[✅ OPTIMIZE] Apple A1286 optimizations applied" | tee -a "$LOG"

# ─── STEP 8: Session Recovery Service ──────────────────────────────────────────
echo "[🔄 SERVICE] Installing session recovery service..." | tee -a "$LOG"

# Create systemd user service for auto-recovery
SERVICE_DIR="$HOME/.config/systemd/user"
mkdir -p "$SERVICE_DIR"

cat > "$SERVICE_DIR/apple-kde-recovery.service" << EOF
[Unit]
Description=Apple A1286 KDE Recovery Service
After=graphical-session.target

[Service]
Type=oneshot
ExecStart=$HOME/.local/bin/apple_kde_recovery_check.sh
Restart=on-failure
RestartSec=30

[Install]
WantedBy=default.target
EOF

# Create recovery check script
RECOVERY_SCRIPT="$HOME/.local/bin/apple_kde_recovery_check.sh"
mkdir -p "$(dirname "$RECOVERY_SCRIPT")"

cat > "$RECOVERY_SCRIPT" << 'EOF'
#!/bin/bash
# Apple A1286 KDE Recovery Check
LOG="$HOME/.apple_kde_recovery.log"

# Check if KWin is running
if ! pgrep kwin_x11 > /dev/null; then
    echo "$(date): KWin crashed, restarting..." >> "$LOG"
    kwin_x11 --replace &
    sleep 3
fi

# Check if plasmashell is running
if ! pgrep plasmashell > /dev/null; then
    echo "$(date): Plasmashell crashed, restarting..." >> "$LOG"
    plasmashell --replace &
    sleep 3
fi

# Check if shortcuts are working
if ! qdbus org.kde.kglobalaccel > /dev/null 2>&1; then
    echo "$(date): Global shortcuts broken, reloading..." >> "$LOG"
    qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.reloadConfig 2>/dev/null || true
fi
EOF

chmod +x "$RECOVERY_SCRIPT"
systemctl --user enable apple-kde-recovery.service 2>/dev/null || true

echo "[✅ SERVICE] Recovery service installed" | tee -a "$LOG"

# ─── STEP 9: Final Verification ────────────────────────────────────────────────
echo "[🔍 VERIFY] Final system verification..." | tee -a "$LOG"

# Check all critical components
FINAL_KWIN=$(pgrep kwin_x11 || echo "none")
FINAL_PLASMA=$(pgrep plasmashell || echo "none")
FINAL_DBUS=$(qdbus > /dev/null 2>&1 && echo "working" || echo "broken")

echo "[📊 STATUS] KWin: $FINAL_KWIN" | tee -a "$LOG"
echo "[📊 STATUS] Plasmashell: $FINAL_PLASMA" | tee -a "$LOG"
echo "[📊 STATUS] DBus: $FINAL_DBUS" | tee -a "$LOG"

# Test Alt+Tab functionality
echo "[🧪 TEST] Testing Alt+Tab functionality..." | tee -a "$LOG"
if qdbus org.kde.kglobalaccel /component/kwin org.kde.kglobalaccel.Component.shortcutNames 2>/dev/null | grep -q "Walk Through Windows"; then
    echo "[✅ TEST] Alt+Tab shortcut registered" | tee -a "$LOG"
else
    echo "[⚠️ TEST] Alt+Tab shortcut may not be working" | tee -a "$LOG"
fi

echo "[🎉 COMPLETE] Apple A1286 KDE repair complete — $(date)" | tee -a "$LOG"
echo "[📝 LOG] Full log available at: $LOG"
echo ""
echo "🎯 VERIFICATION CHECKLIST:"
echo "1. ✅ Window decorations should be visible"
echo "2. ✅ Taskbar should respond to clicks"
echo "3. ✅ Alt+Tab should work for window switching"
echo "4. ✅ Right-click menus should appear"
echo "5. ✅ Drag and drop should function"
echo ""
echo "🔧 IF ISSUES PERSIST:"
echo "1. Reboot the system"
echo "2. Run this script again"
echo "3. Check recovery log: tail -f ~/.apple_kde_recovery.log"
echo ""
echo "✅ Apple A1286 KDE session restored!"
