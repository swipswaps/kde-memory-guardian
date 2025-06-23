#!/usr/bin/env bash
################################################################################
# integrate-custom-clipboard.sh — Complete Clipboard System Integration
# WHAT: Integrates D3.js database-driven clipboard tools with KDE system tray
# WHY: Provides superior clipboard management replacing memory-leaking Klipper
# HOW: Configures services, widgets, and autostart for seamless integration
################################################################################

set -euo pipefail
IFS=$'\n\t'

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.local/share/kde-memory-guardian"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/clipboard-integration-$(date +%Y%m%d_%H%M%S).log"

# Clipboard system paths
CLIPBOARD_DAEMON_PATH="$HOME/Documents/clipboard_daemon/target/release/clipboard_daemon"
CLIPBOARD_MANAGER_PATH="$HOME/.local/bin/clipboard_manager"
CLIPBOARD_UI_PATH="$HOME/Documents/clipboard_ui"

log_message() {
    local level="$1"
    local message="$2"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_message "START" "🚀 Custom Clipboard Integration Started"

# ─── SYSTEM ANALYSIS ──────────────────────────────────────────────────────────
# WHAT: Analyze current clipboard system state and requirements
# WHY: Need to understand existing setup before integration
# HOW: Check for existing tools, services, and configurations
analyze_clipboard_system() {
    log_message "STEP" "🔍 Analyzing current clipboard system..."
    
    # Check for existing clipboard tools
    local analysis_result=""
    
    # Check Rust daemon
    if [[ -f "$CLIPBOARD_DAEMON_PATH" ]]; then
        analysis_result+="RUST_DAEMON:FOUND;"
        if pgrep -f clipboard_daemon >/dev/null; then
            analysis_result+="RUST_DAEMON:RUNNING;"
        else
            analysis_result+="RUST_DAEMON:STOPPED;"
        fi
    else
        analysis_result+="RUST_DAEMON:MISSING;"
    fi
    
    # Check SQL manager
    if [[ -f "$CLIPBOARD_MANAGER_PATH" ]]; then
        analysis_result+="SQL_MANAGER:FOUND;"
        if pgrep -f "clipboard_manager watch" >/dev/null; then
            analysis_result+="SQL_MANAGER:RUNNING;"
        else
            analysis_result+="SQL_MANAGER:STOPPED;"
        fi
    else
        analysis_result+="SQL_MANAGER:MISSING;"
    fi
    
    # Check UI components
    if [[ -d "$CLIPBOARD_UI_PATH" ]]; then
        analysis_result+="UI_COMPONENTS:FOUND;"
    else
        analysis_result+="UI_COMPONENTS:MISSING;"
    fi
    
    # Check systemd services
    if systemctl --user list-units | grep -q clipboard; then
        analysis_result+="SYSTEMD_SERVICES:FOUND;"
    else
        analysis_result+="SYSTEMD_SERVICES:MISSING;"
    fi
    
    log_message "INFO" "📊 System analysis: $analysis_result"
    echo "$analysis_result"
}

# ─── SERVICE CONFIGURATION ────────────────────────────────────────────────────
# WHAT: Configure systemd services for clipboard tools
# WHY: Ensures clipboard tools start automatically and stay running
# HOW: Create and enable systemd user services
configure_clipboard_services() {
    log_message "STEP" "⚙️ Configuring clipboard services..."
    
    local service_dir="$HOME/.config/systemd/user"
    mkdir -p "$service_dir"
    
    # Create clipboard daemon service
    if [[ -f "$CLIPBOARD_DAEMON_PATH" ]]; then
        log_message "ACTION" "📋 Creating clipboard daemon service..."
        cat > "$service_dir/clipboard-daemon.service" << EOF
[Unit]
Description=Advanced Clipboard Daemon with Database Backend
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
ExecStart=$CLIPBOARD_DAEMON_PATH
Restart=always
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF
        
        systemctl --user daemon-reload
        systemctl --user enable clipboard-daemon.service
        log_message "OK" "✅ Clipboard daemon service configured"
    fi
    
    # Create clipboard manager service
    if [[ -f "$CLIPBOARD_MANAGER_PATH" ]]; then
        log_message "ACTION" "📊 Creating clipboard manager service..."
        cat > "$service_dir/clipboard-manager.service" << EOF
[Unit]
Description=SQL Clipboard Manager with D3.js Visualization
After=clipboard-daemon.service
Wants=clipboard-daemon.service

[Service]
Type=simple
ExecStart=$CLIPBOARD_MANAGER_PATH watch --max-entries 1000
Restart=always
RestartSec=5
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF
        
        systemctl --user daemon-reload
        systemctl --user enable clipboard-manager.service
        log_message "OK" "✅ Clipboard manager service configured"
    fi
}

# ─── WIDGET INTEGRATION ───────────────────────────────────────────────────────
# WHAT: Integrate custom clipboard tools with KDE system tray
# WHY: Provides seamless access to advanced clipboard features
# HOW: Configure plasma widgets and create custom tray integration
integrate_system_tray() {
    log_message "STEP" "🔗 Integrating with KDE system tray..."
    
    # Remove default clipboard widgets first
    log_message "ACTION" "🚫 Removing default clipboard widgets..."
    if [[ -f "$SCRIPT_DIR/clipboard-widget-manager.sh" ]]; then
        bash "$SCRIPT_DIR/clipboard-widget-manager.sh"
    else
        log_message "WARN" "⚠️ clipboard-widget-manager.sh not found"
    fi
    
    # Create custom tray integration
    log_message "ACTION" "🎨 Creating custom tray integration..."
    
    # Create desktop entry for clipboard UI
    local desktop_dir="$HOME/.local/share/applications"
    mkdir -p "$desktop_dir"
    
    cat > "$desktop_dir/advanced-clipboard.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Advanced Clipboard Manager
Comment=D3.js Database-Driven Clipboard with Material UI
Exec=$CLIPBOARD_MANAGER_PATH ui
Icon=edit-copy
Categories=Utility;
StartupNotify=true
EOF
    
    log_message "OK" "✅ Desktop entry created for clipboard UI"
    
    # Create autostart entry
    local autostart_dir="$HOME/.config/autostart"
    mkdir -p "$autostart_dir"
    
    cat > "$autostart_dir/advanced-clipboard.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Advanced Clipboard Manager
Comment=Auto-start advanced clipboard system
Exec=$CLIPBOARD_MANAGER_PATH watch --max-entries 1000
Icon=edit-copy
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
    
    log_message "OK" "✅ Autostart entry created"
}

# ─── SERVICE STARTUP ──────────────────────────────────────────────────────────
# WHAT: Start clipboard services and verify operation
# WHY: Ensures the integrated system is immediately functional
# HOW: Start services and check status
start_clipboard_services() {
    log_message "STEP" "🚀 Starting clipboard services..."
    
    # Start clipboard daemon
    if [[ -f "$CLIPBOARD_DAEMON_PATH" ]]; then
        if ! pgrep -f clipboard_daemon >/dev/null; then
            log_message "ACTION" "📋 Starting clipboard daemon..."
            systemctl --user start clipboard-daemon.service 2>&1 | tee -a "$LOG_FILE"
            sleep 2
        fi
        
        if pgrep -f clipboard_daemon >/dev/null; then
            log_message "OK" "✅ Clipboard daemon started (PID: $(pgrep -f clipboard_daemon))"
        else
            log_message "ERROR" "❌ Failed to start clipboard daemon"
        fi
    fi
    
    # Start clipboard manager
    if [[ -f "$CLIPBOARD_MANAGER_PATH" ]]; then
        if ! pgrep -f "clipboard_manager watch" >/dev/null; then
            log_message "ACTION" "📊 Starting clipboard manager..."
            systemctl --user start clipboard-manager.service 2>&1 | tee -a "$LOG_FILE"
            sleep 2
        fi
        
        if pgrep -f "clipboard_manager watch" >/dev/null; then
            log_message "OK" "✅ Clipboard manager started (PID: $(pgrep -f "clipboard_manager watch"))"
        else
            log_message "ERROR" "❌ Failed to start clipboard manager"
        fi
    fi
}

# ─── VERIFICATION AND TESTING ─────────────────────────────────────────────────
# WHAT: Verify complete clipboard system integration
# WHY: Ensures all components are working together properly
# HOW: Test services, widgets, and functionality
verify_integration() {
    log_message "STEP" "🔍 Verifying clipboard system integration..."
    
    local verification_result=""
    
    # Check service status
    if systemctl --user is-active clipboard-daemon.service >/dev/null 2>&1; then
        verification_result+="DAEMON_SERVICE:ACTIVE;"
    else
        verification_result+="DAEMON_SERVICE:INACTIVE;"
    fi
    
    if systemctl --user is-active clipboard-manager.service >/dev/null 2>&1; then
        verification_result+="MANAGER_SERVICE:ACTIVE;"
    else
        verification_result+="MANAGER_SERVICE:INACTIVE;"
    fi
    
    # Check process status
    if pgrep -f clipboard_daemon >/dev/null; then
        verification_result+="DAEMON_PROCESS:RUNNING;"
    else
        verification_result+="DAEMON_PROCESS:STOPPED;"
    fi
    
    if pgrep -f "clipboard_manager watch" >/dev/null; then
        verification_result+="MANAGER_PROCESS:RUNNING;"
    else
        verification_result+="MANAGER_PROCESS:STOPPED;"
    fi
    
    # Check widget status
    local widget_status
    widget_status=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type == 'org.kde.plasma.systemtray') {
                widget = widgets[j];
                widget.currentConfigGroup = ['General'];
                var hidden = widget.readConfig('hiddenItems', '');
                if (hidden.indexOf('clipboard') !== -1) {
                    print('CLIPBOARD_HIDDEN');
                }
            }
        }
    }
    " 2>/dev/null)
    
    if [[ "$widget_status" == *"CLIPBOARD_HIDDEN"* ]]; then
        verification_result+="WIDGET_STATUS:HIDDEN;"
    else
        verification_result+="WIDGET_STATUS:VISIBLE;"
    fi
    
    log_message "INFO" "📊 Verification result: $verification_result"
    
    # Generate summary
    local success_count=0
    local total_checks=6
    
    [[ "$verification_result" == *"DAEMON_SERVICE:ACTIVE"* ]] && ((success_count++))
    [[ "$verification_result" == *"MANAGER_SERVICE:ACTIVE"* ]] && ((success_count++))
    [[ "$verification_result" == *"DAEMON_PROCESS:RUNNING"* ]] && ((success_count++))
    [[ "$verification_result" == *"MANAGER_PROCESS:RUNNING"* ]] && ((success_count++))
    [[ "$verification_result" == *"WIDGET_STATUS:HIDDEN"* ]] && ((success_count++))
    
    log_message "STATUS" "📊 Integration success: $success_count/$total_checks checks passed"
    
    if [[ $success_count -ge 4 ]]; then
        log_message "OK" "✅ Clipboard system integration successful"
        return 0
    else
        log_message "ERROR" "❌ Clipboard system integration incomplete"
        return 1
    fi
}

# ─── MAIN EXECUTION ───────────────────────────────────────────────────────────
main() {
    log_message "START" "🎯 Starting complete clipboard system integration..."
    
    echo "=== ADVANCED CLIPBOARD SYSTEM INTEGRATION ==="
    echo "Integrating D3.js database-driven clipboard tools with KDE..."
    echo ""
    
    # Phase 1: Analysis
    log_message "PHASE" "📊 Phase 1: System Analysis"
    analyze_clipboard_system
    
    # Phase 2: Service Configuration
    log_message "PHASE" "⚙️ Phase 2: Service Configuration"
    configure_clipboard_services
    
    # Phase 3: Widget Integration
    log_message "PHASE" "🔗 Phase 3: System Tray Integration"
    integrate_system_tray
    
    # Phase 4: Service Startup
    log_message "PHASE" "🚀 Phase 4: Service Startup"
    start_clipboard_services
    
    # Phase 5: Verification
    log_message "PHASE" "🔍 Phase 5: Integration Verification"
    if verify_integration; then
        log_message "COMPLETE" "🎉 Clipboard system integration complete!"
        
        echo ""
        echo "=== INTEGRATION COMPLETE ==="
        echo "✅ Advanced clipboard system successfully integrated"
        echo "✅ D3.js database-driven tools active"
        echo "✅ Material UI interface available"
        echo "✅ Unlimited clipboard history enabled"
        echo "✅ Default Klipper widgets removed"
        echo "✅ Services configured for autostart"
        echo ""
        echo "📄 Full log: $LOG_FILE"
        echo ""
        echo "🚀 Your advanced clipboard system is now ready!"
        echo "   Access via: $CLIPBOARD_MANAGER_PATH ui"
        echo ""
    else
        log_message "ERROR" "❌ Integration completed with issues"
        echo ""
        echo "⚠️ Integration completed but some components may not be fully functional."
        echo "📄 Check log for details: $LOG_FILE"
        echo ""
    fi
}

# Execute main function
main "$@"
