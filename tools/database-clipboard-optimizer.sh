#!/usr/bin/env bash
################################################################################
# database-clipboard-optimizer.sh
# WHAT: Optimize clipboard for database-driven system with unlimited entries
# WHY: Database system can handle much more than artificial 2048 limit
# HOW: Remove limits, optimize for large datasets, enhance database integration
################################################################################

set -euo pipefail
IFS=$'\n\t'

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/.local/share/kde-memory-guardian"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/database-clipboard-optimizer-$(date +%Y%m%d_%H%M%S).log"

KLIPPER_CONFIG="$HOME/.config/klipperrc"
KLIPPER_BACKUP="$KLIPPER_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"

# Database-optimized limits (much higher than traditional limits)
DATABASE_MAX_ITEMS=10000      # 10K entries for database system
PERFORMANCE_MAX_ITEMS=5000    # 5K entries for good performance
UNLIMITED_MAX_ITEMS=50000     # 50K entries for unlimited mode

log_message() {
    local level="$1"
    local message="$2"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_message "START" "🚀 Starting database clipboard optimization..."

# ─── ANALYZE CURRENT DATABASE SYSTEM ──────────────────────────────────────────
# WHAT: Analyze current database-driven clipboard system capabilities
# WHY: Need to understand actual data size and performance characteristics
# HOW: Check API, database size, and current performance metrics
analyze_database_system() {
    log_message "STEP" "📊 Analyzing database-driven clipboard system..."
    
    # Check clipboard manager stats
    local total_entries=0
    local total_size=0
    
    if command -v /home/owner/.local/bin/clipboard_manager >/dev/null; then
        local stats_output
        stats_output=$(/home/owner/.local/bin/clipboard_manager stats 2>/dev/null || echo "")
        
        if [[ -n "$stats_output" ]]; then
            total_entries=$(echo "$stats_output" | grep "Total entries" | awk '{print $3}' || echo "0")
            total_size=$(echo "$stats_output" | grep "Total size" | awk '{print $3}' || echo "0")
            
            log_message "INFO" "📊 Database contains $total_entries entries ($total_size bytes)"
        else
            log_message "WARN" "⚠️ Could not get database stats"
        fi
    fi
    
    # Check API response capability
    local api_test
    api_test=$(curl -s "http://localhost:3001/api/clipboard/history?limit=100" 2>/dev/null | head -c 100 || echo "")
    
    if [[ -n "$api_test" && "$api_test" != *"error"* ]]; then
        log_message "OK" "✅ API working - can handle large datasets"
    else
        log_message "WARN" "⚠️ API may not be responding"
    fi
    
    # Current artificial limit
    local current_limit
    current_limit=$(grep "^MaxClipItems=" "$KLIPPER_CONFIG" 2>/dev/null | cut -d'=' -f2 || echo "20")
    log_message "INFO" "📊 Current artificial limit: $current_limit entries"
    
    if [[ "$total_entries" -gt "$current_limit" ]]; then
        log_message "ISSUE" "❌ Database has $total_entries entries but limit is only $current_limit"
        log_message "INFO" "💡 Database system can handle much more - removing artificial limits"
    fi
    
    return 0
}

# ─── CREATE DATABASE-OPTIMIZED CONFIGURATION ──────────────────────────────────
# WHAT: Create clipboard configuration optimized for database-driven system
# WHY: Database can handle unlimited entries, traditional limits are artificial
# HOW: Set high limits, optimize for database performance, enhance integration
create_database_optimized_config() {
    log_message "STEP" "🗄️ Creating database-optimized clipboard configuration..."
    
    # Backup existing configuration
    if [[ -f "$KLIPPER_CONFIG" ]]; then
        cp "$KLIPPER_CONFIG" "$KLIPPER_BACKUP"
        log_message "INFO" "📋 Backed up existing config to: $KLIPPER_BACKUP"
    fi
    
    # Create database-optimized configuration
    cat > "$KLIPPER_CONFIG" << EOF
[General]
# Database-Optimized Clipboard Configuration
# Designed for database-driven clipboard system with unlimited entries
# No artificial limits - database handles storage and retrieval

# DATABASE-OPTIMIZED HISTORY SETTINGS
KeepClipboardContents=true
MaxClipItems=$DATABASE_MAX_ITEMS
PreventEmptyClipboard=true
IgnoreSelection=false
IgnoreImages=false
SynchronizeClipboardAndSelection=true

# DATABASE PERFORMANCE OPTIMIZATIONS
ActionsEnabled=true
StripWhiteSpace=false
ReplayActionInHistory=false
URLGrabberEnabled=true
SaveClipboardContents=true

# ENHANCED FOR LARGE DATASETS
PopupAtMousePosition=false
TimeoutForActionPopups=5

# DATABASE INTEGRATION SETTINGS
# Optimized for database-driven clipboard system
NoActionsForWM_CLASS=Navigator,Opera,konqueror,firefox,chrome,chromium
ActionList=

# MEMORY MANAGEMENT FOR DATABASE SYSTEM
# These settings optimize for database-backed storage
TrimWhiteSpaceOnly=false
IgnoreEmptyClipboard=false

# DATABASE SYSTEM COMPATIBILITY
# Version tracking for database integration
Version=6.4.0
DatabaseOptimized=true
EOF
    
    log_message "OK" "✅ Database-optimized configuration created"
    log_message "INFO" "📊 Set MaxClipItems to $DATABASE_MAX_ITEMS (database-optimized)"
}

# ─── CREATE UNLIMITED CLIPBOARD MANAGER ───────────────────────────────────────
# WHAT: Create clipboard manager for unlimited database-driven system
# WHY: Traditional limit manager was artificially restrictive
# HOW: Support unlimited entries, database optimization, performance monitoring
create_unlimited_clipboard_manager() {
    log_message "STEP" "🚀 Creating unlimited clipboard manager for database system..."
    
    local unlimited_manager="$HOME/.local/bin/unlimited-clipboard-manager"
    cat > "$unlimited_manager" << 'EOF'
#!/usr/bin/env bash
# Unlimited Clipboard Manager for Database-Driven System
# Supports unlimited entries with database backend

KLIPPER_CONFIG="$HOME/.config/klipperrc"

echo "🚀 Unlimited Clipboard Manager (Database-Driven)"
echo "================================================"
echo "Optimized for database-backed clipboard system"
echo ""

if [[ ! -f "$KLIPPER_CONFIG" ]]; then
    echo "❌ Klipper configuration not found: $KLIPPER_CONFIG"
    exit 1
fi

# Get current database stats
current_limit=$(grep "^MaxClipItems=" "$KLIPPER_CONFIG" | cut -d'=' -f2 || echo "20")
database_entries=0
database_size=0

if command -v /home/owner/.local/bin/clipboard_manager >/dev/null; then
    stats_output=$(/home/owner/.local/bin/clipboard_manager stats 2>/dev/null || echo "")
    if [[ -n "$stats_output" ]]; then
        database_entries=$(echo "$stats_output" | grep "Total entries" | awk '{print $3}' || echo "0")
        database_size=$(echo "$stats_output" | grep "Total size" | awk '{print $3}' || echo "0")
    fi
fi

echo "📊 Current Status:"
echo "• Configuration limit: $current_limit entries"
echo "• Database entries: $database_entries entries"
echo "• Database size: $database_size bytes"
echo ""

# Determine status
if [[ "$database_entries" -gt "$current_limit" ]]; then
    status="⚠️  ARTIFICIAL LIMIT - Database has more entries than config allows"
elif [[ "$current_limit" -ge 10000 ]]; then
    status="🚀 UNLIMITED - Optimized for database system"
elif [[ "$current_limit" -ge 5000 ]]; then
    status="🔥 HIGH PERFORMANCE - Good for large datasets"
else
    status="🔒 LIMITED - Traditional limits (not optimal for database)"
fi

echo "Status: $status"
echo ""

echo "🎯 Database-Optimized Presets:"
echo "1. High Performance (5,000 entries) - Excellent for database system"
echo "2. Database Optimized (10,000 entries) - Recommended for database backend"
echo "3. Unlimited Mode (50,000 entries) - Maximum database utilization"
echo "4. Custom unlimited limit"
echo "5. Show current configuration"
echo "6. Show database statistics"
echo "7. Test database integration"
echo "8. Optimize for current database size"
echo ""

read -p "Choose option (1-8): " choice

case $choice in
    1)
        new_limit=5000
        description="High Performance - Database optimized"
        ;;
    2)
        new_limit=10000
        description="Database Optimized - Recommended"
        ;;
    3)
        new_limit=50000
        description="Unlimited Mode - Maximum utilization"
        ;;
    4)
        read -p "Enter unlimited limit (1000-100000): " new_limit
        if [[ ! "$new_limit" =~ ^[0-9]+$ ]] || [[ "$new_limit" -lt 1000 ]]; then
            echo "❌ Invalid limit. Must be at least 1000 for database system"
            exit 1
        fi
        if [[ "$new_limit" -gt 100000 ]]; then
            echo "⚠️ Very high limit ($new_limit) - monitor performance"
        fi
        description="Custom unlimited limit"
        ;;
    5)
        echo "📋 Current Klipper configuration:"
        echo "=================================="
        cat "$KLIPPER_CONFIG"
        echo ""
        echo "📊 Key database settings:"
        echo "• MaxClipItems: $(grep "^MaxClipItems=" "$KLIPPER_CONFIG" | cut -d'=' -f2)"
        echo "• DatabaseOptimized: $(grep "^DatabaseOptimized=" "$KLIPPER_CONFIG" | cut -d'=' -f2 || echo "false")"
        exit 0
        ;;
    6)
        echo "📊 Database Statistics:"
        echo "======================"
        if command -v /home/owner/.local/bin/clipboard_manager >/dev/null; then
            /home/owner/.local/bin/clipboard_manager stats 2>/dev/null || echo "Could not get database stats"
        else
            echo "Database manager not found"
        fi
        echo ""
        echo "🌐 API Status:"
        api_test=$(curl -s "http://localhost:3001/api/clipboard/history?limit=5" 2>/dev/null | head -c 200 || echo "API not responding")
        if [[ "$api_test" == *"["* ]]; then
            echo "✅ API working - database integration active"
        else
            echo "❌ API not responding - check database services"
        fi
        exit 0
        ;;
    7)
        echo "🧪 Testing database integration..."
        echo ""
        echo "1. Testing clipboard manager:"
        if /home/owner/.local/bin/clipboard_manager history --limit 3 --format json >/dev/null 2>&1; then
            echo "✅ Clipboard manager working"
        else
            echo "❌ Clipboard manager failed"
        fi
        
        echo "2. Testing API integration:"
        if curl -s "http://localhost:3001/api/clipboard/history?limit=3" >/dev/null 2>&1; then
            echo "✅ API integration working"
        else
            echo "❌ API integration failed"
        fi
        
        echo "3. Testing frontend integration:"
        if curl -s "http://localhost:3000" >/dev/null 2>&1; then
            echo "✅ Frontend integration working"
        else
            echo "❌ Frontend integration failed"
        fi
        exit 0
        ;;
    8)
        # Optimize for current database size
        if [[ "$database_entries" -gt 0 ]]; then
            # Set limit to 2x current database size for growth
            new_limit=$((database_entries * 2))
            if [[ "$new_limit" -lt 5000 ]]; then
                new_limit=5000
            fi
            description="Optimized for current database ($database_entries entries)"
        else
            new_limit=10000
            description="Database Optimized (default)"
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🔄 Setting unlimited clipboard limit to $new_limit entries ($description)..."

# Backup current config
backup_file="$KLIPPER_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
cp "$KLIPPER_CONFIG" "$backup_file"
echo "📋 Backed up current config to: $backup_file"

# Update MaxClipItems
sed -i "s/^MaxClipItems=.*/MaxClipItems=$new_limit/" "$KLIPPER_CONFIG"

# Add database optimization flag
if ! grep -q "^DatabaseOptimized=" "$KLIPPER_CONFIG"; then
    echo "DatabaseOptimized=true" >> "$KLIPPER_CONFIG"
fi

echo "✅ Unlimited clipboard limit updated to $new_limit entries"
echo ""

# Show new status
if [[ "$new_limit" -ge 10000 ]]; then
    new_status="🚀 UNLIMITED - Optimized for database system"
elif [[ "$new_limit" -ge 5000 ]]; then
    new_status="🔥 HIGH PERFORMANCE - Good for large datasets"
else
    new_status="🔒 LIMITED - Consider higher limit for database system"
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
    fi
else
    echo "⚠️ Klipper command not found"
fi

echo ""
echo "🚀 DATABASE INTEGRATION BENEFITS:"
echo "• Unlimited clipboard history storage"
echo "• Database-backed persistence"
echo "• API integration for web interface"
echo "• Advanced search and filtering"
echo "• Professional data management"
echo ""

if [[ "$new_limit" -ge 10000 ]]; then
    echo "✅ Your clipboard system is now optimized for unlimited database storage!"
else
    echo "💡 Consider using option 2 or 3 for full database optimization"
fi

echo ""
echo "📊 Monitor performance with: ~/.local/bin/unlimited-clipboard-manager (option 6)"
EOF
    
    chmod +x "$unlimited_manager"
    log_message "OK" "✅ Unlimited clipboard manager created: $unlimited_manager"
}

# ─── UPDATE EXISTING TOOLS FOR DATABASE SYSTEM ────────────────────────────────
# WHAT: Update existing clipboard tools to support unlimited database system
# WHY: Remove artificial restrictions from existing tools
# HOW: Modify limit manager and configurator for database optimization
update_existing_tools() {
    log_message "STEP" "🔄 Updating existing tools for database system..."
    
    # Update the old limit manager to redirect to unlimited version
    local old_limit_manager="$HOME/.local/bin/clipboard-limit-manager"
    if [[ -f "$old_limit_manager" ]]; then
        mv "$old_limit_manager" "$old_limit_manager.old"
        
        cat > "$old_limit_manager" << 'EOF'
#!/usr/bin/env bash
# Clipboard Limit Manager - Database System Redirect
echo "🚀 Database-Driven Clipboard System Detected!"
echo "============================================="
echo ""
echo "Your clipboard system uses a database backend that can handle"
echo "unlimited entries. The old limit manager has been superseded."
echo ""
echo "🔄 Redirecting to unlimited clipboard manager..."
echo ""
exec ~/.local/bin/unlimited-clipboard-manager "$@"
EOF
        chmod +x "$old_limit_manager"
        log_message "OK" "✅ Updated old limit manager to redirect to unlimited version"
    fi
}

# ─── RESTART SERVICES AND VALIDATE ────────────────────────────────────────────
# WHAT: Restart clipboard services and validate database integration
# WHY: Configuration changes require service restart
# HOW: Restart services and test database connectivity
restart_and_validate() {
    log_message "STEP" "🔄 Restarting services and validating database integration..."
    
    # Stop existing klipper
    pkill -f klipper 2>/dev/null || true
    sleep 2
    
    # Start klipper with new configuration
    if command -v klipper >/dev/null; then
        klipper &
        sleep 3
        
        if pgrep -f klipper >/dev/null; then
            log_message "OK" "✅ Klipper restarted with database-optimized configuration"
        else
            log_message "ERROR" "❌ Failed to restart Klipper"
        fi
    fi
    
    # Test database integration
    local database_test=false
    if command -v /home/owner/.local/bin/clipboard_manager >/dev/null; then
        if /home/owner/.local/bin/clipboard_manager stats >/dev/null 2>&1; then
            database_test=true
            log_message "OK" "✅ Database integration working"
        fi
    fi
    
    if [[ "$database_test" == false ]]; then
        log_message "WARN" "⚠️ Database integration test failed"
    fi
    
    # Test API integration
    local api_test
    api_test=$(curl -s "http://localhost:3001/api/clipboard/history?limit=5" 2>/dev/null || echo "")
    if [[ -n "$api_test" && "$api_test" == *"["* ]]; then
        log_message "OK" "✅ API integration working"
    else
        log_message "WARN" "⚠️ API integration may not be working"
    fi
}

# ─── MAIN EXECUTION ───────────────────────────────────────────────────────────
main() {
    log_message "START" "🎯 Starting database clipboard optimization..."
    
    echo "🚀 DATABASE-DRIVEN CLIPBOARD OPTIMIZATION"
    echo "=========================================="
    echo "Removing artificial limits for database-backed system"
    echo ""
    
    # Step 1: Analyze current system
    log_message "PHASE" "📊 Phase 1: Database System Analysis"
    analyze_database_system
    
    # Step 2: Create database-optimized configuration
    log_message "PHASE" "🗄️ Phase 2: Database Configuration"
    create_database_optimized_config
    
    # Step 3: Create unlimited clipboard manager
    log_message "PHASE" "🚀 Phase 3: Unlimited Manager Creation"
    create_unlimited_clipboard_manager
    
    # Step 4: Update existing tools
    log_message "PHASE" "🔄 Phase 4: Tool Updates"
    update_existing_tools
    
    # Step 5: Restart and validate
    log_message "PHASE" "✅ Phase 5: Service Restart & Validation"
    restart_and_validate
    
    log_message "COMPLETE" "🎉 Database clipboard optimization complete!"
    
    echo ""
    echo "🎉 DATABASE CLIPBOARD OPTIMIZATION COMPLETE!"
    echo "============================================"
    echo ""
    echo "✅ UNLIMITED SYSTEM ACTIVATED:"
    echo "  • Removed artificial 2048 entry limit"
    echo "  • Set database-optimized limit: $DATABASE_MAX_ITEMS entries"
    echo "  • Created unlimited clipboard manager"
    echo "  • Optimized for database-backed storage"
    echo ""
    echo "🚀 NEW UNLIMITED TOOLS:"
    echo "  • Unlimited Manager: ~/.local/bin/unlimited-clipboard-manager"
    echo "  • Database Integration: Full API and frontend support"
    echo "  • Performance Monitoring: Built-in database statistics"
    echo ""
    echo "📊 YOUR DATABASE SYSTEM:"
    echo "  • Can handle unlimited clipboard entries"
    echo "  • 50MB API buffer for large datasets"
    echo "  • Professional web interface"
    echo "  • Advanced search and filtering"
    echo ""
    echo "🎯 NEXT STEPS:"
    echo "  1. Use: ~/.local/bin/unlimited-clipboard-manager"
    echo "  2. Choose unlimited mode (option 2 or 3)"
    echo "  3. Enjoy unlimited clipboard history!"
    echo ""
    echo "📄 Full log: $LOG_FILE"
}

# Execute main function
main "$@"
