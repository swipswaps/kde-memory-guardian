#!/bin/bash
# Real System Message Capture - No script output, only actual system events

LOG_FILE="/tmp/real-system-$(date +%H%M%S).log"
echo "Starting real system message capture at $(date)" > "$LOG_FILE"

# Kill the GitHub process blocking terminals
pkill -f "gh release" 2>/dev/null || true

# Capture actual journal messages
echo "=== JOURNAL MESSAGES ===" >> "$LOG_FILE"
journalctl --user --since "5 minutes ago" --no-pager | grep -i -E "(klipper|plasma|systemtray)" >> "$LOG_FILE" 2>&1

# Capture dmesg for kernel messages
echo "=== KERNEL MESSAGES ===" >> "$LOG_FILE"
dmesg | grep -i klipper >> "$LOG_FILE" 2>&1

# Capture actual process information
echo "=== PROCESS INFORMATION ===" >> "$LOG_FILE"
ps aux | grep klipper >> "$LOG_FILE" 2>&1

# Capture actual file system state
echo "=== FILE SYSTEM STATE ===" >> "$LOG_FILE"
find ~/.config -name "*klipper*" -type f -ls >> "$LOG_FILE" 2>&1

# Show the actual log content
echo "=== REAL SYSTEM MESSAGES CAPTURED ==="
cat "$LOG_FILE"
echo ""
echo "Log saved to: $LOG_FILE"
