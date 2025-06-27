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
