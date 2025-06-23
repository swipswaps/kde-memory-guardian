#!/bin/bash
echo "=== UNIFIED MEMORY PROTECTION MANAGER ==="
case "${1:-status}" in
    "install")
        echo "Installing all memory protection tiers..."
        ./tools/memory-pressure/install-earlyoom.sh
        ./tools/memory-pressure/install-nohang.sh
        ./tools/memory-pressure/configure-systemd-oomd.sh
        ;;
    "status")
        echo "Memory Protection Status:"
        systemctl is-active earlyoom.service && echo "✅ Tier 1 (earlyoom): ACTIVE" || echo "❌ Tier 1 (earlyoom): INACTIVE"
        systemctl is-active nohang.service && echo "✅ Tier 2 (nohang): ACTIVE" || echo "❌ Tier 2 (nohang): INACTIVE"
        systemctl is-active systemd-oomd.service && echo "✅ Tier 3 (systemd-oomd): ACTIVE" || echo "❌ Tier 3 (systemd-oomd): INACTIVE"
        ;;
    *)
        echo "Usage: $0 [install|status]"
        ;;
esac
