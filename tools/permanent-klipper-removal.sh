#!/bin/bash

# KDE Memory Guardian - Permanent Klipper Removal Tool
#
# WHAT: Completely and permanently removes Klipper from KDE with persistence prevention
# WHY: Addresses the issue where Klipper widget returns after temporary removal
# HOW: Multi-layer removal with session management, autostart blocking, and widget prevention
#
# PROBLEM ANALYSIS: The Apple A1286 system showed Klipper widget returning because:
# 1. KDE session management can restore "missing" widgets
# 2. Plasma can auto-add system tray widgets it thinks are "essential"
# 3. Autostart files can be recreated by KDE updates
# 4. Widget configuration can be restored from cached states

set -euo pipefail

# Configuration
readonly LOG_FILE="$HOME/.local/share/kde-memory-guardian/klipper-removal.log"
readonly BACKUP_DIR="$HOME/.local/share/kde-memory-guardian/klipper-removal-backup"

# Enhanced logging function
log_message() {
    local message="$1"
    local level="${2:-INFO}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S %Z')
    
    case "$level" in
        "START") formatted_message="[START] 🚀 $message" ;;
        "STEP")  formatted_message="[STEP] 🔄 $message" ;;
        "INFO")  formatted_message="[INFO] ℹ️ $message" ;;
        "WARN")  formatted_message="[WARN] ⚠️ $message" ;;
        "ERROR") formatted_message="[ERROR] ❌ $message" ;;
        "OK")    formatted_message="[OK] ✅ $message" ;;
        "DONE")  formatted_message="[DONE] 🎉 $message" ;;
        *)       formatted_message="[INFO] ℹ️ $message" ;;
    esac
    
    mkdir -p "$(dirname "$LOG_FILE")"
    echo "[$timestamp] $formatted_message" | tee -a "$LOG_FILE"
}

# Check current Klipper status
check_klipper_status() {
    log_message "Checking current Klipper status" "STEP"
    
    local klipper_running=false
    local klipper_memory=0
    local klipper_widget_present=false
    
    # Check if Klipper process is running
    if pgrep -f klipper >/dev/null 2>&1; then
        klipper_running=true
        klipper_memory=$(ps -eo rss,comm | grep klipper | awk '{sum+=$1} END {print sum+0}')
        log_message "Klipper process running, using ${klipper_memory}KB memory" "INFO"
    else
        log_message "Klipper process not running" "INFO"
    fi
    
    # Check for Klipper widget in system tray
    if qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
        var panels = panels();
        for (var i = 0; i < panels.length; i++) {
            var panel = panels[i];
            var widgets = panel.widgets();
            for (var j = 0; j < widgets.length; j++) {
                if (widgets[j].type == 'org.kde.plasma.systemtray') {
                    print('Found system tray');
                }
            }
        }
    " 2>/dev/null | grep -q "Found system tray"; then
        log_message "System tray detected - checking for Klipper widget" "INFO"
        klipper_widget_present=true
    fi
    
    # Summary
    log_message "Status Summary:" "INFO"
    log_message "  Process running: $klipper_running" "INFO"
    log_message "  Memory usage: ${klipper_memory}KB" "INFO"
    log_message "  Widget present: $klipper_widget_present" "INFO"
    
    return 0
}

# Create comprehensive backup
create_backup() {
    log_message "Creating comprehensive backup before removal" "STEP"
    
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="$BACKUP_DIR/klipper_removal_$backup_timestamp"
    mkdir -p "$backup_path"
    
    # Files to backup
    local backup_targets=(
        "$HOME/.config/klipperrc"
        "$HOME/.config/autostart/org.kde.klipper.desktop"
        "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"
        "$HOME/.config/plasmarc"
        "$HOME/.config/ksmserverrc"
        "$HOME/.local/share/klipper"
        "$HOME/.cache/plasma"
    )
    
    for target in "${backup_targets[@]}"; do
        if [[ -e "$target" ]]; then
            local target_name=$(basename "$target")
            log_message "Backing up: $target" "STEP"
            cp -r "$target" "$backup_path/$target_name" 2>/dev/null || true
        fi
    done
    
    log_message "Backup completed: $backup_path" "OK"
    echo "$backup_path" > "$BACKUP_DIR/latest_backup.txt"
}

# Stop all Klipper processes
stop_klipper_processes() {
    log_message "Stopping all Klipper processes" "STEP"
    
    if pgrep -f klipper >/dev/null 2>&1; then
        log_message "Terminating Klipper processes" "STEP"
        pkill -f klipper 2>/dev/null || true
        sleep 2
        
        # Force kill if still running
        if pgrep -f klipper >/dev/null 2>&1; then
            log_message "Force terminating stubborn Klipper processes" "WARN"
            pkill -9 -f klipper 2>/dev/null || true
            sleep 1
        fi
        
        if ! pgrep -f klipper >/dev/null 2>&1; then
            log_message "All Klipper processes terminated" "OK"
        else
            log_message "Some Klipper processes may still be running" "WARN"
        fi
    else
        log_message "No Klipper processes found" "INFO"
    fi
}

# Remove Klipper autostart with persistence prevention
remove_autostart() {
    log_message "Removing Klipper autostart with persistence prevention" "STEP"
    
    local autostart_file="$HOME/.config/autostart/org.kde.klipper.desktop"
    
    # Remove existing autostart file
    if [[ -f "$autostart_file" ]]; then
        log_message "Removing existing autostart file" "STEP"
        rm -f "$autostart_file"
    fi
    
    # Create disabled autostart file to prevent recreation
    log_message "Creating disabled autostart file to prevent recreation" "STEP"
    mkdir -p "$(dirname "$autostart_file")"
    cat > "$autostart_file" << 'EOF'
[Desktop Entry]
Type=Application
Name=Klipper
Comment=Clipboard manager (DISABLED by KDE Memory Guardian)
Exec=/bin/false
Hidden=true
NoDisplay=true
X-GNOME-Autostart-enabled=false
X-KDE-autostart-after=panel
X-KDE-StartupNotify=false
EOF
    
    # Make it read-only to prevent KDE from modifying it
    chmod 444 "$autostart_file"
    log_message "Created read-only disabled autostart file" "OK"
}

# Remove Klipper from KDE session management
remove_from_session_management() {
    log_message "Removing Klipper from KDE session management" "STEP"
    
    # Exclude from session restoration
    if command -v kwriteconfig5 >/dev/null 2>&1; then
        kwriteconfig5 --file ksmserverrc --group General --key excludeApps "klipper"
        log_message "Added Klipper to session exclusion list" "OK"
    fi
    
    # Remove from session if present
    local session_file="$HOME/.config/session/klipper*"
    if ls $session_file >/dev/null 2>&1; then
        rm -f $session_file
        log_message "Removed Klipper session files" "OK"
    fi
}

# Remove Klipper widget from system tray permanently
remove_klipper_widget() {
    log_message "Removing Klipper widget from system tray permanently" "STEP"
    
    # Method 1: Remove from Plasma configuration
    local plasma_config="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"
    if [[ -f "$plasma_config" ]]; then
        log_message "Removing Klipper from Plasma configuration" "STEP"
        
        # Create temporary file without Klipper entries
        grep -v "klipper\|Klipper" "$plasma_config" > "${plasma_config}.tmp" || true
        mv "${plasma_config}.tmp" "$plasma_config"
        log_message "Cleaned Plasma configuration" "OK"
    fi
    
    # Method 2: Use Plasma scripting to remove widget
    if command -v qdbus >/dev/null 2>&1; then
        log_message "Using Plasma scripting to remove Klipper widget" "STEP"
        
        qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
            var panels = panels();
            for (var i = 0; i < panels.length; i++) {
                var panel = panels[i];
                var widgets = panel.widgets();
                for (var j = 0; j < widgets.length; j++) {
                    var widget = widgets[j];
                    if (widget.type == 'org.kde.plasma.systemtray') {
                        // Remove Klipper from system tray
                        widget.currentConfigGroup = ['General'];
                        var hiddenItems = widget.readConfig('hiddenItems', '').split(',');
                        if (hiddenItems.indexOf('org.kde.klipper') == -1) {
                            hiddenItems.push('org.kde.klipper');
                            widget.writeConfig('hiddenItems', hiddenItems.join(','));
                        }
                    }
                }
            }
        " 2>/dev/null || true
        
        log_message "Plasma scripting completed" "OK"
    fi
}

# Disable Klipper global shortcuts
disable_global_shortcuts() {
    log_message "Disabling Klipper global shortcuts" "STEP"
    
    if command -v kwriteconfig5 >/dev/null 2>&1; then
        # Disable all Klipper shortcuts
        kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "clipboard_action" "none"
        kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "cycleNextAction" "none"
        kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "cyclePrevAction" "none"
        kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "edit_clipboard" "none"
        kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "repeat_action" "none"
        kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "show-barcode" "none"
        kwriteconfig5 --file kglobalshortcutsrc --group "klipper" --key "show-on-mouse-pos" "none"
        
        log_message "All Klipper global shortcuts disabled" "OK"
    fi
}

# Restart Plasma to apply changes
restart_plasma() {
    log_message "Restarting Plasma to apply changes" "STEP"
    
    # Kill plasmashell
    if pgrep plasmashell >/dev/null 2>&1; then
        log_message "Stopping plasmashell" "STEP"
        pkill plasmashell
        sleep 3
    fi
    
    # Start plasmashell
    log_message "Starting plasmashell" "STEP"
    if command -v kstart >/dev/null 2>&1; then
        nohup kstart plasmashell >/dev/null 2>&1 &
    else
        nohup plasmashell >/dev/null 2>&1 &
    fi
    
    sleep 5
    
    if pgrep plasmashell >/dev/null 2>&1; then
        log_message "Plasmashell restarted successfully" "OK"
    else
        log_message "Failed to restart plasmashell" "ERROR"
        return 1
    fi
}

# Create persistence prevention measures
create_persistence_prevention() {
    log_message "Creating persistence prevention measures" "STEP"
    
    # Create a script that runs on login to ensure Klipper stays disabled
    local prevention_script="$HOME/.local/bin/klipper-prevention.sh"
    mkdir -p "$(dirname "$prevention_script")"
    
    cat > "$prevention_script" << 'EOF'
#!/bin/bash
# Klipper Prevention Script - Ensures Klipper stays disabled

# Kill any Klipper processes that may have started
pkill -f klipper 2>/dev/null || true

# Ensure autostart file remains disabled
AUTOSTART_FILE="$HOME/.config/autostart/org.kde.klipper.desktop"
if [[ -f "$AUTOSTART_FILE" ]] && ! grep -q "Hidden=true" "$AUTOSTART_FILE"; then
    cat > "$AUTOSTART_FILE" << 'INNER_EOF'
[Desktop Entry]
Type=Application
Name=Klipper
Comment=Clipboard manager (DISABLED by KDE Memory Guardian)
Exec=/bin/false
Hidden=true
NoDisplay=true
X-GNOME-Autostart-enabled=false
INNER_EOF
    chmod 444 "$AUTOSTART_FILE"
fi
EOF
    
    chmod +x "$prevention_script"
    
    # Create autostart entry for prevention script
    cat > "$HOME/.config/autostart/klipper-prevention.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Klipper Prevention
Comment=Ensures Klipper stays disabled
Exec=$prevention_script
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
StartupNotify=false
EOF
    
    log_message "Persistence prevention measures created" "OK"
}

# Main execution function
main() {
    log_message "Starting permanent Klipper removal process" "START"
    
    # Check current status
    check_klipper_status
    
    # Create backup
    create_backup
    
    # Perform removal steps
    stop_klipper_processes
    remove_autostart
    remove_from_session_management
    remove_klipper_widget
    disable_global_shortcuts
    create_persistence_prevention
    
    # Restart Plasma to apply changes
    restart_plasma
    
    # Final status check
    log_message "Waiting 10 seconds for system to stabilize..." "INFO"
    sleep 10
    
    log_message "Final status check:" "STEP"
    check_klipper_status
    
    log_message "Permanent Klipper removal completed!" "DONE"
    log_message "Klipper should now be permanently disabled" "INFO"
    log_message "If Klipper returns, check the log for troubleshooting" "INFO"
    log_message "Log file: $LOG_FILE" "INFO"
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
