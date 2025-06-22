# KDE Memory Guardian - Configuration Guide

This guide explains how to customize KDE Memory Guardian for your specific system and usage patterns.

## 📋 Configuration Overview

KDE Memory Guardian uses several configuration methods:

1. **Script Variables**: Core monitoring thresholds and behavior
2. **Systemd Service**: Service behavior and resource limits  
3. **System Settings**: Kernel memory management parameters
4. **Environment Variables**: Runtime configuration overrides

## ⚙️ Core Configuration

### Memory Thresholds

Edit `~/.local/bin/kde-memory-manager.sh` to adjust these key variables:

```bash
# System memory threshold (percentage)
# When total system memory usage exceeds this, trigger cleanup
# DEFAULT: 80 (80% of total RAM)
# RANGE: 50-95 (lower = more aggressive, higher = more tolerant)
readonly MEMORY_THRESHOLD=${MEMORY_THRESHOLD:-80}

# Plasma memory threshold (KB)  
# When plasmashell uses more than this, restart it
# DEFAULT: 1500000 (1.5GB)
# TYPICAL RANGE: 500MB-3GB depending on system RAM
readonly PLASMA_MEMORY_THRESHOLD=${PLASMA_MEMORY_THRESHOLD:-1500000}

# KGlobalAccel memory threshold (KB)
# When kglobalacceld uses more than this, restart it  
# DEFAULT: 1000000 (1GB)
# TYPICAL RANGE: 100MB-2GB depending on usage
readonly KGLOBAL_MEMORY_THRESHOLD=${KGLOBAL_MEMORY_THRESHOLD:-1000000}

# Check interval (seconds)
# How often to check memory usage
# DEFAULT: 300 (5 minutes)
# RANGE: 60-1800 (1 minute to 30 minutes)
readonly CHECK_INTERVAL=${CHECK_INTERVAL:-300}
```

### Configuration Examples by System Type

#### 8GB RAM System (Aggressive Management)
```bash
# For systems with limited RAM, be more aggressive
MEMORY_THRESHOLD=60           # Trigger at 60% system memory
PLASMA_MEMORY_THRESHOLD=800000    # Restart Plasma at 800MB
KGLOBAL_MEMORY_THRESHOLD=500000   # Restart KGlobal at 500MB  
CHECK_INTERVAL=180            # Check every 3 minutes
```

#### 16GB RAM System (Balanced Management)
```bash
# Balanced approach for typical desktop systems
MEMORY_THRESHOLD=75           # Trigger at 75% system memory
PLASMA_MEMORY_THRESHOLD=1200000   # Restart Plasma at 1.2GB
KGLOBAL_MEMORY_THRESHOLD=800000   # Restart KGlobal at 800MB
CHECK_INTERVAL=300            # Check every 5 minutes (default)
```

#### 32GB+ RAM System (Conservative Management)
```bash
# For high-memory systems, be more tolerant
MEMORY_THRESHOLD=85           # Trigger at 85% system memory
PLASMA_MEMORY_THRESHOLD=2500000   # Restart Plasma at 2.5GB
KGLOBAL_MEMORY_THRESHOLD=1500000  # Restart KGlobal at 1.5GB
CHECK_INTERVAL=600            # Check every 10 minutes
```

### Configuration by Usage Pattern

#### Development Workstation
```bash
# Frequent application switching, many open windows
MEMORY_THRESHOLD=70           # More aggressive due to high memory usage
PLASMA_MEMORY_THRESHOLD=1000000   # Lower threshold for stability
CHECK_INTERVAL=120            # More frequent checks (2 minutes)
```

#### Media/Gaming System  
```bash
# High-memory applications, less frequent KDE interaction
MEMORY_THRESHOLD=80           # Standard threshold
PLASMA_MEMORY_THRESHOLD=2000000   # Allow more Plasma memory
CHECK_INTERVAL=600            # Less frequent checks (10 minutes)
```

#### Server/Headless with KDE
```bash
# Minimal KDE usage, focus on stability
MEMORY_THRESHOLD=90           # Very conservative
PLASMA_MEMORY_THRESHOLD=500000    # Keep Plasma minimal
CHECK_INTERVAL=900            # Infrequent checks (15 minutes)
```

## 🔧 Advanced Configuration

### Environment Variable Overrides

You can override configuration without editing files:

```bash
# Set environment variables before starting service
systemctl --user set-environment MEMORY_THRESHOLD=70
systemctl --user set-environment CHECK_INTERVAL=180
systemctl --user restart kde-memory-manager.service
```

### Systemd Service Customization

Create a service override to customize behavior:

```bash
# Create override directory
mkdir -p ~/.config/systemd/user/kde-memory-manager.service.d

# Create custom configuration
cat > ~/.config/systemd/user/kde-memory-manager.service.d/custom.conf << 'EOF'
[Service]
# Custom environment variables
Environment=MEMORY_THRESHOLD=70
Environment=CHECK_INTERVAL=180

# Increase memory limit for the service itself
MemoryMax=100M

# Reduce CPU priority (nice value)
Nice=10

# Custom restart behavior
RestartSec=60
EOF

# Reload and restart service
systemctl --user daemon-reload
systemctl --user restart kde-memory-manager.service
```

### Logging Configuration

#### Adjust Log Verbosity

Edit the script to change logging behavior:

```bash
# Add debug logging (edit kde-memory-manager.sh)
log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        log_message "DEBUG: $1"
    fi
}

# Enable debug mode
systemctl --user set-environment DEBUG=true
systemctl --user restart kde-memory-manager.service
```

#### Custom Log Location

```bash
# Change log file location (edit kde-memory-manager.sh)
readonly LOG_FILE="${LOG_FILE:-$HOME/.local/share/kde-memory-guardian.log}"

# Set custom location
systemctl --user set-environment LOG_FILE="/tmp/kde-memory.log"
```

#### Log Rotation Settings

```bash
# Edit ~/.config/logrotate/kde-memory-manager
/home/*/.*local/share/kde-memory-manager.log {
    # Rotate more frequently
    hourly
    
    # Keep more history  
    rotate 168  # 1 week of hourly logs
    
    # Compress immediately
    compress
    delaycompress
    
    # Rotate even if empty
    ifempty
    
    # Custom post-rotation script
    postrotate
        systemctl --user reload-or-restart kde-memory-manager.service
    endscript
}
```

## 🎛️ System-Wide Optimizations

### Memory Management Tuning

Edit `/etc/sysctl.d/99-kde-memory-optimization.conf`:

```bash
# More aggressive swappiness (prefer RAM even more)
vm.swappiness=5

# Faster dirty page writeback
vm.dirty_writeback_centisecs=1000
vm.dirty_expire_centisecs=3000

# More aggressive cache reclaim
vm.vfs_cache_pressure=150

# Optimize for desktop workloads
vm.dirty_background_ratio=5
vm.dirty_ratio=10

# Memory compaction settings
vm.compact_memory=1
vm.compaction_proactiveness=20
```

### KDE-Specific Optimizations

#### Plasma Configuration

Edit `~/.config/plasmarc`:

```ini
[PlasmaViews][Panel 1]
# Disable transparency effects (saves memory)
alignment=132
floating=0

[Theme]
# Use lightweight theme
name=breeze

[General]  
# Reduce animations (saves memory and CPU)
AnimationDurationFactor=0.25

[KDE Action Restrictions]
# Disable memory-intensive features
action/kwin_rules=false
action/switch_user=false
```

#### KWin Configuration

Edit `~/.config/kwinrc`:

```ini
[Compositing]
# Reduce compositor memory usage
Backend=OpenGL
GLCore=true
GLPreferBufferSwap=a
GLTextureFilter=1

[Effect-PresentWindows]
# Disable memory-intensive effects
BorderActivate=9
BorderActivateAll=9
BorderActivateClass=9
```

## 📊 Monitoring and Alerting

### Custom Notifications

Add desktop notifications for memory events:

```bash
# Edit kde-memory-manager.sh, add to restart functions:
send_notification() {
    local title="$1"
    local message="$2"
    local urgency="${3:-normal}"
    
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "$title" "$message" \
            --icon=dialog-information \
            --urgency="$urgency" \
            --expire-time=5000
    fi
}

# Use in restart functions:
restart_plasmashell() {
    send_notification "KDE Memory Guardian" \
        "Restarting Plasma Shell (memory: ${plasma_memory}KB)" \
        "low"
    # ... rest of function
}
```

### Integration with System Monitors

#### Prometheus Metrics Export

```bash
# Add to kde-memory-manager.sh
export_metrics() {
    local metrics_file="/tmp/kde-memory-guardian.prom"
    
    cat > "$metrics_file" << EOF
# HELP kde_plasma_memory_bytes Plasma shell memory usage in bytes
# TYPE kde_plasma_memory_bytes gauge
kde_plasma_memory_bytes $(($plasma_memory * 1024))

# HELP kde_system_memory_percent System memory usage percentage
# TYPE kde_system_memory_percent gauge  
kde_system_memory_percent $system_mem_usage

# HELP kde_memory_restarts_total Total number of service restarts
# TYPE kde_memory_restarts_total counter
kde_memory_restarts_total $restart_count
EOF
}
```

#### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "KDE Memory Guardian",
    "panels": [
      {
        "title": "Plasma Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "kde_plasma_memory_bytes / 1024 / 1024",
            "legendFormat": "Plasma Memory (MB)"
          }
        ]
      }
    ]
  }
}
```

## 🔄 Configuration Management

### Version Control

Keep your configuration in version control:

```bash
# Create config repository
mkdir ~/.config/kde-memory-guardian
cd ~/.config/kde-memory-guardian
git init

# Track configuration files
cp ~/.local/bin/kde-memory-manager.sh ./
cp ~/.config/systemd/user/kde-memory-manager.service ./
cp /etc/sysctl.d/99-kde-memory-optimization.conf ./

# Commit changes
git add .
git commit -m "Initial KDE Memory Guardian configuration"
```

### Configuration Profiles

Create different profiles for different scenarios:

```bash
# Create profile directory
mkdir -p ~/.config/kde-memory-guardian/profiles

# Development profile
cat > ~/.config/kde-memory-guardian/profiles/development.conf << 'EOF'
MEMORY_THRESHOLD=65
PLASMA_MEMORY_THRESHOLD=1000000
CHECK_INTERVAL=120
EOF

# Gaming profile  
cat > ~/.config/kde-memory-guardian/profiles/gaming.conf << 'EOF'
MEMORY_THRESHOLD=85
PLASMA_MEMORY_THRESHOLD=2000000
CHECK_INTERVAL=600
EOF

# Switch profiles
load_profile() {
    local profile="$1"
    source ~/.config/kde-memory-guardian/profiles/${profile}.conf
    systemctl --user restart kde-memory-manager.service
}
```

## 🧪 Testing Configuration

### Validate Configuration

```bash
# Test configuration syntax
bash -n ~/.local/bin/kde-memory-manager.sh

# Test with dry-run mode (add to script)
DRY_RUN=true ~/.local/bin/kde-memory-manager.sh

# Validate systemd service
systemd-analyze --user verify ~/.config/systemd/user/kde-memory-manager.service
```

### Performance Testing

```bash
# Monitor service resource usage
systemctl --user status kde-memory-manager.service

# Check service limits
systemctl --user show kde-memory-manager.service | grep -E "(Memory|CPU|Tasks)"

# Benchmark memory detection performance
time bash -c 'source ~/.local/bin/kde-memory-manager.sh; get_process_memory plasmashell'
```

This configuration guide provides comprehensive customization options for KDE Memory Guardian. Adjust settings based on your specific system requirements and usage patterns.
