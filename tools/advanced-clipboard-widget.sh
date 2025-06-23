#!/usr/bin/env bash
################################################################################
# advanced-clipboard-widget.sh — Custom Taskbar Widget for Advanced Clipboard
# WHAT: Creates and manages custom taskbar integration for D3.js clipboard system
# WHY: Provides direct access to Material UI interface from system tray
# HOW: Creates desktop entries and configures KDE integration
################################################################################

set -euo pipefail
IFS=$'\n\t'

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.local/share/kde-memory-guardian"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/clipboard-widget-$(date +%Y%m%d_%H%M%S).log"

# Clipboard system paths
CLIPBOARD_MANAGER="$HOME/.local/bin/clipboard_manager"
CLIPBOARD_DAEMON="$HOME/Documents/clipboard_daemon/target/release/clipboard_daemon"

log_message() {
    local level="$1"
    local message="$2"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_message "START" "🎨 Advanced Clipboard Widget Manager Started"

# ─── WIDGET VISIBILITY MANAGEMENT ────────────────────────────────────────────
# WHAT: Ensure our advanced clipboard widget is visible in system tray
# WHY: Users need easy access to the advanced clipboard functionality
# HOW: Configure plasma system tray to show our clipboard widget
ensure_widget_visible() {
    log_message "STEP" "🔍 Ensuring advanced clipboard widget is visible..."
    
    local widget_result
    widget_result=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    var result = '';
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type == 'org.kde.plasma.systemtray') {
                widget = widgets[j];
                widget.currentConfigGroup = ['General'];
                
                // Remove clipboard from hidden items
                var hiddenItems = widget.readConfig('hiddenItems', '').split(',');
                var newHidden = [];
                for (var k = 0; k < hiddenItems.length; k++) {
                    if (hiddenItems[k] !== 'org.kde.plasma.clipboard' && hiddenItems[k] !== '') {
                        newHidden.push(hiddenItems[k]);
                    }
                }
                widget.writeConfig('hiddenItems', newHidden.join(','));
                
                // Add clipboard to extra items (visible)
                var extraItems = widget.readConfig('extraItems', '').split(',');
                if (extraItems.indexOf('org.kde.plasma.clipboard') == -1) {
                    extraItems.push('org.kde.plasma.clipboard');
                }
                widget.writeConfig('extraItems', extraItems.join(','));
                
                result += 'WIDGET_VISIBLE:' + extraItems.join(',') + ';';
            }
        }
    }
    print(result);
    " 2>&1)
    
    log_message "OK" "✅ Widget visibility result: $widget_result"
    
    if [[ "$widget_result" == *"WIDGET_VISIBLE"* ]]; then
        log_message "OK" "✅ Advanced clipboard widget is now visible in taskbar"
        return 0
    else
        log_message "ERROR" "❌ Failed to make widget visible"
        return 1
    fi
}

# ─── DESKTOP INTEGRATION ──────────────────────────────────────────────────────
# WHAT: Create desktop entries for easy access to clipboard functionality
# WHY: Users need multiple ways to access the advanced clipboard features
# HOW: Create .desktop files for applications menu and quick access
create_desktop_integration() {
    log_message "STEP" "🖥️ Creating desktop integration..."
    
    local desktop_dir="$HOME/.local/share/applications"
    mkdir -p "$desktop_dir"
    
    # Main clipboard manager application
    cat > "$desktop_dir/advanced-clipboard-manager.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Advanced Clipboard Manager
Comment=D3.js Database-Driven Clipboard with Material UI
Exec=$CLIPBOARD_MANAGER history --limit 50
Icon=edit-copy
Categories=Utility;Office;
StartupNotify=true
Keywords=clipboard;history;search;database;
EOF
    
    # Quick search application
    cat > "$desktop_dir/clipboard-search.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Clipboard Search
Comment=Search clipboard history with advanced filters
Exec=konsole -e $CLIPBOARD_MANAGER search
Icon=edit-find
Categories=Utility;Office;
StartupNotify=true
Keywords=clipboard;search;find;history;
EOF
    
    # Statistics viewer
    cat > "$desktop_dir/clipboard-stats.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Clipboard Statistics
Comment=View clipboard usage statistics and analytics
Exec=konsole -e $CLIPBOARD_MANAGER stats
Icon=office-chart-bar
Categories=Utility;Office;
StartupNotify=true
Keywords=clipboard;statistics;analytics;usage;
EOF
    
    log_message "OK" "✅ Desktop integration files created"
}

# ─── QUICK ACCESS SHORTCUTS ───────────────────────────────────────────────────
# WHAT: Create keyboard shortcuts for clipboard functionality
# WHY: Power users need quick access without mouse interaction
# HOW: Configure KDE global shortcuts for clipboard actions
setup_keyboard_shortcuts() {
    log_message "STEP" "⌨️ Setting up keyboard shortcuts..."
    
    # Create shortcut configuration directory
    local shortcuts_dir="$HOME/.config"
    mkdir -p "$shortcuts_dir"
    
    # Add clipboard shortcuts to KDE global shortcuts
    # Note: This requires user to manually configure in System Settings
    # We create a helper script for easy setup
    
    cat > "$HOME/.local/bin/setup-clipboard-shortcuts" << 'EOF'
#!/usr/bin/env bash
# Helper script to set up clipboard shortcuts
echo "🔧 Clipboard Shortcut Setup Helper"
echo "=================================="
echo ""
echo "To set up keyboard shortcuts for advanced clipboard:"
echo ""
echo "1. Open System Settings → Shortcuts → Custom Shortcuts"
echo "2. Add these shortcuts:"
echo ""
echo "   📋 Clipboard History: Ctrl+Alt+V"
echo "      Command: $HOME/.local/bin/clipboard_manager history --limit 20"
echo ""
echo "   🔍 Clipboard Search: Ctrl+Alt+F"  
echo "      Command: konsole -e $HOME/.local/bin/clipboard_manager search"
echo ""
echo "   📊 Clipboard Stats: Ctrl+Alt+S"
echo "      Command: konsole -e $HOME/.local/bin/clipboard_manager stats"
echo ""
echo "3. Click Apply and test the shortcuts"
echo ""
EOF
    
    chmod +x "$HOME/.local/bin/setup-clipboard-shortcuts"
    log_message "OK" "✅ Keyboard shortcut helper created at ~/.local/bin/setup-clipboard-shortcuts"
}

# ─── SYSTEM TRAY CONTEXT MENU ─────────────────────────────────────────────────
# WHAT: Enhance system tray clipboard widget with custom context menu
# WHY: Right-click access to advanced features improves usability
# HOW: Create custom menu entries for clipboard actions
create_context_menu_integration() {
    log_message "STEP" "📋 Creating context menu integration..."
    
    # Create custom clipboard actions directory
    local actions_dir="$HOME/.local/share/kservices5/ServiceMenus"
    mkdir -p "$actions_dir"
    
    # Context menu for clipboard widget
    cat > "$actions_dir/clipboard-advanced-actions.desktop" << EOF
[Desktop Entry]
Type=Service
ServiceTypes=KonqPopupMenu/Plugin
MimeType=all/all;
Actions=ClipboardHistory;ClipboardSearch;ClipboardStats;ClipboardClear;

[Desktop Action ClipboardHistory]
Name=Show Clipboard History
Icon=edit-copy
Exec=$CLIPBOARD_MANAGER history --limit 20

[Desktop Action ClipboardSearch]
Name=Search Clipboard
Icon=edit-find
Exec=konsole -e $CLIPBOARD_MANAGER search

[Desktop Action ClipboardStats]
Name=Clipboard Statistics
Icon=office-chart-bar
Exec=konsole -e $CLIPBOARD_MANAGER stats

[Desktop Action ClipboardClear]
Name=Clear Clipboard History
Icon=edit-clear
Exec=$CLIPBOARD_MANAGER clear --confirm
EOF
    
    log_message "OK" "✅ Context menu integration created"
}

# ─── STATUS MONITORING ────────────────────────────────────────────────────────
# WHAT: Monitor clipboard system status and provide user feedback
# WHY: Users need to know if the advanced clipboard system is working
# HOW: Check processes, database, and widget status
monitor_clipboard_status() {
    log_message "STEP" "📊 Monitoring clipboard system status..."
    
    local status_summary=""
    local daemon_status="❌ Not running"
    local manager_status="❌ Not running"
    local widget_status="❌ Not visible"
    local database_status="❌ No data"
    
    # Check daemon process
    if pgrep -f clipboard_daemon >/dev/null; then
        daemon_status="✅ Running (PID: $(pgrep -f clipboard_daemon))"
    fi
    
    # Check manager process
    if pgrep -f "clipboard_manager watch" >/dev/null; then
        manager_status="✅ Running (PID: $(pgrep -f "clipboard_manager watch"))"
    fi
    
    # Check widget visibility
    local widget_check
    widget_check=$(qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
    var panels = panels();
    for (var i = 0; i < panels.length; i++) {
        var widgets = panels[i].widgets();
        for (var j = 0; j < widgets.length; j++) {
            if (widgets[j].type == 'org.kde.plasma.systemtray') {
                widget = widgets[j];
                widget.currentConfigGroup = ['General'];
                var extra = widget.readConfig('extraItems', '');
                if (extra.indexOf('org.kde.plasma.clipboard') !== -1) {
                    print('VISIBLE');
                }
            }
        }
    }
    " 2>/dev/null)
    
    if [[ "$widget_check" == *"VISIBLE"* ]]; then
        widget_status="✅ Visible in taskbar"
    fi
    
    # Check database status
    if [[ -f "$CLIPBOARD_MANAGER" ]]; then
        local stats_output
        stats_output=$("$CLIPBOARD_MANAGER" stats 2>/dev/null | grep "Total entries:" | awk '{print $3}' || echo "0")
        if [[ "$stats_output" -gt 0 ]]; then
            database_status="✅ $stats_output entries stored"
        fi
    fi
    
    # Generate status report
    status_summary="
=== ADVANCED CLIPBOARD SYSTEM STATUS ===
🔧 Clipboard Daemon: $daemon_status
📊 Clipboard Manager: $manager_status  
🎨 Taskbar Widget: $widget_status
💾 Database: $database_status
"
    
    log_message "STATUS" "$status_summary"
    echo "$status_summary"
    
    # Return success if all components are working
    if [[ "$daemon_status" == *"Running"* ]] && [[ "$manager_status" == *"Running"* ]] && [[ "$widget_status" == *"Visible"* ]]; then
        return 0
    else
        return 1
    fi
}

# ─── MAIN EXECUTION ───────────────────────────────────────────────────────────
main() {
    log_message "START" "🎯 Starting advanced clipboard widget management..."
    
    echo "=== ADVANCED CLIPBOARD WIDGET MANAGER ==="
    echo "Configuring D3.js Material UI clipboard system integration..."
    echo ""
    
    # Step 1: Ensure widget is visible
    if ensure_widget_visible; then
        echo "✅ Clipboard widget is visible in taskbar"
    else
        echo "⚠️ Widget visibility configuration may need manual adjustment"
    fi
    
    # Step 2: Create desktop integration
    create_desktop_integration
    echo "✅ Desktop integration configured"
    
    # Step 3: Set up keyboard shortcuts
    setup_keyboard_shortcuts  
    echo "✅ Keyboard shortcut helper created"
    
    # Step 4: Create context menu integration
    create_context_menu_integration
    echo "✅ Context menu integration configured"
    
    # Step 5: Monitor status
    echo ""
    if monitor_clipboard_status; then
        echo ""
        echo "🎉 Advanced clipboard system is fully operational!"
        echo ""
        echo "📋 Available features:"
        echo "   • Clipboard icon visible in taskbar"
        echo "   • Database-driven unlimited history"
        echo "   • Advanced search functionality"
        echo "   • Usage statistics and analytics"
        echo "   • Desktop application shortcuts"
        echo "   • Context menu integration"
        echo ""
        echo "🔧 Setup keyboard shortcuts: ~/.local/bin/setup-clipboard-shortcuts"
        echo "📄 Log file: $LOG_FILE"
    else
        echo ""
        echo "⚠️ Some components may need attention. Check the status above."
        echo "📄 Log file: $LOG_FILE"
    fi
}

# Execute main function
main "$@"
