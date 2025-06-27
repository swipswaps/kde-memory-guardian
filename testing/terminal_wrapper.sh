#!/bin/bash
# Terminal Wrapper Script for Sequential Sudo Commands
# Handles multiple sudo commands in sequence with password caching

COMMAND="$1"
DESCRIPTION="$2"
OUTPUT_FILE="$3"

echo "🔍 Sequential Sudo Command Execution"
echo "======================================"
echo "This terminal will execute multiple sudo commands in sequence."
echo "You only need to enter your password once."
echo ""

if [[ "$COMMAND" == *"sequential"* ]]; then
    # This is a sequential script execution
    echo "🚀 Executing sequential sudo commands..."
    echo "Please enter your sudo password when prompted:"
    echo ""

    # Execute the script directly
    bash "$COMMAND"
    exit_code=$?
else
    # Legacy single command execution
    echo "🔍 Collecting $DESCRIPTION for crash analysis..."
    echo "Please enter your sudo password when prompted:"
    echo ""

    # Run the command and save output
    eval "$COMMAND" > "$OUTPUT_FILE" 2>&1
    exit_code=$?
fi

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ $DESCRIPTION collected successfully!"
    echo "📄 Output saved to $OUTPUT_FILE"
    echo "📊 Data ready for crash analysis integration"
    
    # Show first few lines of output for verification
    echo ""
    echo "📋 Sample output (first 5 lines):"
    head -5 "$OUTPUT_FILE" 2>/dev/null || echo "No output to display"
else
    echo "❌ Failed to collect $DESCRIPTION"
    echo "Exit code: $exit_code"
    
    # Show error output
    if [ -f "$OUTPUT_FILE" ]; then
        echo ""
        echo "📋 Error output:"
        head -10 "$OUTPUT_FILE" 2>/dev/null
    fi
fi

echo ""
echo "🔄 Returning focus to crash analyzer..."
echo "Press Enter to close this window..."

# Set up automatic closing
read -t 30 -p "Closing automatically in 30 seconds... "

# Multiple methods to close terminal
close_terminal() {
    # Method 1: Try Konsole-specific closing
    if [ -n "$KONSOLE_DBUS_SERVICE" ] && [ -n "$KONSOLE_DBUS_SESSION" ]; then
        qdbus "$KONSOLE_DBUS_SERVICE" "$KONSOLE_DBUS_SESSION" close 2>/dev/null
        return $?
    fi
    
    # Method 2: Try xdotool if WINDOWID is available
    if [ -n "$WINDOWID" ]; then
        xdotool windowclose "$WINDOWID" 2>/dev/null
        return $?
    fi
    
    # Method 3: Try wmctrl to close current window
    if command -v wmctrl >/dev/null 2>&1; then
        wmctrl -c "$(wmctrl -l | grep $$ | head -1 | cut -d' ' -f5-)" 2>/dev/null
        return $?
    fi
    
    # Method 4: Try to kill parent terminal process
    if [ -n "$PPID" ]; then
        kill -TERM "$PPID" 2>/dev/null
        return $?
    fi
    
    return 1
}

# Try to close terminal
if close_terminal; then
    echo "✅ Terminal closing..."
else
    echo "⚠️ Please close this terminal window manually"
    echo "Focus will return to the crash analyzer"
fi

# Return focus to Firefox/browser
if command -v xdotool >/dev/null 2>&1; then
    # Find Firefox window and focus it
    firefox_window=$(xdotool search --name "Mozilla Firefox" | head -1)
    if [ -n "$firefox_window" ]; then
        xdotool windowactivate "$firefox_window" 2>/dev/null
    fi
fi

exit 0
