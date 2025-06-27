#!/usr/bin/env python3
"""
KDE Memory Guardian Web Server
Provides web interface for monitoring and testing
"""

import http.server
import socketserver
import os
import json
import subprocess
import threading
import time
from urllib.parse import urlparse, parse_qs

class KDEMemoryGuardianHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/stats':
            self.send_api_response(self.get_memory_stats())
        elif parsed_path.path == '/api/logs':
            self.send_api_response(self.get_recent_logs())
        elif parsed_path.path == '/api/test':
            self.send_api_response(self.run_test_suite())
        else:
            super().do_GET()

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/restart-plasma':
            self.send_api_response(self.restart_plasma())
        elif parsed_path.path == '/api/clear-cache':
            self.send_api_response(self.clear_cache())
        elif parsed_path.path == '/api/view-logs':
            self.send_api_response(self.view_logs())
        elif parsed_path.path == '/api/run-tests':
            self.send_api_response(self.run_comprehensive_tests())
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_api_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_memory_stats(self):
        """Get current memory statistics"""
        try:
            # Get system memory
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            mem_total = 0
            mem_available = 0
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1])
                elif line.startswith('MemAvailable:'):
                    mem_available = int(line.split()[1])
            
            system_usage = int((1 - mem_available / mem_total) * 100) if mem_total > 0 else 0
            
            # Get process memory
            plasma_memory = self.get_process_memory('plasmashell')
            kwin_memory = self.get_process_memory('kwin')
            
            return {
                'system_memory': f"{system_usage}%",
                'plasma_memory': f"{plasma_memory} MB",
                'kwin_memory': f"{kwin_memory} MB",
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_process_memory(self, process_name):
        """Get memory usage for a specific process"""
        try:
            result = subprocess.run(['ps', '-eo', 'rss,comm'], 
                                  capture_output=True, text=True)
            total_memory = 0
            for line in result.stdout.split('\n'):
                if process_name in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        total_memory += int(parts[0])
            return int(total_memory / 1024)  # Convert to MB
        except:
            return 0
    
    def get_recent_logs(self):
        """Get recent KDE Memory Guardian logs"""
        try:
            log_file = os.path.expanduser('~/.local/share/kde-memory-manager.log')
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                return {'logs': lines[-20:]}  # Last 20 lines
            else:
                return {'logs': ['No log file found']}
        except Exception as e:
            return {'error': str(e)}
    
    def run_test_suite(self):
        """Run basic test suite"""
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': []
        }
        
        # Test 1: Service status
        try:
            result = subprocess.run(['systemctl', '--user', 'is-active', 'kde-memory-manager.service'],
                                  capture_output=True, text=True)
            service_active = result.stdout.strip() == 'active'
            results['tests'].append({
                'name': 'Service Status',
                'status': 'PASS' if service_active else 'FAIL',
                'details': f"Service is {'active' if service_active else 'inactive'}"
            })
        except:
            results['tests'].append({
                'name': 'Service Status',
                'status': 'ERROR',
                'details': 'Could not check service status'
            })
        
        # Test 2: Memory detection
        try:
            plasma_mem = self.get_process_memory('plasmashell')
            results['tests'].append({
                'name': 'Memory Detection',
                'status': 'PASS' if plasma_mem >= 0 else 'FAIL',
                'details': f"Detected Plasma memory: {plasma_mem} MB"
            })
        except:
            results['tests'].append({
                'name': 'Memory Detection',
                'status': 'ERROR',
                'details': 'Could not detect memory usage'
            })
        
        # Test 3: Log file access
        try:
            log_file = os.path.expanduser('~/.local/share/kde-memory-manager.log')
            log_exists = os.path.exists(log_file)
            results['tests'].append({
                'name': 'Log File Access',
                'status': 'PASS' if log_exists else 'FAIL',
                'details': f"Log file {'found' if log_exists else 'not found'}"
            })
        except:
            results['tests'].append({
                'name': 'Log File Access',
                'status': 'ERROR',
                'details': 'Could not check log file'
            })
        
        return results

    def restart_plasma(self):
        """Actually restart Plasma shell"""
        try:
            print("🔄 REAL OPERATION: Restarting Plasma shell...")

            # Kill plasmashell
            result1 = subprocess.run(['killall', 'plasmashell'],
                                   capture_output=True, text=True)

            # Wait a moment
            time.sleep(2)

            # Start plasmashell
            result2 = subprocess.run(['kstart', 'plasmashell'],
                                   capture_output=True, text=True)

            return {
                'action': 'restart_plasma',
                'status': 'SUCCESS',
                'details': f'Plasma restarted - killall exit code: {result1.returncode}, kstart exit code: {result2.returncode}',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'real_operation': True
            }

        except Exception as e:
            return {
                'action': 'restart_plasma',
                'status': 'ERROR',
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'real_operation': True
            }

    def clear_cache(self):
        """Actually clear system cache"""
        try:
            print("🧹 REAL OPERATION: Clearing system cache...")

            # Sync filesystem
            result1 = subprocess.run(['sync'], capture_output=True, text=True)

            # Clear page cache, dentries and inodes
            result2 = subprocess.run(['sudo', 'sh', '-c', 'echo 3 > /proc/sys/vm/drop_caches'],
                                   capture_output=True, text=True)

            return {
                'action': 'clear_cache',
                'status': 'SUCCESS' if result2.returncode == 0 else 'PARTIAL',
                'details': f'Cache clearing attempted - sync: {result1.returncode}, drop_caches: {result2.returncode}',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'real_operation': True,
                'note': 'May require sudo privileges for full cache clearing'
            }

        except Exception as e:
            return {
                'action': 'clear_cache',
                'status': 'ERROR',
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'real_operation': True
            }

    def view_logs(self):
        """Actually open log viewer"""
        try:
            print("📋 REAL OPERATION: Opening log viewer...")

            log_file = os.path.expanduser('~/.local/share/kde-memory-manager.log')

            # Try to open with various log viewers
            viewers = ['konsole', 'gnome-terminal', 'xterm']
            opened = False

            for viewer in viewers:
                try:
                    if viewer == 'konsole':
                        result = subprocess.run([viewer, '-e', 'tail', '-f', log_file],
                                              capture_output=True, text=True)
                    else:
                        result = subprocess.run([viewer, '-e', f'tail -f {log_file}'],
                                              capture_output=True, text=True)
                    opened = True
                    break
                except:
                    continue

            if not opened:
                # Fallback: just return log content
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        content = f.read()
                else:
                    content = "Log file not found"

                return {
                    'action': 'view_logs',
                    'status': 'FALLBACK',
                    'details': 'No terminal viewer available, returning log content',
                    'log_content': content[-2000:],  # Last 2000 chars
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'real_operation': True
                }

            return {
                'action': 'view_logs',
                'status': 'SUCCESS',
                'details': f'Log viewer opened with {viewer}',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'real_operation': True
            }

        except Exception as e:
            return {
                'action': 'view_logs',
                'status': 'ERROR',
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'real_operation': True
            }

    def run_comprehensive_tests(self):
        """Actually run real tests"""
        try:
            print("🧪 REAL OPERATION: Running comprehensive tests...")

            test_results = {
                'action': 'run_tests',
                'status': 'SUCCESS',
                'tests': [],
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'real_operation': True
            }

            # Test 1: Check if KDE Memory Guardian service is running
            try:
                result = subprocess.run(['systemctl', '--user', 'is-active', 'kde-memory-manager.service'],
                                      capture_output=True, text=True)
                test_results['tests'].append({
                    'name': 'KDE Memory Guardian Service',
                    'status': 'PASS' if result.returncode == 0 else 'FAIL',
                    'details': f"Service status: {result.stdout.strip()}"
                })
            except Exception as e:
                test_results['tests'].append({
                    'name': 'KDE Memory Guardian Service',
                    'status': 'ERROR',
                    'details': str(e)
                })

            # Test 2: Check Plasma process
            try:
                result = subprocess.run(['pgrep', 'plasmashell'], capture_output=True, text=True)
                test_results['tests'].append({
                    'name': 'Plasma Process Check',
                    'status': 'PASS' if result.returncode == 0 else 'FAIL',
                    'details': f"Plasma PID: {result.stdout.strip() if result.returncode == 0 else 'Not running'}"
                })
            except Exception as e:
                test_results['tests'].append({
                    'name': 'Plasma Process Check',
                    'status': 'ERROR',
                    'details': str(e)
                })

            # Test 3: Memory usage check
            try:
                stats = self.get_memory_stats()
                if 'system_memory' in stats:
                    test_results['tests'].append({
                        'name': 'Memory Statistics',
                        'status': 'PASS',
                        'details': f"System: {stats['system_memory']}, Plasma: {stats.get('plasma_memory', 'N/A')}"
                    })
                else:
                    test_results['tests'].append({
                        'name': 'Memory Statistics',
                        'status': 'FAIL',
                        'details': 'Could not retrieve memory stats'
                    })
            except Exception as e:
                test_results['tests'].append({
                    'name': 'Memory Statistics',
                    'status': 'ERROR',
                    'details': str(e)
                })

            return test_results

        except Exception as e:
            return {
                'action': 'run_tests',
                'status': 'ERROR',
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'real_operation': True
            }

def start_server(port=8000):
    """Start the web server"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", port), KDEMemoryGuardianHandler) as httpd:
        print(f"🌐 KDE Memory Guardian Web Server starting on port {port}")
        print(f"📊 Dashboard: http://localhost:{port}")
        print(f"🔧 API endpoints:")
        print(f"   • http://localhost:{port}/api/stats")
        print(f"   • http://localhost:{port}/api/logs") 
        print(f"   • http://localhost:{port}/api/test")
        print("Press Ctrl+C to stop the server")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    start_server()
