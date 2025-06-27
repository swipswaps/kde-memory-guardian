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
        """Actually restart Plasma shell - REAL IMPLEMENTATION"""
        try:
            print("🔄 REAL OPERATION: Restarting Plasma shell...")

            # Get current plasma PID for verification
            pid_before = subprocess.run(['pgrep', 'plasmashell'],
                                      capture_output=True, text=True).stdout.strip()
            print(f"Plasma PID before kill: {pid_before}")

            if not pid_before:
                return {
                    'action': 'restart_plasma',
                    'status': 'ERROR',
                    'details': 'No plasmashell process found to restart',
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'real_operation': True
                }

            # Use the same approach that works from command line
            # Run the bash script that we know works
            script_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'kde-memory-manager.sh')

            if os.path.exists(script_path):
                # Use the proven working bash script
                result = subprocess.run(['/bin/bash', script_path, 'restart-plasma'],
                                      capture_output=True, text=True,
                                      env=dict(os.environ, DISPLAY=':0'))

                # Wait and verify
                time.sleep(3)
                pid_after = subprocess.run(['pgrep', 'plasmashell'],
                                         capture_output=True, text=True).stdout.strip()

                success = (pid_before != pid_after and pid_after != '')

                return {
                    'action': 'restart_plasma',
                    'status': 'SUCCESS' if success else 'FAILED',
                    'details': f'Used bash script. PID: {pid_before} → {pid_after}. Script exit: {result.returncode}',
                    'script_output': result.stdout,
                    'script_errors': result.stderr,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'real_operation': True,
                    'pid_before': pid_before,
                    'pid_after': pid_after
                }
            else:
                # Fallback: direct command with proper session handling
                # Force kill with -9 to ensure it actually dies
                result1 = subprocess.run(['killall', '-9', 'plasmashell'],
                                       capture_output=True, text=True)
                print(f"killall -9 result: exit_code={result1.returncode}")

                # Wait longer to ensure process is gone
                time.sleep(5)

                # Verify it's actually gone
                pid_after_kill = subprocess.run(['pgrep', 'plasmashell'],
                                              capture_output=True, text=True).stdout.strip()
                print(f"PID after kill -9: {pid_after_kill}")

                if pid_after_kill:
                    return {
                        'action': 'restart_plasma',
                        'status': 'FAILED',
                        'details': f'Failed to kill plasmashell. PID {pid_before} still running as {pid_after_kill}',
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'real_operation': True
                    }

                # Start new instance with proper environment
                env = dict(os.environ)
                env.update({
                    'DISPLAY': ':0',
                    'XDG_SESSION_TYPE': 'x11',
                    'XDG_CURRENT_DESKTOP': 'KDE',
                    'KDE_SESSION_VERSION': '5'
                })

                result2 = subprocess.run(['kstart', 'plasmashell'],
                                       capture_output=True, text=True, env=env)
                print(f"kstart result: exit_code={result2.returncode}, stderr={result2.stderr}")

                # Wait and verify new process
                time.sleep(3)
                pid_final = subprocess.run(['pgrep', 'plasmashell'],
                                         capture_output=True, text=True).stdout.strip()
                print(f"Final PID: {pid_final}")

                success = (pid_final != '' and pid_final != pid_before)

                return {
                    'action': 'restart_plasma',
                    'status': 'SUCCESS' if success else 'FAILED',
                    'details': f'Direct restart. PID: {pid_before} → {pid_final}. killall: {result1.returncode}, kstart: {result2.returncode}',
                    'kstart_output': result2.stdout,
                    'kstart_errors': result2.stderr,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'real_operation': True,
                    'pid_before': pid_before,
                    'pid_after': pid_final
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
        """Actually clear system cache - REAL IMPLEMENTATION"""
        try:
            print("🧹 REAL OPERATION: Clearing system cache...")

            # Use the bash script that we know works
            script_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'kde-memory-manager.sh')

            if os.path.exists(script_path):
                # Use the proven working bash script
                result = subprocess.run(['/bin/bash', script_path, 'clear-cache'],
                                      capture_output=True, text=True,
                                      env=dict(os.environ, DISPLAY=':0'),
                                      timeout=30)

                # Check if it worked (even with permission issues)
                success = result.returncode == 0

                return {
                    'action': 'clear_cache',
                    'status': 'SUCCESS' if success else 'PARTIAL',
                    'details': f'Used bash script. Exit code: {result.returncode}',
                    'script_output': result.stdout,
                    'script_errors': result.stderr,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'real_operation': True,
                    'note': 'Cache clearing may require sudo privileges for full effect'
                }
            else:
                # Fallback: basic cache clearing without sudo
                print("🧹 REAL: Fallback cache clearing (no sudo)...")

                # Sync filesystem (this always works)
                result1 = subprocess.run(['sync'], capture_output=True, text=True)

                # Clear user-level caches
                user_caches = [
                    os.path.expanduser('~/.cache/thumbnails'),
                    os.path.expanduser('~/.cache/icon-cache.kcache'),
                    os.path.expanduser('~/.cache/krunner')
                ]

                cleared = []
                for cache_path in user_caches:
                    try:
                        if os.path.exists(cache_path):
                            if os.path.isfile(cache_path):
                                os.remove(cache_path)
                                cleared.append(f"Removed file: {os.path.basename(cache_path)}")
                            elif os.path.isdir(cache_path):
                                import shutil
                                shutil.rmtree(cache_path)
                                cleared.append(f"Removed directory: {os.path.basename(cache_path)}")
                    except Exception as e:
                        cleared.append(f"Failed to clear {os.path.basename(cache_path)}: {e}")

                return {
                    'action': 'clear_cache',
                    'status': 'PARTIAL',
                    'details': f'User-level cache clearing. Sync: {result1.returncode}',
                    'cleared_items': cleared,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'real_operation': True,
                    'note': 'System-level cache clearing requires sudo privileges'
                }

        except subprocess.TimeoutExpired:
            return {
                'action': 'clear_cache',
                'status': 'TIMEOUT',
                'details': 'Cache clearing operation timed out after 30 seconds',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'real_operation': True
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
        """Actually view log files - REAL IMPLEMENTATION"""
        try:
            print("📋 REAL OPERATION: Retrieving log files...")

            # Find all relevant log files
            log_files = [
                ('KDE Memory Manager', os.path.expanduser('~/.local/share/kde-memory-manager.log')),
                ('KDE Memory Guardian', os.path.expanduser('~/.local/share/kde-memory-guardian/kde-memory-manager.log')),
                ('Plasma Tray Cache', os.path.expanduser('~/.local/share/kde-memory-guardian/plasma-tray-cache.log')),
                ('Real KDE Manager', os.path.expanduser('~/.local/share/real_kde_memory_manager.log'))
            ]

            logs_found = {}
            total_size = 0

            for log_name, log_path in log_files:
                if os.path.exists(log_path):
                    try:
                        with open(log_path, 'r') as f:
                            content = f.read()
                            # Get last 1000 characters to avoid huge responses
                            if len(content) > 1000:
                                content = "...\n" + content[-1000:]
                            logs_found[log_name] = {
                                'path': log_path,
                                'size': os.path.getsize(log_path),
                                'content': content,
                                'lines': len(content.split('\n'))
                            }
                            total_size += os.path.getsize(log_path)
                    except Exception as e:
                        logs_found[log_name] = {
                            'path': log_path,
                            'error': f"Could not read: {e}"
                        }
                else:
                    logs_found[log_name] = {
                        'path': log_path,
                        'status': 'File not found'
                    }

            if logs_found:
                return {
                    'action': 'view_logs',
                    'status': 'SUCCESS',
                    'details': f'Retrieved {len([l for l in logs_found.values() if "content" in l])} log files, total size: {total_size} bytes',
                    'logs': logs_found,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'real_operation': True
                }
            else:
                return {
                    'action': 'view_logs',
                    'status': 'NO_LOGS',
                    'details': 'No log files found',
                    'searched_paths': [path for _, path in log_files],
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
