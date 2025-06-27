#!/bin/bash
################################################################################
# KDE Memory Guardian - Enhanced Database Manager Launcher
# WHO: Users who want easy access to superior database tools
# WHAT: Launcher script for enhanced database management system
# WHY: One-click access to professional database tools with superior UX
# HOW: Starts Flask server with Material Design UI and integrated tools
################################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SCRIPT_DIR/kde-memory-guardian-server.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🗃️ KDE Memory Guardian - Enhanced Database Manager${NC}"
echo "=================================================================="

# Check if server script exists
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo -e "${RED}❌ Server script not found at: $SERVER_SCRIPT${NC}"
    exit 1
fi

# Check dependencies
echo -e "${BLUE}🔍 Checking dependencies...${NC}"

# Check Python and Flask
if ! python3 -c "import flask, flask_cors" 2>/dev/null; then
    echo -e "${RED}❌ Flask or Flask-CORS not installed${NC}"
    echo "Install with: pip install flask flask-cors --user"
    exit 1
fi

# Check clipboard database
CLIPBOARD_DB="$HOME/.clipboard_manager.db"
if [ -f "$CLIPBOARD_DB" ]; then
    SIZE=$(du -h "$CLIPBOARD_DB" | cut -f1)
    ENTRIES=$(sqlite3 "$CLIPBOARD_DB" "SELECT COUNT(*) FROM clipboard_entries;" 2>/dev/null || echo "0")
    echo -e "${GREEN}✅ Clipboard database found: $SIZE, $ENTRIES entries${NC}"
else
    echo -e "${YELLOW}⚠️ Clipboard database not found - will be created when first used${NC}"
fi

# Check Adminer
ADMINER_PATH="$SCRIPT_DIR/adminer.php"
if [ -f "$ADMINER_PATH" ]; then
    SIZE=$(du -h "$ADMINER_PATH" | cut -f1)
    echo -e "${GREEN}✅ Adminer ready: $SIZE${NC}"
else
    echo -e "${YELLOW}⚠️ Adminer not found - downloading...${NC}"
    if command -v wget >/dev/null 2>&1; then
        wget -O "$ADMINER_PATH" https://www.adminer.org/latest.php
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Adminer downloaded successfully${NC}"
        else
            echo -e "${YELLOW}⚠️ Failed to download Adminer - some features may not work${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ wget not available - please download Adminer manually${NC}"
    fi
fi

# Check available tools
echo -e "${BLUE}🔧 Checking available tools...${NC}"
TOOLS_AVAILABLE=()

if command -v sqlitebrowser >/dev/null 2>&1; then
    TOOLS_AVAILABLE+=("SQLite Browser")
fi

if command -v clipboard-plot >/dev/null 2>&1; then
    TOOLS_AVAILABLE+=("Clipboard Plot")
fi

if command -v clipboard-sql >/dev/null 2>&1; then
    TOOLS_AVAILABLE+=("Clipboard SQL")
fi

if [ ${#TOOLS_AVAILABLE[@]} -gt 0 ]; then
    echo -e "${GREEN}✅ Available tools: ${TOOLS_AVAILABLE[*]}${NC}"
else
    echo -e "${YELLOW}⚠️ No additional tools found - basic functionality available${NC}"
fi

echo "=================================================================="
echo -e "${GREEN}🚀 Starting KDE Memory Guardian Enhanced Database Manager...${NC}"
echo ""
echo -e "${BLUE}📊 Access Points:${NC}"
echo "• Main Interface: http://localhost:5000"
echo "• Adminer: http://localhost:5000/adminer"
echo "• Tools: http://localhost:5000/tools"
echo "• API Docs: http://localhost:5000/api/docs"
echo ""
echo -e "${BLUE}🌟 Enhanced Features:${NC}"
echo "• Material Design UI with superior UX"
echo "• Real-time database statistics"
echo "• Multiple database tool integration"
echo "• Advanced SQL query interface"
echo "• Data visualization capabilities"
echo "• Professional database management"
echo ""
echo -e "${YELLOW}💡 Press Ctrl+C to stop the server${NC}"
echo "=================================================================="

# Start the server
cd "$SCRIPT_DIR"
python3 "$SERVER_SCRIPT"
