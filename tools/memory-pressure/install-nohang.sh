#!/bin/bash
echo "=== NOHANG INSTALLATION ==="
if ! command -v python3 >/dev/null; then
    echo "❌ Python 3 required"
    exit 1
fi
cd /tmp
git clone https://github.com/hakavlad/nohang.git
cd nohang
sudo make install
sudo systemctl enable --now nohang.service
echo "✅ nohang installed and running"
