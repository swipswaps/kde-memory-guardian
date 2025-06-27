#!/usr/bin/env python3
"""
🔧 System Diagnostic Correlator
Real-time system issue detection and correlation with clipboard data
Specifically designed for KDE Plasma 6 issues on AMD/Fedora systems

Features:
- Real-time system message monitoring
- KDE Plasma crash detection and recovery
- Memory leak detection
- Graphics driver issue monitoring
- Clipboard data correlation with system events
- Automated hardening recommendations
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
import subprocess
import threading
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
import psutil
import os

app = Flask(__name__)

# Configuration
CLIPBOARD_DB = Path.home() / '.local/share/clipboard_daemon/clipboard.sqlite'

class SystemDiagnosticCorrelator:
    def __init__(self):
        self.clipboard_db = CLIPBOARD_DB
        self.monitoring = False
        self.system_events = []
        self.plasma_crashes = []
        self.memory_issues = []
        self.graphics_issues = []
        
    def start_monitoring(self):
        """Start real-time system monitoring"""
        if not self.monitoring:
            self.monitoring = True
            threading.Thread(target=self._monitor_system_logs, daemon=True).start()
            threading.Thread(target=self._monitor_plasma_health, daemon=True).start()
            threading.Thread(target=self._monitor_memory_usage, daemon=True).start()
    
    def _monitor_system_logs(self):
        """Monitor system logs for KDE/graphics issues"""
        try:
            # Follow journalctl for real-time monitoring
            process = subprocess.Popen([
                'journalctl', '-f', '--no-pager', 
                '--grep=kwin|plasma|compositor|drm|amd|graphics|crash|error'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            while self.monitoring:
                line = process.stdout.readline()
                if line:
                    self._analyze_log_line(line.strip())
                time.sleep(0.1)
                
        except Exception as e:
            print(f"Error monitoring system logs: {e}")
    
    def _analyze_log_line(self, line):
        """Analyze log line for known issues"""
        timestamp = datetime.now()
        
        # KDE Plasma crashes
        if any(keyword in line.lower() for keyword in ['plasmashell', 'kwin_wayland', 'kwin_x11']):
            if any(error in line.lower() for error in ['crash', 'segfault', 'killed', 'terminated']):
                event = {
                    'timestamp': timestamp.isoformat(),
                    'type': 'plasma_crash',
                    'severity': 'critical',
                    'message': line,
                    'component': self._extract_component(line)
                }
                self.plasma_crashes.append(event)
                self.system_events.append(event)
                
                # Trigger automatic recovery
                self._trigger_plasma_recovery()
        
        # Graphics driver issues
        if any(keyword in line.lower() for keyword in ['drm', 'amd', 'radeon', 'graphics']):
            if any(error in line.lower() for error in ['error', 'failed', 'timeout', 'hang']):
                event = {
                    'timestamp': timestamp.isoformat(),
                    'type': 'graphics_issue',
                    'severity': 'high',
                    'message': line,
                    'driver': self._extract_driver_info(line)
                }
                self.graphics_issues.append(event)
                self.system_events.append(event)
        
        # Memory issues
        if any(keyword in line.lower() for keyword in ['oom', 'memory', 'swap']):
            if any(error in line.lower() for error in ['killed', 'out of memory', 'leak']):
                event = {
                    'timestamp': timestamp.isoformat(),
                    'type': 'memory_issue',
                    'severity': 'high',
                    'message': line,
                    'process': self._extract_process_name(line)
                }
                self.memory_issues.append(event)
                self.system_events.append(event)
    
    def _monitor_plasma_health(self):
        """Monitor KDE Plasma process health"""
        while self.monitoring:
            try:
                # Check if plasmashell is running
                plasma_running = any('plasmashell' in p.name() for p in psutil.process_iter(['name']))
                
                if not plasma_running:
                    event = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'plasma_missing',
                        'severity': 'critical',
                        'message': 'plasmashell process not found',
                        'action': 'auto_restart_triggered'
                    }
                    self.plasma_crashes.append(event)
                    self.system_events.append(event)
                    
                    # Auto-restart plasmashell
                    self._trigger_plasma_recovery()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error monitoring Plasma health: {e}")
                time.sleep(10)
    
    def _monitor_memory_usage(self):
        """Monitor system memory usage"""
        while self.monitoring:
            try:
                memory = psutil.virtual_memory()
                swap = psutil.swap_memory()
                
                # Alert on high memory usage (>90%)
                if memory.percent > 90:
                    event = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'high_memory_usage',
                        'severity': 'warning',
                        'message': f'High memory usage: {memory.percent:.1f}%',
                        'memory_percent': memory.percent,
                        'swap_percent': swap.percent
                    }
                    self.memory_issues.append(event)
                    self.system_events.append(event)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error monitoring memory: {e}")
                time.sleep(60)
    
    def _trigger_plasma_recovery(self):
        """Trigger automatic Plasma recovery"""
        try:
            print("🔄 Triggering Plasma recovery...")
            
            # Kill plasmashell
            subprocess.run(['killall', 'plasmashell'], capture_output=True)
            time.sleep(2)
            
            # Restart plasmashell
            subprocess.Popen(['plasmashell'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Log recovery action
            event = {
                'timestamp': datetime.now().isoformat(),
                'type': 'plasma_recovery',
                'severity': 'info',
                'message': 'Automatic Plasma recovery triggered',
                'action': 'plasmashell_restarted'
            }
            self.system_events.append(event)
            
        except Exception as e:
            print(f"Error during Plasma recovery: {e}")
    
    def _extract_component(self, line):
        """Extract component name from log line"""
        components = ['plasmashell', 'kwin_wayland', 'kwin_x11', 'kwin', 'plasma']
        for component in components:
            if component in line.lower():
                return component
        return 'unknown'
    
    def _extract_driver_info(self, line):
        """Extract graphics driver info from log line"""
        drivers = ['amdgpu', 'radeon', 'drm', 'mesa']
        for driver in drivers:
            if driver in line.lower():
                return driver
        return 'unknown'
    
    def _extract_process_name(self, line):
        """Extract process name from log line"""
        # Simple regex to extract process names
        match = re.search(r'(\w+)\[\d+\]', line)
        return match.group(1) if match else 'unknown'
    
    def get_recent_events(self, hours=1):
        """Get recent system events"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_events = [
            event for event in self.system_events
            if datetime.fromisoformat(event['timestamp']) > cutoff
        ]
        return sorted(recent_events, key=lambda x: x['timestamp'], reverse=True)
    
    def correlate_with_clipboard(self, hours=1):
        """Correlate system events with clipboard data"""
        try:
            # Get recent clipboard entries
            conn = sqlite3.connect(str(self.clipboard_db))
            conn.row_factory = sqlite3.Row
            
            cutoff = datetime.now() - timedelta(hours=hours)
            cursor = conn.execute('''
                SELECT id, content, timestamp
                FROM clipboard_history 
                WHERE datetime(timestamp) > ?
                ORDER BY timestamp DESC
            ''', (cutoff.isoformat(),))
            
            clipboard_entries = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # Get recent system events
            system_events = self.get_recent_events(hours)
            
            # Find correlations (events within 5 minutes of clipboard entries)
            correlations = []
            for clipboard_entry in clipboard_entries:
                clipboard_time = datetime.fromisoformat(clipboard_entry['timestamp'])
                
                for event in system_events:
                    event_time = datetime.fromisoformat(event['timestamp'])
                    time_diff = abs((event_time - clipboard_time).total_seconds())
                    
                    if time_diff <= 300:  # Within 5 minutes
                        correlation = {
                            'clipboard_entry': clipboard_entry,
                            'system_event': event,
                            'time_difference_seconds': time_diff,
                            'correlation_strength': max(0, 100 - (time_diff / 3))  # Stronger correlation for closer times
                        }
                        correlations.append(correlation)
            
            return sorted(correlations, key=lambda x: x['correlation_strength'], reverse=True)
            
        except Exception as e:
            print(f"Error correlating data: {e}")
            return []
    
    def get_diagnostic_summary(self):
        """Get comprehensive diagnostic summary"""
        return {
            'plasma_crashes': len(self.plasma_crashes),
            'graphics_issues': len(self.graphics_issues),
            'memory_issues': len(self.memory_issues),
            'total_events': len(self.system_events),
            'monitoring_active': self.monitoring,
            'recent_events': self.get_recent_events(1),
            'system_health': self._assess_system_health(),
            'recommendations': self._generate_recommendations()
        }
    
    def _assess_system_health(self):
        """Assess overall system health"""
        recent_events = self.get_recent_events(1)
        critical_events = [e for e in recent_events if e['severity'] == 'critical']
        
        if len(critical_events) > 3:
            return 'critical'
        elif len(recent_events) > 10:
            return 'warning'
        else:
            return 'healthy'
    
    def _generate_recommendations(self):
        """Generate hardening recommendations based on detected issues"""
        recommendations = []
        
        if len(self.plasma_crashes) > 0:
            recommendations.append({
                'type': 'plasma_stability',
                'priority': 'high',
                'title': 'KDE Plasma Stability Issues Detected',
                'description': 'Multiple Plasma crashes detected. Consider switching to X11 session or updating graphics drivers.',
                'actions': [
                    'Switch to Plasma X11 session',
                    'Update AMD graphics drivers',
                    'Disable compositor effects',
                    'Check for Plasma updates'
                ]
            })
        
        if len(self.graphics_issues) > 0:
            recommendations.append({
                'type': 'graphics_driver',
                'priority': 'high',
                'title': 'Graphics Driver Issues Detected',
                'description': 'AMD graphics driver issues may be causing system instability.',
                'actions': [
                    'Update kernel and mesa drivers',
                    'Add amdgpu.dc=0 to kernel parameters',
                    'Disable hardware acceleration in browsers',
                    'Check for firmware updates'
                ]
            })
        
        if len(self.memory_issues) > 0:
            recommendations.append({
                'type': 'memory_optimization',
                'priority': 'medium',
                'title': 'Memory Issues Detected',
                'description': 'High memory usage or potential memory leaks detected.',
                'actions': [
                    'Enable zram compression',
                    'Increase swap size',
                    'Monitor for memory leaks',
                    'Close unnecessary applications'
                ]
            })
        
        return recommendations

# Global correlator instance
correlator = SystemDiagnosticCorrelator()

@app.route('/')
def diagnostic_dashboard():
    """System diagnostic dashboard"""
    return render_template_string(DIAGNOSTIC_TEMPLATE)

@app.route('/api/start-monitoring')
def start_monitoring():
    """Start system monitoring"""
    correlator.start_monitoring()
    return jsonify({'status': 'monitoring_started'})

@app.route('/api/diagnostic-summary')
def diagnostic_summary():
    """Get diagnostic summary"""
    return jsonify(correlator.get_diagnostic_summary())

@app.route('/api/correlations')
def get_correlations():
    """Get clipboard-system event correlations"""
    hours = request.args.get('hours', 1, type=int)
    correlations = correlator.correlate_with_clipboard(hours)
    return jsonify(correlations)

@app.route('/api/plasma-recovery')
def trigger_plasma_recovery():
    """Manually trigger Plasma recovery"""
    correlator._trigger_plasma_recovery()
    return jsonify({'status': 'recovery_triggered'})

# Diagnostic Template
DIAGNOSTIC_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔧 System Diagnostic Correlator</title>
    <style>
        :root {
            --bg-primary: #0a0e1a;
            --bg-secondary: #1a1f2e;
            --bg-surface: #2a2f3e;
            --text-primary: #ffffff;
            --text-secondary: #b0b7c3;
            --accent-critical: #ff4757;
            --accent-warning: #ffa502;
            --accent-success: #2ed573;
            --accent-info: #3742fa;
            --border-color: #3a3f4e;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }

        .header {
            background: var(--bg-secondary);
            padding: 1rem 2rem;
            border-bottom: 2px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo { font-size: 1.5rem; font-weight: bold; }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 500;
        }

        .status-healthy { background: var(--accent-success); color: white; }
        .status-warning { background: var(--accent-warning); color: white; }
        .status-critical { background: var(--accent-critical); color: white; }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            display: grid;
            gap: 2rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
        }

        .stat-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            position: relative;
            overflow: hidden;
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
        }

        .stat-card.critical::before { background: var(--accent-critical); }
        .stat-card.warning::before { background: var(--accent-warning); }
        .stat-card.success::before { background: var(--accent-success); }
        .stat-card.info::before { background: var(--accent-info); }

        .stat-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .stat-title {
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-icon { font-size: 1.5rem; }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .stat-description {
            font-size: 0.75rem;
            color: var(--text-secondary);
        }

        .section {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--border-color);
        }

        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
        }

        .btn {
            background: var(--accent-info);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }

        .btn:hover { transform: translateY(-1px); opacity: 0.9; }
        .btn.critical { background: var(--accent-critical); }
        .btn.warning { background: var(--accent-warning); }

        .event-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-height: 400px;
            overflow-y: auto;
        }

        .event-item {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            border-left: 4px solid var(--accent-info);
        }

        .event-item.critical { border-left-color: var(--accent-critical); }
        .event-item.warning { border-left-color: var(--accent-warning); }
        .event-item.success { border-left-color: var(--accent-success); }

        .event-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }

        .event-type {
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: bold;
            letter-spacing: 0.5px;
        }

        .event-timestamp {
            font-size: 0.75rem;
            color: var(--text-secondary);
        }

        .event-message {
            font-size: 0.875rem;
            font-family: monospace;
            background: rgba(0, 0, 0, 0.3);
            padding: 0.5rem;
            border-radius: 4px;
            word-break: break-all;
        }

        .correlation-item {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .correlation-strength {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
        }

        .strength-high { background: var(--accent-critical); color: white; }
        .strength-medium { background: var(--accent-warning); color: white; }
        .strength-low { background: var(--accent-info); color: white; }

        .recommendation-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }

        .recommendation-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .recommendation-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .recommendation-actions {
            list-style: none;
            padding-left: 1rem;
        }

        .recommendation-actions li {
            margin-bottom: 0.5rem;
            position: relative;
        }

        .recommendation-actions li::before {
            content: '→';
            position: absolute;
            left: -1rem;
            color: var(--accent-info);
        }

        .loading {
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
        }

        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid var(--border-color);
            border-top: 2px solid var(--accent-info);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 0.5rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .fade-in { animation: fadeIn 0.5s ease-in; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">🔧 System Diagnostic Correlator</div>
        <div class="status-indicator" id="systemStatus">
            <span class="spinner"></span>
            <span>Initializing...</span>
        </div>
    </header>

    <div class="container">
        <!-- Stats Grid -->
        <div class="stats-grid" id="statsGrid">
            <!-- Stats populated by JavaScript -->
        </div>

        <!-- Recent Events -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Recent System Events</h2>
                <button class="btn critical" onclick="triggerPlasmaRecovery()">
                    🔄 Emergency Plasma Recovery
                </button>
            </div>
            <div class="event-list" id="eventList">
                <div class="loading">
                    <div class="spinner"></div>
                    <span>Loading system events...</span>
                </div>
            </div>
        </div>

        <!-- Clipboard Correlations -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Clipboard-System Event Correlations</h2>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    Events occurring near clipboard activity
                </div>
            </div>
            <div id="correlationList">
                <div class="loading">
                    <div class="spinner"></div>
                    <span>Analyzing correlations...</span>
                </div>
            </div>
        </div>

        <!-- Hardening Recommendations -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Hardening Recommendations</h2>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    Based on detected issues
                </div>
            </div>
            <div id="recommendationList">
                <div class="loading">
                    <div class="spinner"></div>
                    <span>Generating recommendations...</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        class DiagnosticCorrelator {
            constructor() {
                this.init();
            }

            async init() {
                await this.startMonitoring();
                await this.loadDiagnosticData();
                setInterval(() => this.loadDiagnosticData(), 10000); // Refresh every 10 seconds
            }

            async startMonitoring() {
                try {
                    await fetch('/api/start-monitoring');
                } catch (error) {
                    console.error('Error starting monitoring:', error);
                }
            }

            async loadDiagnosticData() {
                try {
                    const response = await fetch('/api/diagnostic-summary');
                    const data = await response.json();

                    this.updateSystemStatus(data.system_health);
                    this.renderStats(data);
                    this.renderEvents(data.recent_events);
                    this.renderRecommendations(data.recommendations);

                    // Load correlations
                    const correlationResponse = await fetch('/api/correlations?hours=1');
                    const correlations = await correlationResponse.json();
                    this.renderCorrelations(correlations);

                } catch (error) {
                    console.error('Error loading diagnostic data:', error);
                }
            }

            updateSystemStatus(health) {
                const statusElement = document.getElementById('systemStatus');
                statusElement.className = `status-indicator status-${health}`;

                const statusText = {
                    'healthy': '✅ System Healthy',
                    'warning': '⚠️ Issues Detected',
                    'critical': '🚨 Critical Issues'
                };

                statusElement.innerHTML = `<span>${statusText[health] || '❓ Unknown'}</span>`;
            }

            renderStats(data) {
                const container = document.getElementById('statsGrid');
                container.innerHTML = '';

                const stats = [
                    {
                        title: 'Plasma Crashes',
                        value: data.plasma_crashes,
                        icon: '💥',
                        type: data.plasma_crashes > 0 ? 'critical' : 'success',
                        description: 'Desktop environment crashes'
                    },
                    {
                        title: 'Graphics Issues',
                        value: data.graphics_issues,
                        icon: '🎮',
                        type: data.graphics_issues > 0 ? 'warning' : 'success',
                        description: 'AMD driver problems'
                    },
                    {
                        title: 'Memory Issues',
                        value: data.memory_issues,
                        icon: '🧠',
                        type: data.memory_issues > 0 ? 'warning' : 'success',
                        description: 'Memory leaks and usage'
                    },
                    {
                        title: 'Total Events',
                        value: data.total_events,
                        icon: '📊',
                        type: 'info',
                        description: 'All system events'
                    },
                    {
                        title: 'Monitoring',
                        value: data.monitoring_active ? 'Active' : 'Inactive',
                        icon: '👁️',
                        type: data.monitoring_active ? 'success' : 'critical',
                        description: 'Real-time monitoring status'
                    }
                ];

                stats.forEach(stat => {
                    const card = document.createElement('div');
                    card.className = `stat-card ${stat.type} fade-in`;
                    card.innerHTML = `
                        <div class="stat-header">
                            <div class="stat-title">${stat.title}</div>
                            <div class="stat-icon">${stat.icon}</div>
                        </div>
                        <div class="stat-value">${stat.value}</div>
                        <div class="stat-description">${stat.description}</div>
                    `;
                    container.appendChild(card);
                });
            }

            renderEvents(events) {
                const container = document.getElementById('eventList');
                container.innerHTML = '';

                if (events.length === 0) {
                    container.innerHTML = '<div class="loading">No recent events</div>';
                    return;
                }

                events.forEach(event => {
                    const item = document.createElement('div');
                    item.className = `event-item ${event.severity} fade-in`;
                    item.innerHTML = `
                        <div class="event-header">
                            <div class="event-type">${event.type.replace('_', ' ')}</div>
                            <div class="event-timestamp">${new Date(event.timestamp).toLocaleString()}</div>
                        </div>
                        <div class="event-message">${this.escapeHtml(event.message)}</div>
                    `;
                    container.appendChild(item);
                });
            }

            renderCorrelations(correlations) {
                const container = document.getElementById('correlationList');
                container.innerHTML = '';

                if (correlations.length === 0) {
                    container.innerHTML = '<div class="loading">No correlations found</div>';
                    return;
                }

                correlations.slice(0, 10).forEach(correlation => {
                    const strengthClass = correlation.correlation_strength > 70 ? 'high' :
                                        correlation.correlation_strength > 40 ? 'medium' : 'low';

                    const item = document.createElement('div');
                    item.className = 'correlation-item fade-in';
                    item.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span class="correlation-strength strength-${strengthClass}">
                                ${Math.round(correlation.correlation_strength)}% correlation
                            </span>
                            <span style="font-size: 0.75rem; color: var(--text-secondary);">
                                ${Math.round(correlation.time_difference_seconds)}s apart
                            </span>
                        </div>
                        <div style="font-size: 0.875rem; margin-bottom: 0.5rem;">
                            <strong>System Event:</strong> ${correlation.system_event.type}
                        </div>
                        <div style="font-size: 0.875rem; margin-bottom: 0.5rem;">
                            <strong>Clipboard Content:</strong> ${this.escapeHtml(correlation.clipboard_entry.content.substring(0, 100))}...
                        </div>
                    `;
                    container.appendChild(item);
                });
            }

            renderRecommendations(recommendations) {
                const container = document.getElementById('recommendationList');
                container.innerHTML = '';

                if (recommendations.length === 0) {
                    container.innerHTML = '<div class="loading">No recommendations at this time</div>';
                    return;
                }

                recommendations.forEach(rec => {
                    const card = document.createElement('div');
                    card.className = 'recommendation-card fade-in';
                    card.innerHTML = `
                        <div class="recommendation-header">
                            <div>
                                <div class="recommendation-title">${rec.title}</div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">${rec.description}</div>
                            </div>
                            <span class="status-indicator status-${rec.priority}">${rec.priority.toUpperCase()}</span>
                        </div>
                        <ul class="recommendation-actions">
                            ${rec.actions.map(action => `<li>${action}</li>`).join('')}
                        </ul>
                    `;
                    container.appendChild(card);
                });
            }

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        }

        async function triggerPlasmaRecovery() {
            try {
                await fetch('/api/plasma-recovery');
                alert('Plasma recovery triggered! Desktop should restart shortly.');
            } catch (error) {
                alert('Error triggering recovery: ' + error.message);
            }
        }

        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            new DiagnosticCorrelator();
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("🔧 Starting System Diagnostic Correlator...")
    print("=" * 70)
    print("🎯 REAL-TIME SYSTEM ISSUE DETECTION & CORRELATION")
    print("📊 Monitoring KDE Plasma 6, AMD graphics, and memory issues")
    print("🔗 Correlating system events with clipboard data")
    print("")
    print("🚀 Features:")
    print("• Real-time Plasma crash detection and auto-recovery")
    print("• AMD graphics driver issue monitoring")
    print("• Memory leak and usage monitoring")
    print("• Clipboard data correlation with system events")
    print("• Automated hardening recommendations")
    print("")
    print("📱 ACCESS: http://localhost:7000")
    print("=" * 70)
    
    # Start monitoring immediately
    correlator.start_monitoring()
    
    app.run(host='0.0.0.0', port=7000, debug=False)
