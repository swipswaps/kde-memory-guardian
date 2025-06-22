# KDE Memory Guardian - Troubleshooting Guide

This guide helps you diagnose and resolve common issues with KDE Memory Guardian.

## 🔍 Quick Diagnostics

### Check Service Status
```bash
# Check if service is running
systemctl --user status kde-memory-manager.service

# View recent logs
journalctl --user -u kde-memory-manager.service --since "1 hour ago"

# Check memory usage
memcheck
```

### Verify Installation
```bash
# Check if script exists and is executable
ls -la ~/.local/bin/kde-memory-manager.sh

# Check if service file exists
ls -la ~/.config/systemd/user/kde-memory-manager.service

# Check if log file exists
ls -la ~/.local/share/kde-memory-manager.log
```

## 🚨 Common Issues

### Service Won't Start

#### Symptom
```
● kde-memory-manager.service - KDE Memory Guardian
   Loaded: loaded
   Active: failed (Result: exit-code)
```

#### Possible Causes & Solutions

**1. Script Not Executable**
```bash
# Check permissions
ls -la ~/.local/bin/kde-memory-manager.sh

# Fix permissions
chmod +x ~/.local/bin/kde-memory-manager.sh
```

**2. Missing Dependencies**
```bash
# Check for required commands
which kstart || echo "kstart missing - install KDE development tools"
which killall || echo "killall missing - install psmisc package"
which ps || echo "ps missing - install procps package"

# Install missing dependencies (Fedora)
sudo dnf install kdelibs-devel psmisc procps-ng

# Install missing dependencies (Ubuntu)
sudo apt install kde-runtime psmisc procps
```

**3. Environment Variables Missing**
```bash
# Check environment in service
systemctl --user show-environment

# Add missing variables to service
systemctl --user set-environment DISPLAY=:0
```

**4. Script Syntax Errors**
```bash
# Check script syntax
bash -n ~/.local/bin/kde-memory-manager.sh

# View detailed error logs
journalctl --user -u kde-memory-manager.service -f
```

### Service Starts But Doesn't Work

#### Symptom
Service is active but memory issues persist or no logs are generated.

#### Diagnostics
```bash
# Check if script is actually running
ps aux | grep kde-memory-manager

# Check log file for activity
tail -f ~/.local/share/kde-memory-manager.log

# Test script manually
~/.local/bin/kde-memory-manager.sh &
```

#### Solutions

**1. Incorrect Thresholds**
```bash
# Check current thresholds
grep THRESHOLD ~/.local/bin/kde-memory-manager.sh

# Adjust thresholds for your system
# Edit ~/.local/bin/kde-memory-manager.sh
# Lower thresholds for more aggressive management:
MEMORY_THRESHOLD=60
PLASMA_MEMORY_THRESHOLD=1000000
```

**2. Process Detection Issues**
```bash
# Check if processes are detected correctly
ps aux | grep plasmashell
ps aux | grep kglobalacceld

# Test memory detection function
bash -c 'source ~/.local/bin/kde-memory-manager.sh; get_process_memory plasmashell'
```

### Plasma Restart Fails

#### Symptom
Service logs show restart attempts but Plasma doesn't actually restart.

#### Diagnostics
```bash
# Test manual restart
killall plasmashell && kstart plasmashell

# Check if kstart works
kstart --help

# Check display environment
echo $DISPLAY
```

#### Solutions

**1. Wrong kstart Command**
```bash
# Try alternative restart methods
killall plasmashell && plasmashell &
killall plasmashell && nohup plasmashell >/dev/null 2>&1 &
```

**2. Display Issues**
```bash
# Set correct display in service
systemctl --user edit kde-memory-manager.service

# Add:
[Service]
Environment=DISPLAY=:0
Environment=WAYLAND_DISPLAY=wayland-0
```

### High Memory Usage Persists

#### Symptom
Service is working but memory usage remains high.

#### Analysis
```bash
# Identify memory-hungry processes
ps aux --sort=-%mem | head -20

# Check swap usage
free -h

# Monitor memory over time
watch -n 5 'free -h && echo "---" && ps aux --sort=-%mem | head -5'
```

#### Solutions

**1. Adjust Thresholds**
```bash
# Make thresholds more aggressive
# Edit ~/.local/bin/kde-memory-manager.sh
MEMORY_THRESHOLD=70          # Lower from 80
PLASMA_MEMORY_THRESHOLD=800000  # Lower from 1500000
```

**2. Additional System Optimizations**
```bash
# Check current swappiness
cat /proc/sys/vm/swappiness

# Apply more aggressive memory settings
sudo sysctl vm.swappiness=5
sudo sysctl vm.vfs_cache_pressure=200
```

**3. Identify Other Memory Leaks**
```bash
# Check for other problematic KDE processes
ps aux | grep -E "(kwin|kded|baloo)" | sort -k4 -nr

# Consider restarting other KDE services
systemctl --user restart kded5  # or kded6 for Plasma 6
```

## 🔧 Advanced Troubleshooting

### Debug Mode

Enable detailed logging by modifying the script:

```bash
# Edit ~/.local/bin/kde-memory-manager.sh
# Add at the top after set -euo pipefail:
set -x  # Enable debug output

# Or run manually with debug
bash -x ~/.local/bin/kde-memory-manager.sh
```

### Memory Leak Investigation

```bash
# Monitor specific process memory over time
watch -n 30 'ps -eo pid,rss,comm | grep plasmashell'

# Create memory usage graph
while true; do
    echo "$(date): $(ps -eo rss,comm | grep plasmashell | awk '{sum+=$1} END {print sum}')" >> plasma-memory.log
    sleep 300
done
```

### System Resource Analysis

```bash
# Check system limits
ulimit -a

# Check systemd service limits
systemctl --user show kde-memory-manager.service | grep -i limit

# Monitor system calls (advanced)
strace -p $(pgrep kde-memory-manager) -e trace=memory
```

## 🛠️ Configuration Tuning

### For Different System Sizes

**8GB RAM Systems (Aggressive)**
```bash
MEMORY_THRESHOLD=60
PLASMA_MEMORY_THRESHOLD=800000
KGLOBAL_MEMORY_THRESHOLD=500000
CHECK_INTERVAL=180  # 3 minutes
```

**16GB RAM Systems (Balanced)**
```bash
MEMORY_THRESHOLD=75
PLASMA_MEMORY_THRESHOLD=1200000
KGLOBAL_MEMORY_THRESHOLD=800000
CHECK_INTERVAL=300  # 5 minutes
```

**32GB+ RAM Systems (Conservative)**
```bash
MEMORY_THRESHOLD=85
PLASMA_MEMORY_THRESHOLD=2000000
KGLOBAL_MEMORY_THRESHOLD=1500000
CHECK_INTERVAL=600  # 10 minutes
```

### For Different Usage Patterns

**Development Workstation (Many Applications)**
```bash
MEMORY_THRESHOLD=70
CHECK_INTERVAL=120  # More frequent checks
```

**Media/Gaming System (High Memory Apps)**
```bash
MEMORY_THRESHOLD=80
PLASMA_MEMORY_THRESHOLD=2000000  # Allow more Plasma memory
```

## 📞 Getting Help

If you're still experiencing issues:

1. **Gather Information**
   ```bash
   # Create diagnostic report
   {
     echo "=== System Info ==="
     uname -a
     echo "=== KDE Version ==="
     plasmashell --version
     echo "=== Service Status ==="
     systemctl --user status kde-memory-manager.service
     echo "=== Recent Logs ==="
     tail -50 ~/.local/share/kde-memory-manager.log
     echo "=== Memory Usage ==="
     free -h
     ps aux --sort=-%mem | head -10
   } > kde-memory-guardian-debug.txt
   ```

2. **Create GitHub Issue**
   - Include the diagnostic report
   - Describe the specific problem
   - Include steps to reproduce

3. **Community Support**
   - Check GitHub Discussions for similar issues
   - Search existing issues for solutions

## 🔄 Recovery Procedures

### Complete Reset
```bash
# Stop service
systemctl --user stop kde-memory-manager.service
systemctl --user disable kde-memory-manager.service

# Remove files
rm ~/.local/bin/kde-memory-manager.sh
rm ~/.config/systemd/user/kde-memory-manager.service
rm ~/.local/share/kde-memory-manager.log*

# Reinstall
cd kde-memory-guardian
./install.sh
```

### Emergency Plasma Recovery
```bash
# If Plasma becomes unresponsive
# Switch to TTY (Ctrl+Alt+F2)
killall plasmashell
kstart plasmashell

# Or restart entire KDE session
systemctl --user restart plasma-plasmashell.service
```
