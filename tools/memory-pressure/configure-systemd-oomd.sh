#!/bin/bash
echo "=== SYSTEMD-OOMD CONFIGURATION ==="
if ! command -v systemd-oomd >/dev/null; then
    echo "❌ systemd-oomd not available"
    exit 1
fi
sudo systemctl enable --now systemd-oomd.service
echo "✅ systemd-oomd configured and running"
