#!/usr/bin/env python3
"""
REAL KDE Memory Guardian - Performs Actual System Operations
No simulations, no placeholders - real functionality only
"""

import subprocess
import time
import os
import sys
import logging
from datetime import datetime

class RealKDEMemoryManager:
    def __init__(self):
        self.setup_logging()
        self.log("🚀 REAL KDE Memory Guardian initialized")
    
    def setup_logging(self):
        """Setup real logging to file"""
        log_dir = os.path.expanduser('~/.local/share')
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'real_kde_memory_manager.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message):
        """Log with timestamp"""
        self.logger.info(message)
    
    def get_process_memory(self, process_name):
        """Get actual memory usage for a process"""
        try:
            result = subprocess.run(['ps', '-eo', 'rss,comm'], 
                                  capture_output=True, text=True, check=True)
            total_memory = 0
            process_count = 0
            
            for line in result.stdout.split('\n'):
                if process_name in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        total_memory += int(parts[0])
                        process_count += 1
            
            memory_mb = total_memory // 1024
            self.log(f"📊 REAL: {process_name} using {memory_mb} MB ({process_count} processes)")
            return memory_mb
            
        except subprocess.CalledProcessError as e:
            self.log(f"❌ REAL: Error getting memory for {process_name}: {e}")
            return 0
        except Exception as e:
            self.log(f"❌ REAL: Unexpected error getting memory for {process_name}: {e}")
            return 0
    
    def get_system_memory_usage(self):
        """Get actual system memory usage"""
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            mem_total = 0
            mem_available = 0
            
            for line in meminfo.split('\n'):
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1])
                elif line.startswith('MemAvailable:'):
                    mem_available = int(line.split()[1])
            
            if mem_total > 0:
                usage_percent = int((1 - mem_available / mem_total) * 100)
                self.log(f"📊 REAL: System memory usage: {usage_percent}% ({mem_total//1024} MB total, {mem_available//1024} MB available)")
                return usage_percent
            else:
                self.log("❌ REAL: Could not determine system memory usage")
                return 0
                
        except Exception as e:
            self.log(f"❌ REAL: Error getting system memory: {e}")
            return 0
    
    def restart_plasma(self):
        """Actually restart Plasma shell"""
        try:
            self.log("🔄 REAL: Starting Plasma restart operation...")
            
            # Kill plasmashell
            self.log("🔄 REAL: Killing plasmashell...")
            result1 = subprocess.run(['killall', 'plasmashell'], 
                                   capture_output=True, text=True)
            self.log(f"🔄 REAL: killall plasmashell exit code: {result1.returncode}")
            
            # Wait for processes to terminate
            time.sleep(3)
            
            # Start plasmashell
            self.log("🔄 REAL: Starting plasmashell...")
            result2 = subprocess.run(['kstart', 'plasmashell'], 
                                   capture_output=True, text=True)
            self.log(f"🔄 REAL: kstart plasmashell exit code: {result2.returncode}")
            
            # Verify it's running
            time.sleep(2)
            verify_result = subprocess.run(['pgrep', 'plasmashell'], 
                                         capture_output=True, text=True)
            
            if verify_result.returncode == 0:
                pid = verify_result.stdout.strip()
                self.log(f"✅ REAL: Plasma restart successful - PID: {pid}")
                return True
            else:
                self.log("❌ REAL: Plasma restart failed - process not found after restart")
                return False
                
        except Exception as e:
            self.log(f"❌ REAL: Plasma restart error: {e}")
            return False
    
    def clear_system_cache(self):
        """Actually clear system cache"""
        try:
            self.log("🧹 REAL: Starting cache clearing operation...")
            
            # Sync filesystem
            self.log("🧹 REAL: Syncing filesystem...")
            result1 = subprocess.run(['sync'], capture_output=True, text=True)
            self.log(f"🧹 REAL: sync exit code: {result1.returncode}")
            
            # Clear page cache, dentries and inodes (requires sudo)
            self.log("🧹 REAL: Attempting to clear page cache...")
            try:
                result2 = subprocess.run(['sudo', 'sh', '-c', 'echo 3 > /proc/sys/vm/drop_caches'], 
                                       capture_output=True, text=True, timeout=10)
                self.log(f"🧹 REAL: drop_caches exit code: {result2.returncode}")
                
                if result2.returncode == 0:
                    self.log("✅ REAL: System cache cleared successfully")
                    return True
                else:
                    self.log(f"⚠️ REAL: Cache clearing partial - stderr: {result2.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                self.log("⚠️ REAL: Cache clearing timed out (may require sudo password)")
                return False
                
        except Exception as e:
            self.log(f"❌ REAL: Cache clearing error: {e}")
            return False
    
    def check_kde_processes(self):
        """Check status of KDE processes"""
        processes = ['plasmashell', 'kwin_x11', 'kwin_wayland', 'kglobalaccel5']
        status = {}
        
        for process in processes:
            try:
                result = subprocess.run(['pgrep', process], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    memory = self.get_process_memory(process)
                    status[process] = {
                        'running': True,
                        'pids': pids,
                        'memory_mb': memory
                    }
                    self.log(f"✅ REAL: {process} running - PIDs: {pids}, Memory: {memory} MB")
                else:
                    status[process] = {'running': False}
                    self.log(f"❌ REAL: {process} not running")
                    
            except Exception as e:
                status[process] = {'error': str(e)}
                self.log(f"❌ REAL: Error checking {process}: {e}")
        
        return status
    
    def run_memory_check(self):
        """Run comprehensive memory check"""
        self.log("🔍 REAL: Starting comprehensive memory check...")
        
        # System memory
        system_usage = self.get_system_memory_usage()
        
        # Process memory
        plasma_memory = self.get_process_memory('plasmashell')
        kwin_memory = self.get_process_memory('kwin')
        
        # Process status
        kde_status = self.check_kde_processes()
        
        # Memory thresholds (configurable)
        SYSTEM_THRESHOLD = 85  # 85%
        PLASMA_THRESHOLD = 1500  # 1.5GB
        KWIN_THRESHOLD = 800  # 800MB
        
        issues = []
        
        if system_usage > SYSTEM_THRESHOLD:
            issues.append(f"High system memory usage: {system_usage}%")
        
        if plasma_memory > PLASMA_THRESHOLD:
            issues.append(f"High Plasma memory usage: {plasma_memory} MB")
        
        if kwin_memory > KWIN_THRESHOLD:
            issues.append(f"High KWin memory usage: {kwin_memory} MB")
        
        if issues:
            self.log(f"⚠️ REAL: Memory issues detected: {', '.join(issues)}")
            return False
        else:
            self.log("✅ REAL: All memory usage within normal parameters")
            return True
    
    def run_maintenance(self):
        """Run maintenance operations"""
        self.log("🔧 REAL: Starting maintenance operations...")
        
        # Check memory first
        memory_ok = self.run_memory_check()
        
        if not memory_ok:
            self.log("🔧 REAL: Memory issues detected, running maintenance...")
            
            # Clear cache first
            cache_cleared = self.clear_system_cache()
            
            # Check if Plasma needs restart
            plasma_memory = self.get_process_memory('plasmashell')
            if plasma_memory > 1500:  # 1.5GB threshold
                self.log(f"🔧 REAL: Plasma using {plasma_memory} MB, restarting...")
                plasma_restarted = self.restart_plasma()
                
                if plasma_restarted:
                    # Check memory again after restart
                    time.sleep(5)
                    new_plasma_memory = self.get_process_memory('plasmashell')
                    self.log(f"🔧 REAL: Plasma memory after restart: {new_plasma_memory} MB")
        
        self.log("🔧 REAL: Maintenance operations completed")

def main():
    """Main function for command-line usage"""
    manager = RealKDEMemoryManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'check':
            manager.run_memory_check()
        elif command == 'restart-plasma':
            manager.restart_plasma()
        elif command == 'clear-cache':
            manager.clear_system_cache()
        elif command == 'maintenance':
            manager.run_maintenance()
        elif command == 'status':
            manager.check_kde_processes()
        else:
            print("Usage: real_kde_memory_manager.py [check|restart-plasma|clear-cache|maintenance|status]")
    else:
        # Default: run memory check
        manager.run_memory_check()

if __name__ == "__main__":
    main()
