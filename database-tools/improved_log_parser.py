#!/usr/bin/env python3
"""
🔧 Improved Log Parser - Based on Best Practices from lnav and log-viewer
Fixes timestamp parsing and data display issues
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ImprovedLogParser:
    """
    Log parser based on best practices from lnav and sevdokimov/log-viewer
    Properly extracts timestamps, services, and structured data
    """
    
    def __init__(self):
        # Timestamp patterns based on lnav's format detection
        self.timestamp_patterns = [
            # ISO 8601 format: 2025-06-26T11:09:12-04:00
            (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})', '%Y-%m-%dT%H:%M:%S%z'),
            # ISO 8601 without timezone: 2025-06-26T11:09:12
            (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', '%Y-%m-%dT%H:%M:%S'),
            # Syslog format: Jun 26 11:09:12
            (r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),
            # RFC3339: 2025-06-26 11:09:12
            (r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', '%Y-%m-%d %H:%M:%S'),
        ]
        
        # Service/application patterns
        self.service_patterns = [
            # systemd journal: service[pid]:
            r'(\w+)\[(\d+)\]:',
            # audit logs: audit[pid]:
            r'(audit)\[(\d+)\]:',
            # kernel messages
            r'(kernel):',
            # sudo messages
            r'(sudo)\[(\d+)\]:',
        ]
        
        # Log level patterns
        self.level_patterns = [
            r'\b(EMERGENCY|ALERT|CRITICAL|ERROR|WARNING|NOTICE|INFO|DEBUG)\b',
            r'\b(FATAL|WARN|TRACE)\b',
            r'\b(sig=\d+)\b',  # Signal numbers as severity indicators
        ]
    
    def extract_timestamp(self, line: str) -> Tuple[Optional[datetime], str]:
        """
        Extract timestamp from log line using multiple patterns
        Returns (datetime_obj, remaining_line)
        """
        for pattern, fmt in self.timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                try:
                    # Handle timezone-aware parsing
                    if '%z' in fmt:
                        dt = datetime.strptime(timestamp_str, fmt)
                    else:
                        dt = datetime.strptime(timestamp_str, fmt)
                        # Add current year if not present
                        if dt.year == 1900:
                            dt = dt.replace(year=datetime.now().year)
                    
                    # Remove timestamp from line
                    remaining = line[match.end():].strip()
                    return dt, remaining
                except ValueError:
                    continue
        
        return None, line
    
    def extract_service_info(self, line: str) -> Tuple[Optional[str], Optional[int], str]:
        """
        Extract service name and PID from log line
        Returns (service_name, pid, remaining_line)
        """
        for pattern in self.service_patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                service = groups[0]
                pid = int(groups[1]) if len(groups) > 1 and groups[1] else None
                remaining = line[match.end():].strip()
                return service, pid, remaining
        
        return None, None, line
    
    def extract_hostname(self, line: str) -> Tuple[Optional[str], str]:
        """
        Extract hostname from log line
        Returns (hostname, remaining_line)
        """
        # Pattern: timestamp hostname service[pid]: message
        # Look for hostname after timestamp
        parts = line.split()
        if len(parts) >= 2:
            # Second part is likely hostname
            potential_hostname = parts[1]
            if not re.match(r'^\d', potential_hostname):  # Not starting with digit
                remaining = ' '.join(parts[2:])
                return potential_hostname, remaining
        
        return None, line
    
    def extract_log_level(self, line: str) -> Optional[str]:
        """Extract log level/severity from line"""
        for pattern in self.level_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        # Check for signal numbers
        if 'sig=' in line:
            return 'SIGNAL'
        
        # Check for ANOM_ABEND (abnormal end)
        if 'ANOM_ABEND' in line:
            return 'CRITICAL'
        
        return 'INFO'  # Default level
    
    def parse_structured_data(self, line: str) -> Dict:
        """
        Parse structured data from log line (JSON, key=value pairs, etc.)
        """
        structured = {}
        
        # Extract key=value pairs
        kv_pattern = r'(\w+)=([^\s]+)'
        for match in re.finditer(kv_pattern, line):
            key, value = match.groups()
            # Remove quotes if present
            value = value.strip('"\'')
            structured[key] = value
        
        # Extract signal information
        if 'sig=' in line:
            sig_match = re.search(r'sig=(\d+)', line)
            if sig_match:
                structured['signal_number'] = int(sig_match.group(1))
                structured['signal_name'] = self.get_signal_name(int(sig_match.group(1)))
        
        # Extract process information
        if 'pid=' in line:
            pid_match = re.search(r'pid=(\d+)', line)
            if pid_match:
                structured['process_id'] = int(pid_match.group(1))
        
        # Extract command information
        if 'comm=' in line:
            comm_match = re.search(r'comm="([^"]+)"', line)
            if comm_match:
                structured['command'] = comm_match.group(1)
        
        return structured
    
    def get_signal_name(self, signal_num: int) -> str:
        """Convert signal number to name"""
        signal_names = {
            1: 'SIGHUP', 2: 'SIGINT', 3: 'SIGQUIT', 4: 'SIGILL',
            5: 'SIGTRAP', 6: 'SIGABRT', 7: 'SIGBUS', 8: 'SIGFPE',
            9: 'SIGKILL', 10: 'SIGUSR1', 11: 'SIGSEGV', 12: 'SIGUSR2',
            13: 'SIGPIPE', 14: 'SIGALRM', 15: 'SIGTERM'
        }
        return signal_names.get(signal_num, f'SIG{signal_num}')
    
    def parse_log_line(self, raw_line: str) -> Dict:
        """
        Parse a complete log line into structured components
        Based on best practices from lnav and log-viewer
        """
        original_line = raw_line.strip()
        working_line = original_line
        
        # Extract timestamp
        timestamp, working_line = self.extract_timestamp(working_line)
        
        # Extract hostname
        hostname, working_line = self.extract_hostname(working_line)
        
        # Extract service and PID
        service, pid, working_line = self.extract_service_info(working_line)
        
        # Extract log level
        log_level = self.extract_log_level(original_line)
        
        # Parse structured data
        structured_data = self.parse_structured_data(original_line)
        
        # Remaining text is the message
        message = working_line.strip()
        
        return {
            'timestamp': timestamp.isoformat() if timestamp else 'unknown',
            'timestamp_obj': timestamp,
            'hostname': hostname or 'unknown',
            'service': service or 'unknown',
            'pid': pid,
            'log_level': log_level,
            'message': message,
            'structured_data': structured_data,
            'raw_line': original_line
        }
    
    def categorize_log_entry(self, parsed_entry: Dict) -> Dict:
        """
        Categorize log entry based on content analysis
        Similar to lnav's automatic categorization
        """
        categories = []
        tags = []
        
        # System categories
        if parsed_entry['service'] in ['systemd', 'kernel', 'audit']:
            categories.append('system')
        
        # Application categories
        if 'code-insiders' in parsed_entry['raw_line']:
            categories.append('application')
            tags.append('vscode')
        
        # Security categories
        if parsed_entry['service'] == 'audit' or 'ANOM_ABEND' in parsed_entry['raw_line']:
            categories.append('security')
            tags.append('audit')
        
        # Error categories
        if parsed_entry['log_level'] in ['CRITICAL', 'ERROR', 'SIGNAL']:
            categories.append('error')
        
        # Memory/crash categories
        if any(term in parsed_entry['raw_line'].lower() for term in ['sig=', 'segfault', 'oom', 'memory']):
            categories.append('crash')
            tags.append('memory')
        
        return {
            'categories': categories,
            'tags': tags,
            'primary_category': categories[0] if categories else 'general'
        }

def test_improved_parser():
    """Test the improved parser with real log samples"""
    parser = ImprovedLogParser()
    
    # Test samples from actual system logs
    test_logs = [
        "2025-06-26T11:09:12-04:00 fedora audit[17314]: USER_CMD pid=17314 uid=1000 auid=1000 ses=3 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='cwd=\"/home/owner/Documents/6854a1da-e23c-8008-a9fc-76b7fa3c1f92/kde-memory-guardian/testing\" cmd=\"dmesg\" exe=\"/usr/bin/sudo\" terminal=pts/5 res=failed'",
        "2025-06-26T09:19:02-04:00 fedora audit[1909]: ANOM_ABEND auid=1000 uid=1000 gid=1000 ses=3 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 pid=1909 comm=\"xdg-desktop-por\" exe=\"/usr/libexec/xdg-desktop-portal-kde\" sig=6 res=1",
        "2025-06-26T09:13:26-04:00 fedora kernel: amdgpu 0000:04:00.0: amdgpu: GART: 1024M 0x0000000000000000 - 0x000000003FFFFFFF"
    ]
    
    print("🧪 TESTING IMPROVED LOG PARSER:")
    print("=" * 50)
    
    for i, log_line in enumerate(test_logs, 1):
        print(f"\n{i}. PARSING: {log_line[:80]}...")
        parsed = parser.parse_log_line(log_line)
        categorized = parser.categorize_log_entry(parsed)
        
        print(f"   Timestamp: {parsed['timestamp']}")
        print(f"   Hostname: {parsed['hostname']}")
        print(f"   Service: {parsed['service']}")
        print(f"   PID: {parsed['pid']}")
        print(f"   Level: {parsed['log_level']}")
        print(f"   Categories: {categorized['categories']}")
        print(f"   Structured Data: {parsed['structured_data']}")

if __name__ == "__main__":
    test_improved_parser()
