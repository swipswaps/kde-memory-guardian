#!/usr/bin/env python3
"""
🔍 Real System Log Capture - No Placeholders
Captures actual verbatim system and application event messages
"""

import subprocess
import json
import sqlite3
import re
from datetime import datetime, timedelta
import os

class RealSystemLogCapture:
    def __init__(self, db_path="real_system_logs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database for real system logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Real system event messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                hostname TEXT,
                service TEXT,
                pid INTEGER,
                message TEXT NOT NULL,
                severity TEXT,
                source_command TEXT,
                raw_line TEXT NOT NULL,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Real application error messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                application TEXT,
                pid INTEGER,
                error_type TEXT,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                signal_number INTEGER,
                exit_code INTEGER,
                raw_line TEXT NOT NULL,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Kernel messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kernel_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                subsystem TEXT,
                message TEXT NOT NULL,
                severity TEXT,
                raw_line TEXT NOT NULL,
                captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Real system log database initialized")
    
    def capture_journalctl_logs(self, hours=24):
        """Capture real journalctl logs - verbatim"""
        print(f"🔍 Capturing journalctl logs from last {hours} hours...")
        
        try:
            # Get system logs
            cmd = ['journalctl', '--since', f'{hours} hours ago', '--no-pager', '-o', 'short-iso']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print(f"📥 Captured {len(lines)} journalctl lines")
                return lines
            else:
                print(f"❌ journalctl failed: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print("⏰ journalctl timeout - using alternative method")
            return self.capture_dmesg_logs()
        except Exception as e:
            print(f"❌ journalctl error: {e}")
            return []
    
    def capture_dmesg_logs(self):
        """Capture real dmesg logs as fallback"""
        print("🔍 Capturing dmesg logs...")
        
        try:
            result = subprocess.run(['dmesg', '-T'], capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print(f"📥 Captured {len(lines)} dmesg lines")
                return lines
            else:
                print(f"❌ dmesg failed: {result.stderr}")
                return []
        except Exception as e:
            print(f"❌ dmesg error: {e}")
            return []
    
    def capture_vscode_specific_logs(self):
        """Capture VSCode-specific logs"""
        print("🔍 Capturing VSCode-specific logs...")
        
        vscode_logs = []
        
        # Check journalctl for VSCode
        try:
            cmd = ['journalctl', '_COMM=code-insiders', '--since', '7 days ago', '--no-pager']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                vscode_logs.extend(lines)
                print(f"📥 Captured {len(lines)} VSCode journalctl entries")
        except Exception as e:
            print(f"❌ VSCode journalctl error: {e}")
        
        # Check audit logs for VSCode
        try:
            cmd = ['journalctl', '_TRANSPORT=audit', '--grep=code-insiders', '--since', '7 days ago', '--no-pager']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                vscode_logs.extend(lines)
                print(f"📥 Captured {len(lines)} VSCode audit entries")
        except Exception as e:
            print(f"❌ VSCode audit error: {e}")
        
        return vscode_logs
    
    def parse_system_log_line(self, line):
        """Parse real system log line - no placeholders"""
        if not line.strip() or line.startswith('--'):
            return None
        
        # Parse journalctl format: timestamp hostname service[pid]: message
        # Example: 2025-06-26T18:30:15+0000 fedora systemd[1]: Started some service
        
        patterns = [
            # ISO timestamp format
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{4})\s+(\S+)\s+(\S+?)(?:\[(\d+)\])?\s*:\s*(.+)$',
            # Standard syslog format  
            r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+?)(?:\[(\d+)\])?\s*:\s*(.+)$',
            # Audit format
            r'^.*audit\[(\d+)\]:\s*(.+)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                if len(match.groups()) == 5:
                    timestamp, hostname, service, pid, message = match.groups()
                    return {
                        'timestamp': timestamp,
                        'hostname': hostname,
                        'service': service,
                        'pid': int(pid) if pid else None,
                        'message': message,
                        'raw_line': line
                    }
                elif len(match.groups()) == 2:  # Audit format
                    pid, message = match.groups()
                    return {
                        'timestamp': 'unknown',
                        'hostname': 'unknown',
                        'service': 'audit',
                        'pid': int(pid) if pid else None,
                        'message': message,
                        'raw_line': line
                    }
        
        # If no pattern matches, store as raw
        return {
            'timestamp': 'unknown',
            'hostname': 'unknown', 
            'service': 'unknown',
            'pid': None,
            'message': line.strip(),
            'raw_line': line
        }
    
    def store_real_logs(self, log_lines):
        """Store real log lines in database - verbatim"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        system_count = 0
        app_count = 0
        kernel_count = 0
        
        for line in log_lines:
            parsed = self.parse_system_log_line(line)
            if not parsed:
                continue
            
            # Categorize and store
            if 'kernel' in parsed['service'].lower() or 'dmesg' in line:
                cursor.execute('''
                    INSERT INTO kernel_messages 
                    (timestamp, subsystem, message, raw_line)
                    VALUES (?, ?, ?, ?)
                ''', (
                    parsed['timestamp'],
                    parsed['service'],
                    parsed['message'],
                    parsed['raw_line']
                ))
                kernel_count += 1
                
            elif any(app in parsed['message'].lower() for app in ['code-insiders', 'vscode', 'anom_abend', 'sig=']):
                # Extract signal info if present
                signal_match = re.search(r'sig=(\d+)', parsed['message'])
                signal_num = int(signal_match.group(1)) if signal_match else None
                
                cursor.execute('''
                    INSERT INTO application_errors
                    (timestamp, application, pid, error_message, signal_number, raw_line)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    parsed['timestamp'],
                    'code-insiders' if 'code-insiders' in parsed['message'] else 'unknown',
                    parsed['pid'],
                    parsed['message'],
                    signal_num,
                    parsed['raw_line']
                ))
                app_count += 1
                
            else:
                cursor.execute('''
                    INSERT INTO system_events
                    (timestamp, hostname, service, pid, message, raw_line)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    parsed['timestamp'],
                    parsed['hostname'],
                    parsed['service'],
                    parsed['pid'],
                    parsed['message'],
                    parsed['raw_line']
                ))
                system_count += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Stored {system_count} system events, {app_count} app errors, {kernel_count} kernel messages")
        return system_count + app_count + kernel_count
    
    def get_verbatim_logs(self, limit=50):
        """Get verbatim system logs for display"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent system events
        cursor.execute('''
            SELECT timestamp, service, pid, message, raw_line, captured_at
            FROM system_events 
            ORDER BY captured_at DESC 
            LIMIT ?
        ''', (limit,))
        system_events = cursor.fetchall()
        
        # Get application errors
        cursor.execute('''
            SELECT timestamp, application, pid, error_message, signal_number, raw_line, captured_at
            FROM application_errors 
            ORDER BY captured_at DESC 
            LIMIT ?
        ''', (limit,))
        app_errors = cursor.fetchall()
        
        # Get kernel messages
        cursor.execute('''
            SELECT timestamp, subsystem, message, raw_line, captured_at
            FROM kernel_messages 
            ORDER BY captured_at DESC 
            LIMIT ?
        ''', (limit,))
        kernel_messages = cursor.fetchall()
        
        conn.close()
        
        return {
            'system_events': system_events,
            'application_errors': app_errors,
            'kernel_messages': kernel_messages
        }
    
    def capture_and_store_all(self):
        """Capture and store all real system logs"""
        print("🔄 Starting real system log capture...")
        
        # Capture journalctl logs
        journal_logs = self.capture_journalctl_logs(24)
        
        # Capture VSCode-specific logs
        vscode_logs = self.capture_vscode_specific_logs()
        
        # Combine all logs
        all_logs = journal_logs + vscode_logs
        
        if all_logs:
            total_stored = self.store_real_logs(all_logs)
            print(f"✅ Captured and stored {total_stored} real log entries")
            return total_stored
        else:
            print("❌ No logs captured")
            return 0
    
    def get_stats(self):
        """Get real statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM system_events')
        stats['system_events'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM application_errors')
        stats['application_errors'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM kernel_messages')
        stats['kernel_messages'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM application_errors WHERE signal_number IS NOT NULL')
        stats['signal_errors'] = cursor.fetchone()[0]
        
        conn.close()
        return stats

if __name__ == "__main__":
    # Test real log capture
    capture = RealSystemLogCapture()
    capture.capture_and_store_all()
    
    # Show stats
    stats = capture.get_stats()
    print("\n📊 REAL LOG STATISTICS:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Show sample verbatim logs
    logs = capture.get_verbatim_logs(5)
    print("\n📋 SAMPLE VERBATIM LOGS:")
    
    if logs['application_errors']:
        print("Application Errors:")
        for log in logs['application_errors'][:3]:
            print(f"  {log[5]}")  # raw_line
    
    if logs['system_events']:
        print("System Events:")
        for log in logs['system_events'][:3]:
            print(f"  {log[4]}")  # raw_line
