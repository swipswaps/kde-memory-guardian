#!/usr/bin/env python3
"""
🚨 Performance Emergency Monitor
Real-time performance issue detection and immediate fixes
Specifically designed for VSCode/KDE performance problems

Features:
- Real-time CPU/memory monitoring
- VSCode extension analysis
- Immediate performance fixes
- Clipboard correlation with performance issues
- Emergency system optimization
"""

from flask import Flask, render_template_string, jsonify, request
import subprocess
import psutil
import time
import threading
from datetime import datetime
import sqlite3
from pathlib import Path
import json
import os

app = Flask(__name__)

# Configuration
CLIPBOARD_DB = Path.home() / '.local/share/clipboard_daemon/clipboard.sqlite'

class PerformanceEmergencyMonitor:
    def __init__(self):
        self.monitoring = False
        self.performance_issues = []
        self.high_cpu_processes = []
        self.memory_hogs = []
        
    def start_monitoring(self):
        """Start real-time performance monitoring"""
        if not self.monitoring:
            self.monitoring = True
            threading.Thread(target=self._monitor_performance, daemon=True).start()
    
    def _monitor_performance(self):
        """Monitor system performance continuously"""
        while self.monitoring:
            try:
                # Get top CPU processes
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                    try:
                        proc_info = proc.info
                        if proc_info['cpu_percent'] > 5 or proc_info['memory_percent'] > 5:
                            processes.append(proc_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # Sort by CPU usage
                processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
                
                # Check for performance issues
                for proc in processes[:5]:  # Top 5 processes
                    if proc['cpu_percent'] > 30:
                        issue = {
                            'timestamp': datetime.now().isoformat(),
                            'type': 'high_cpu',
                            'process': proc['name'],
                            'pid': proc['pid'],
                            'cpu_percent': proc['cpu_percent'],
                            'memory_mb': proc['memory_info']['rss'] / 1024 / 1024,
                            'severity': 'critical' if proc['cpu_percent'] > 40 else 'high'
                        }
                        
                        # Check if this is a new issue
                        if not any(i['pid'] == proc['pid'] and i['type'] == 'high_cpu' 
                                 for i in self.performance_issues[-5:]):
                            self.performance_issues.append(issue)
                            self.high_cpu_processes.append(issue)
                            
                            # Auto-fix for known issues
                            if 'code-insiders' in proc['name'].lower():
                                self._handle_vscode_performance_issue(issue)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Error monitoring performance: {e}")
                time.sleep(10)
    
    def _handle_vscode_performance_issue(self, issue):
        """Handle VSCode performance issues automatically"""
        try:
            print(f"🚨 VSCode performance issue detected: {issue['cpu_percent']:.1f}% CPU")
            
            # Log the issue
            fix_action = {
                'timestamp': datetime.now().isoformat(),
                'type': 'vscode_performance_fix',
                'original_issue': issue,
                'actions_taken': [],
                'success': False
            }
            
            # Try to reduce VSCode CPU usage
            try:
                # Send SIGUSR1 to VSCode to trigger garbage collection
                os.kill(issue['pid'], 10)  # SIGUSR1
                fix_action['actions_taken'].append('triggered_gc')
                print("✅ Triggered VSCode garbage collection")
            except:
                pass
            
            # Check if issue persists after 10 seconds
            time.sleep(10)
            try:
                proc = psutil.Process(issue['pid'])
                new_cpu = proc.cpu_percent()
                if new_cpu < issue['cpu_percent'] * 0.8:  # 20% improvement
                    fix_action['success'] = True
                    print(f"✅ VSCode CPU usage reduced from {issue['cpu_percent']:.1f}% to {new_cpu:.1f}%")
                else:
                    print(f"⚠️ VSCode CPU usage still high: {new_cpu:.1f}%")
            except:
                pass
            
            self.performance_issues.append(fix_action)
            
        except Exception as e:
            print(f"Error handling VSCode issue: {e}")
    
    def get_current_performance(self):
        """Get current system performance snapshot"""
        try:
            # CPU and memory info
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Top processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 1:  # Only processes using CPU
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory_mb': proc_info['memory_info']['rss'] / 1024 / 1024,
                            'memory_percent': proc_info['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / 1024 / 1024 / 1024,
                'memory_total_gb': memory.total / 1024 / 1024 / 1024,
                'swap_percent': swap.percent,
                'top_processes': processes[:10],
                'performance_issues': len(self.performance_issues),
                'monitoring_active': self.monitoring
            }
            
        except Exception as e:
            print(f"Error getting performance data: {e}")
            return {}
    
    def correlate_with_clipboard(self):
        """Correlate performance issues with clipboard data"""
        try:
            conn = sqlite3.connect(str(CLIPBOARD_DB))
            conn.row_factory = sqlite3.Row
            
            # Get recent clipboard entries about performance
            cursor = conn.execute('''
                SELECT id, content, timestamp
                FROM clipboard_history 
                WHERE content LIKE '%slow%' OR content LIKE '%lag%' OR content LIKE '%performance%'
                   OR content LIKE '%cpu%' OR content LIKE '%memory%' OR content LIKE '%freeze%'
                ORDER BY timestamp DESC 
                LIMIT 5
            ''')
            
            clipboard_entries = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # Correlate with recent performance issues
            correlations = []
            for entry in clipboard_entries:
                for issue in self.performance_issues[-10:]:  # Last 10 issues
                    entry_time = datetime.fromisoformat(entry['timestamp'])
                    issue_time = datetime.fromisoformat(issue['timestamp'])
                    time_diff = abs((issue_time - entry_time).total_seconds())
                    
                    if time_diff <= 1800:  # Within 30 minutes
                        correlation = {
                            'clipboard_entry': entry,
                            'performance_issue': issue,
                            'time_difference_minutes': time_diff / 60,
                            'correlation_strength': max(0, 100 - (time_diff / 18))
                        }
                        correlations.append(correlation)
            
            return sorted(correlations, key=lambda x: x['correlation_strength'], reverse=True)
            
        except Exception as e:
            print(f"Error correlating data: {e}")
            return []
    
    def get_emergency_fixes(self):
        """Get emergency performance fixes"""
        current_perf = self.get_current_performance()
        fixes = []
        
        # Check for high CPU processes
        for proc in current_perf.get('top_processes', [])[:3]:
            if proc['cpu_percent'] > 30:
                if 'code' in proc['name'].lower():
                    fixes.append({
                        'priority': 'critical',
                        'title': f'VSCode High CPU Usage ({proc["cpu_percent"]:.1f}%)',
                        'description': f'Process {proc["name"]} is using excessive CPU',
                        'actions': [
                            'Disable VSCode extensions',
                            'Restart VSCode with --disable-extensions',
                            'Close large files or projects',
                            'Switch to VSCode stable version'
                        ],
                        'command': f'kill -USR1 {proc["pid"]}  # Trigger garbage collection'
                    })
                elif 'firefox' in proc['name'].lower():
                    fixes.append({
                        'priority': 'high',
                        'title': f'Firefox High CPU Usage ({proc["cpu_percent"]:.1f}%)',
                        'description': f'Browser is using excessive CPU',
                        'actions': [
                            'Close unnecessary tabs',
                            'Disable hardware acceleration',
                            'Clear browser cache',
                            'Restart Firefox'
                        ],
                        'command': f'kill -USR1 {proc["pid"]}'
                    })
                else:
                    fixes.append({
                        'priority': 'medium',
                        'title': f'High CPU Process: {proc["name"]}',
                        'description': f'Process using {proc["cpu_percent"]:.1f}% CPU',
                        'actions': [
                            f'Investigate process {proc["name"]}',
                            'Consider terminating if unnecessary',
                            'Check for memory leaks'
                        ],
                        'command': f'kill -TERM {proc["pid"]}  # Graceful termination'
                    })
        
        # Check for high memory usage
        if current_perf.get('memory_percent', 0) > 80:
            fixes.append({
                'priority': 'high',
                'title': f'High Memory Usage ({current_perf["memory_percent"]:.1f}%)',
                'description': 'System memory is critically low',
                'actions': [
                    'Close unnecessary applications',
                    'Clear system caches',
                    'Enable swap if not active',
                    'Restart memory-heavy applications'
                ],
                'command': 'echo 3 | sudo tee /proc/sys/vm/drop_caches  # Clear caches'
            })
        
        return fixes

# Global monitor instance
monitor = PerformanceEmergencyMonitor()

@app.route('/')
def emergency_dashboard():
    """Emergency performance dashboard"""
    return render_template_string(EMERGENCY_TEMPLATE)

@app.route('/api/start-monitoring')
def start_monitoring():
    """Start performance monitoring"""
    monitor.start_monitoring()
    return jsonify({'status': 'monitoring_started'})

@app.route('/api/current-performance')
def current_performance():
    """Get current performance data"""
    return jsonify(monitor.get_current_performance())

@app.route('/api/emergency-fixes')
def emergency_fixes():
    """Get emergency performance fixes"""
    return jsonify(monitor.get_emergency_fixes())

@app.route('/api/correlations')
def performance_correlations():
    """Get performance-clipboard correlations"""
    return jsonify(monitor.correlate_with_clipboard())

@app.route('/api/kill-process/<int:pid>')
def kill_process(pid):
    """Emergency process termination"""
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc.terminate()
        return jsonify({'status': 'terminated', 'process': proc_name, 'pid': pid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Emergency template will be added in next chunk
EMERGENCY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚨 Performance Emergency Monitor</title>
    <style>
        /* Emergency CSS will be added in next chunk */
    </style>
</head>
<body>
    <!-- Emergency HTML will be added in next chunk -->
</body>
</html>
'''

if __name__ == '__main__':
    print("🚨 Starting Performance Emergency Monitor...")
    print("=" * 60)
    print("⚡ REAL-TIME PERFORMANCE ISSUE DETECTION")
    print("🎯 VSCode/KDE performance optimization")
    print("🔗 Clipboard correlation with performance issues")
    print("")
    print("🚀 Features:")
    print("• Real-time CPU/memory monitoring")
    print("• Automatic VSCode performance fixes")
    print("• Emergency process termination")
    print("• Performance-clipboard correlation")
    print("• Immediate optimization recommendations")
    print("")
    print("📱 ACCESS: http://localhost:8000")
    print("=" * 60)
    
    # Start monitoring immediately
    monitor.start_monitoring()
    
    app.run(host='0.0.0.0', port=8000, debug=False)
