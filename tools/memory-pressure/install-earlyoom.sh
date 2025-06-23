#!/bin/bash
echo "=== EARLYOOM INSTALLATION ==="
if command -v dnf >/dev/null; then
    sudo dnf install -y earlyoom
elif command -v apt >/dev/null; then
    sudo apt update && sudo apt install -y earlyoom
elif command -v pacman >/dev/null; then
    sudo pacman -S --noconfirm earlyoom
else
    echo "Please install earlyoom manually"
    exit 1
fi
sudo systemctl enable --now earlyoom.service
echo "✅ earlyoom installed and running"
