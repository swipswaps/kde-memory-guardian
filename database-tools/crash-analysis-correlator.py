#!/usr/bin/env python3
"""
💥 Crash Analysis Correlator
Advanced crash analysis and correlation with system events
Specifically designed for VSCode crashes and system instability

Features:
- Crash data analysis and parsing
- Timeline correlation with clipboard data
- Predictive crash detection
- Automated crash recovery
- System hardening recommendations
"""

from flask import Flask, render_template_string, jsonify, request
import sqlite3
import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

# Import enhanced components
try:
    from vscode_issues_solutions_database import VSCodeIssuesSolutionsDatabase
    SOLUTIONS_DB_AVAILABLE = True
except ImportError:
    SOLUTIONS_DB_AVAILABLE = False
    print("⚠️ VSCode Solutions Database not available")

try:
    from performance_optimizer import PerformanceOptimizer
    PERFORMANCE_OPTIMIZER_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZER_AVAILABLE = False
    print("⚠️ Performance Optimizer not available")

try:
    from intelligent_ranking import IntelligentRanking
    INTELLIGENT_RANKING_AVAILABLE = True
except ImportError:
    INTELLIGENT_RANKING_AVAILABLE = False
    print("⚠️ Intelligent Ranking not available")

app = Flask(__name__)

# Configuration
CLIPBOARD_DB = Path.home() / '.local/share/clipboard_daemon/clipboard.sqlite'

class CrashAnalysisCorrelator:
    def __init__(self):
        self.crash_events = []
        self.correlations = []

        # Initialize enhanced components
        if SOLUTIONS_DB_AVAILABLE:
            try:
                self.solutions_db = VSCodeIssuesSolutionsDatabase()
                print("✅ VSCode Solutions Database initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize Solutions Database: {e}")
                self.solutions_db = None
        else:
            self.solutions_db = None

        # Initialize Performance Optimizer
        if PERFORMANCE_OPTIMIZER_AVAILABLE:
            try:
                self.performance_optimizer = PerformanceOptimizer()
                print("✅ Performance Optimizer initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize Performance Optimizer: {e}")
                self.performance_optimizer = None
        else:
            self.performance_optimizer = None

        # Initialize Intelligent Ranking
        if INTELLIGENT_RANKING_AVAILABLE:
            try:
                self.intelligent_ranking = IntelligentRanking()
                print("✅ Intelligent Ranking initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize Intelligent Ranking: {e}")
                self.intelligent_ranking = None
        else:
            self.intelligent_ranking = None
        
    def analyze_vscode_crash_file(self, crash_file_path):
        """Analyze VSCode crash file with verbose data and system correlation"""
        try:
            if not os.path.exists(crash_file_path):
                return {'error': f'Crash file not found: {crash_file_path}'}

            with open(crash_file_path, 'r') as f:
                crash_data = f.read()

            # Get system logs around crash time
            system_logs = self._get_system_logs_around_crash()
            error_logs = self._get_error_logs_around_crash()
            application_logs = self._get_application_logs_around_crash()

            analysis = {
                'timestamp': datetime.now().isoformat(),
                'file_path': crash_file_path,
                'file_size': len(crash_data),
                'raw_crash_data': crash_data[:2000] + '...' if len(crash_data) > 2000 else crash_data,
                'crash_type': self._identify_crash_type(crash_data),
                'memory_info': self._extract_memory_info(crash_data),
                'cpu_info': self._extract_cpu_info(crash_data),
                'stack_trace': self._extract_stack_trace(crash_data),
                'extensions': self._extract_extensions_info(crash_data),
                'system_info': self._extract_system_info(crash_data),
                'system_logs': system_logs,
                'error_logs': error_logs,
                'application_logs': application_logs,
                'kernel_messages': self._get_kernel_messages(),
                'memory_pressure_data': self._get_memory_pressure_data(),
                'process_state': self._get_process_state_at_crash(),
                'root_cause': self._determine_root_cause(crash_data),
                'severity': self._assess_severity(crash_data),
                'evidence': self._compile_evidence(crash_data, system_logs, error_logs),
                'recommendations': self._generate_crash_recommendations(crash_data)
            }

            # Integrate sudo-collected data if available
            analysis = self._integrate_sudo_data(analysis)

            # Store crash event
            self.crash_events.append(analysis)

            return analysis

        except Exception as e:
            return {'error': f'Error analyzing crash file: {e}'}
    
    def _identify_crash_type(self, crash_data):
        """Identify crash type using evidence-based analysis"""
        crash_data_lower = crash_data.lower()

        # Get current memory pressure for evidence
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()

            memory_data = {}
            for line in meminfo.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    memory_data[key.strip()] = value.strip()

            total_mem = int(memory_data.get('MemTotal', '0').split()[0])
            available_mem = int(memory_data.get('MemAvailable', '0').split()[0])

            if total_mem > 0:
                memory_usage_percent = ((total_mem - available_mem) / total_mem) * 100
            else:
                memory_usage_percent = 0
        except:
            memory_usage_percent = 0

        # Evidence-based crash type detection
        if 'out of memory' in crash_data_lower or 'oom' in crash_data_lower:
            return 'memory_exhaustion'
        elif memory_usage_percent > 70:
            # High memory usage suggests memory exhaustion even without explicit OOM
            return 'memory_exhaustion'
        elif 'segmentation fault' in crash_data_lower or 'segfault' in crash_data_lower:
            return 'segmentation_fault'
        elif 'gpu' in crash_data_lower or 'graphics' in crash_data_lower or 'webgl' in crash_data_lower:
            return 'gpu_driver_crash'
        elif 'extension' in crash_data_lower and 'error' in crash_data_lower:
            return 'extension_error'
        elif 'timeout' in crash_data_lower:
            return 'timeout_related'
        elif 'renderer' in crash_data_lower or 'process' in crash_data_lower:
            return 'process_crash'
        else:
            # Default to memory exhaustion if high memory usage detected
            if memory_usage_percent > 60:
                return 'memory_exhaustion'
            return 'unknown'
    
    def _extract_memory_info(self, crash_data):
        """Extract memory usage information"""
        memory_info = {}
        
        # Look for memory patterns
        memory_patterns = [
            r'memory[:\s]+(\d+(?:\.\d+)?)\s*(mb|gb|kb)',
            r'rss[:\s]+(\d+)',
            r'heap[:\s]+(\d+(?:\.\d+)?)\s*(mb|gb|kb)',
            r'used[:\s]+(\d+(?:\.\d+)?)\s*(mb|gb|kb)'
        ]
        
        for pattern in memory_patterns:
            matches = re.findall(pattern, crash_data.lower())
            if matches:
                memory_info['found_memory_data'] = matches
                break
        
        return memory_info
    
    def _extract_cpu_info(self, crash_data):
        """Extract CPU usage information"""
        cpu_info = {}
        
        cpu_patterns = [
            r'cpu[:\s]+(\d+(?:\.\d+)?)\s*%',
            r'load[:\s]+(\d+(?:\.\d+)?)',
            r'usage[:\s]+(\d+(?:\.\d+)?)\s*%'
        ]
        
        for pattern in cpu_patterns:
            matches = re.findall(pattern, crash_data.lower())
            if matches:
                cpu_info['found_cpu_data'] = matches
                break
        
        return cpu_info
    
    def _extract_stack_trace(self, crash_data):
        """Extract stack trace information"""
        stack_info = {}
        
        # Look for common stack trace patterns
        if 'stack trace' in crash_data.lower() or 'backtrace' in crash_data.lower():
            lines = crash_data.split('\n')
            stack_lines = []
            in_stack = False
            
            for line in lines:
                if 'stack' in line.lower() or 'backtrace' in line.lower():
                    in_stack = True
                    continue
                
                if in_stack and (line.strip().startswith('#') or 'at ' in line):
                    stack_lines.append(line.strip())
                elif in_stack and not line.strip():
                    break
            
            stack_info['stack_trace'] = stack_lines[:10]  # First 10 lines
        
        return stack_info
    
    def _extract_extensions_info(self, crash_data):
        """Extract VSCode extensions information"""
        extensions_info = {}
        
        # Look for extension-related information
        if 'extension' in crash_data.lower():
            extension_patterns = [
                r'extension[:\s]+([a-zA-Z0-9\-\.]+)',
                r'([a-zA-Z0-9\-\.]+)\.vscode-extension',
                r'extensions[/\\]([a-zA-Z0-9\-\.]+)'
            ]
            
            for pattern in extension_patterns:
                matches = re.findall(pattern, crash_data)
                if matches:
                    extensions_info['found_extensions'] = list(set(matches))
                    break
        
        return extensions_info
    
    def _extract_system_info(self, crash_data):
        """Extract system information"""
        system_info = {}
        
        # Look for system information
        system_patterns = [
            r'os[:\s]+([^\n]+)',
            r'kernel[:\s]+([^\n]+)',
            r'arch[:\s]+([^\n]+)',
            r'version[:\s]+([^\n]+)'
        ]
        
        for pattern in system_patterns:
            matches = re.findall(pattern, crash_data.lower())
            if matches:
                system_info['system_data'] = matches
                break
        
        return system_info
    
    def _determine_root_cause(self, crash_data):
        """Determine the root cause of the crash"""
        crash_type = self._identify_crash_type(crash_data)
        
        root_causes = {
            'memory_exhaustion': 'VSCode consumed too much memory, likely due to large files or memory leaks',
            'segmentation_fault': 'Memory access violation, possibly due to corrupted data or faulty extension',
            'graphics_related': 'GPU/graphics driver issue, common with AMD drivers on Linux',
            'extension_related': 'Problematic VSCode extension causing instability',
            'timeout_related': 'Operation timeout, possibly due to system overload',
            'unknown': 'Unable to determine specific cause from available data'
        }
        
        return root_causes.get(crash_type, 'Unknown crash type')
    
    def _assess_severity(self, crash_data):
        """Assess crash severity using evidence-based analysis"""
        crash_data_lower = crash_data.lower()

        # Get current system state for evidence-based assessment
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()

            memory_data = {}
            for line in meminfo.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    memory_data[key.strip()] = value.strip()

            total_mem = int(memory_data.get('MemTotal', '0').split()[0])
            available_mem = int(memory_data.get('MemAvailable', '0').split()[0])

            if total_mem > 0:
                memory_usage_percent = ((total_mem - available_mem) / total_mem) * 100
            else:
                memory_usage_percent = 0
        except:
            memory_usage_percent = 0

        # Evidence-based severity assessment
        if any(keyword in crash_data_lower for keyword in ['critical', 'fatal', 'segfault']):
            return 'critical'
        elif memory_usage_percent > 85:
            return 'critical'  # Critical memory pressure
        elif any(keyword in crash_data_lower for keyword in ['error', 'exception', 'failed']) or memory_usage_percent > 70:
            return 'high'  # High memory pressure or explicit errors
        elif any(keyword in crash_data_lower for keyword in ['warning', 'timeout']) or memory_usage_percent > 50:
            return 'medium'  # Moderate memory pressure or warnings
        else:
            return 'low'
    
    def _generate_crash_recommendations(self, crash_data):
        """Generate specific recommendations based on crash analysis"""
        crash_type = self._identify_crash_type(crash_data)
        
        recommendations = {
            'memory_exhaustion': [
                'Increase system RAM or add swap space',
                'Close large files and projects in VSCode',
                'Disable memory-intensive extensions',
                'Use VSCode stable instead of Insiders',
                'Monitor memory usage with our tools'
            ],
            'segmentation_fault': [
                'Update VSCode to latest version',
                'Disable all extensions and re-enable one by one',
                'Check for corrupted VSCode installation',
                'Run VSCode with --disable-gpu flag',
                'Check system memory for hardware issues'
            ],
            'graphics_related': [
                'Update AMD graphics drivers',
                'Disable hardware acceleration in VSCode',
                'Switch to X11 session instead of Wayland',
                'Add amdgpu.dc=0 to kernel parameters',
                'Use software rendering as fallback'
            ],
            'extension_related': [
                'Identify and disable problematic extensions',
                'Start VSCode with --disable-extensions',
                'Update all extensions to latest versions',
                'Remove unused or outdated extensions',
                'Use extension bisect to find culprit'
            ],
            'timeout_related': [
                'Reduce system load and close unnecessary apps',
                'Increase VSCode timeout settings',
                'Check for disk I/O issues',
                'Monitor system performance',
                'Consider SSD upgrade for better performance'
            ]
        }
        
        return recommendations.get(crash_type, ['Update VSCode', 'Check system logs', 'Monitor system resources'])

    def _get_system_logs_around_crash(self):
        """Get system logs from around the crash time using accessible methods"""
        try:
            # Try user logs first (no sudo required)
            cmd = ['journalctl', '--user', '--since', '30 minutes ago', '--no-pager', '--lines=50']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            user_logs = []
            if result.returncode == 0 and result.stdout.strip():
                logs = result.stdout.strip().split('\n')
                for log in logs:
                    if any(keyword in log.lower() for keyword in
                          ['code', 'vscode', 'insiders', 'crash', 'error', 'killed']):
                        user_logs.append(f"[USER] {log}")

            # Try system logs without sudo (may have limited access) - EXCLUDE chat/application logs
            cmd = ['journalctl', '--since', '30 minutes ago', '--no-pager', '--lines=50']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            system_logs = []
            if result.returncode == 0 and result.stdout.strip():
                logs = result.stdout.strip().split('\n')
                for log in logs:
                    log_lower = log.lower()
                    # EXCLUDE chat logs, debug messages, and application logs
                    if any(exclude in log_lower for exclude in [
                        'augment', 'workspacestorage', 'debug', 'trace', 'info:console',
                        'conversation', 'chat', 'extension', '_performtextedits'
                    ]):
                        continue

                    # INCLUDE actual system errors and crashes
                    if any(keyword in log_lower for keyword in [
                        'segfault', 'killed', 'oom', 'out of memory', 'crash', 'abort',
                        'kernel:', 'systemd:', 'error:', 'failed', 'critical', 'warning'
                    ]):
                        system_logs.append(f"[SYSTEM] {log}")

            # Combine results
            all_logs = user_logs + system_logs
            if all_logs:
                return all_logs[:20]
            else:
                # Try with sudo if no logs found - use sequential execution
                try:
                    output_dir = self._run_sequential_sudo_commands_with_terminal()
                    # Check if system logs were collected
                    system_log_file = os.path.join(output_dir, 'system_logs.txt')
                    if os.path.exists(system_log_file):
                        with open(system_log_file, 'r') as f:
                            logs = f.read().strip().split('\n')
                            relevant_logs = []
                            for log in logs:
                                if any(keyword in log.lower() for keyword in
                                      ['code', 'vscode', 'insiders', 'crash', 'error', 'killed', 'segfault', 'oom']):
                                    relevant_logs.append(f"[SUDO] {log}")

                            if relevant_logs:
                                return relevant_logs[:25]
                except Exception as e:
                    return [f"[SUDO] Error collecting system logs: {e}"]

                # Final fallback: Check /var/log files that might be readable
                try:
                    log_files = ['/var/log/messages', '/var/log/syslog', '/var/log/kern.log']
                    for log_file in log_files:
                        if os.path.exists(log_file) and os.access(log_file, os.R_OK):
                            with open(log_file, 'r') as f:
                                lines = f.readlines()
                                recent_lines = lines[-50:]  # Last 50 lines
                                relevant = []
                                for line in recent_lines:
                                    if any(keyword in line.lower() for keyword in
                                          ['code', 'vscode', 'crash', 'error', 'oom']):
                                        relevant.append(f"[{log_file}] {line.strip()}")
                                if relevant:
                                    return relevant[:15]
                except:
                    pass

                return ["No relevant system logs found in accessible sources"]

        except Exception as e:
            return [f"Error accessing system logs: {e}"]

    def _run_sequential_sudo_commands_with_terminal(self):
        """Run all sudo commands sequentially in a single terminal window (singleton pattern)"""
        try:
            # Check if we already have a recent session running
            if hasattr(self, 'last_sudo_output_dir') and self.last_sudo_output_dir:
                # Check if the session is recent (within last 5 minutes)
                try:
                    session_timestamp = int(self.last_sudo_output_dir.split('_')[-1])
                    current_timestamp = int(time.time())
                    if current_timestamp - session_timestamp < 300:  # 5 minutes
                        print(f"🔄 Using existing sequential execution session: {self.last_sudo_output_dir}")
                        return self.last_sudo_output_dir
                except:
                    pass

            # Create unique output directory for this collection session
            timestamp = int(time.time())
            output_dir = f'/tmp/crash_analysis_session_{timestamp}'
            os.makedirs(output_dir, exist_ok=True)
            print(f"🚀 Starting new sequential execution session: {output_dir}")

            # Create a comprehensive script that runs all sudo commands sequentially
            sequential_script_content = f'''#!/bin/bash
# Sequential Sudo Command Execution for Crash Analysis
# This script runs all sudo commands in sequence, allowing password caching

echo "🔍 Starting comprehensive system log collection..."
echo "Please enter your sudo password once. Subsequent commands will run automatically."
echo ""

# Set sudo timeout to 15 minutes to allow all commands to complete
sudo -v
if [ $? -ne 0 ]; then
    echo "❌ Sudo authentication failed"
    exit 1
fi

echo "✅ Sudo authentication successful"
echo ""

# Command 1: System logs
echo "📋 1/3: Collecting system logs..."
sudo journalctl --since '30 minutes ago' --no-pager --lines=100 > {output_dir}/system_logs.txt 2>&1
if [ $? -eq 0 ]; then
    echo "✅ System logs collected successfully"
    echo "📄 Output: {output_dir}/system_logs.txt"
    echo "📊 Lines collected: $(wc -l < {output_dir}/system_logs.txt)"
else
    echo "❌ Failed to collect system logs"
fi
echo ""

# Command 2: Kernel messages
echo "📋 2/3: Collecting kernel messages..."
sudo dmesg --time-format=iso > {output_dir}/kernel_messages.txt 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Kernel messages collected successfully"
    echo "📄 Output: {output_dir}/kernel_messages.txt"
    echo "📊 Lines collected: $(wc -l < {output_dir}/kernel_messages.txt)"
else
    echo "❌ Failed to collect kernel messages"
fi
echo ""

# Command 3: Error logs
echo "📋 3/3: Collecting error logs..."
sudo journalctl --since '30 minutes ago' --no-pager --priority=err --lines=50 > {output_dir}/error_logs.txt 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Error logs collected successfully"
    echo "📄 Output: {output_dir}/error_logs.txt"
    echo "📊 Lines collected: $(wc -l < {output_dir}/error_logs.txt)"
else
    echo "❌ Failed to collect error logs"
fi
echo ""

# Summary
echo "🏁 Log collection complete!"
echo "📁 All logs saved to: {output_dir}/"
echo "📊 Total files created: $(ls -1 {output_dir}/ | wc -l)"
echo ""
echo "💡 You can now close this terminal and refresh the crash analysis"
echo "🔄 The collected data will be automatically integrated into the analysis"

# Keep terminal open for user to see results
echo ""
echo "Press Enter to close this terminal..."
read

# Return focus to browser
if command -v xdotool >/dev/null 2>&1; then
    firefox_window=$(xdotool search --name "Mozilla Firefox" | head -1)
    if [ -n "$firefox_window" ]; then
        xdotool windowactivate "$firefox_window" 2>/dev/null
    fi
fi

exit 0
'''

            # Write the sequential script
            script_path = f'/tmp/sequential_sudo_script_{timestamp}.sh'
            with open(script_path, 'w') as f:
                f.write(sequential_script_content)

            # Make script executable
            os.chmod(script_path, 0o755)

            # Store the output directory for later retrieval
            self.last_sudo_output_dir = output_dir

            # Open single terminal window with the sequential script
            terminal_commands = [
                ['konsole', '-e', 'bash', script_path],
                ['gnome-terminal', '--', 'bash', script_path],
                ['xterm', '-e', 'bash', script_path],
                ['alacritty', '-e', 'bash', script_path],
                ['xfce4-terminal', '-x', 'bash', script_path]
            ]

            terminal_opened = False
            for term_cmd in terminal_commands:
                try:
                    subprocess.Popen(term_cmd)
                    terminal_opened = True
                    print(f"✅ Opened single terminal for sequential sudo commands: {term_cmd[0]}")
                    break
                except FileNotFoundError:
                    continue

            if not terminal_opened:
                raise Exception("No suitable terminal emulator found")

            return output_dir

        except Exception as e:
            logger.error(f"Error running sequential sudo commands: {e}")
            raise e

    def _run_sudo_command_with_terminal(self, cmd, description="system logs"):
        """Legacy method - now redirects to sequential execution"""
        # For backward compatibility, redirect to sequential execution
        return self._run_sequential_sudo_commands_with_terminal()

    def _read_terminal_output(self):
        """Read output from terminal commands"""
        try:
            # Look for all crash analysis output files
            import glob
            output_files = glob.glob('/tmp/crash_analysis_*.txt')

            if output_files:
                all_content = {}
                for output_file in output_files:
                    try:
                        with open(output_file, 'r') as f:
                            content = f.read()
                            # Extract description from filename
                            filename = os.path.basename(output_file)
                            description = filename.replace('crash_analysis_', '').replace('.txt', '')
                            all_content[description] = content
                        # Clean up
                        os.remove(output_file)
                    except:
                        continue

                return all_content
            else:
                return {}
        except:
            return {}

    def _integrate_sudo_data(self, analysis):
        """Integrate sudo-collected data into analysis"""
        try:
            sudo_data = self._read_terminal_output()

            if sudo_data:
                # Process system logs
                if any('system_logs' in key for key in sudo_data.keys()):
                    system_key = next((k for k in sudo_data.keys() if 'system_logs' in k), None)
                    if system_key:
                        logs = sudo_data[system_key].split('\n')
                        relevant_logs = []
                        for log in logs:
                            if any(keyword in log.lower() for keyword in
                                  ['code', 'vscode', 'insiders', 'crash', 'error', 'killed', 'segfault', 'oom']):
                                relevant_logs.append(f"[SUDO] {log}")
                        if relevant_logs:
                            analysis['system_logs'] = relevant_logs[:25]

                # Process kernel messages
                if any('kernel_messages' in key for key in sudo_data.keys()):
                    kernel_key = next((k for k in sudo_data.keys() if 'kernel_messages' in k), None)
                    if kernel_key:
                        lines = sudo_data[kernel_key].split('\n')
                        relevant = []
                        for line in lines:
                            if any(keyword in line.lower() for keyword in
                                  ['oom', 'killed', 'segfault', 'memory', 'gpu', 'amd', 'drm', 'error', 'warning', 'crash']):
                                relevant.append(f"[SUDO] {line}")
                        if relevant:
                            analysis['kernel_messages'] = relevant[:15]

                # Update evidence with sudo data
                if 'evidence' not in analysis:
                    analysis['evidence'] = {'crash_indicators': [], 'system_correlation': [], 'resource_exhaustion': [], 'timeline_evidence': []}

                # Add sudo data to evidence
                for key, content in sudo_data.items():
                    if any(keyword in content.lower() for keyword in ['oom', 'killed', 'memory']):
                        analysis['evidence']['resource_exhaustion'].append(f"Sudo data from {key}: Memory/OOM evidence found")
                    if any(keyword in content.lower() for keyword in ['code', 'vscode', 'crash']):
                        analysis['evidence']['system_correlation'].append(f"Sudo data from {key}: VSCode/crash correlation found")

            return analysis

        except Exception as e:
            # Don't fail the analysis if sudo integration fails
            return analysis

    def _get_error_logs_around_crash(self):
        """Get error logs from around the crash time with proper sudo access"""
        try:
            # Get actual system error logs (priority=err) excluding application chatter
            cmd = ['journalctl', '--since', '30 minutes ago', '--no-pager', '--priority=err', '--lines=50']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0 and result.stdout.strip():
                logs = result.stdout.strip().split('\n')
                error_logs = []
                for log in logs:
                    log_lower = log.lower()
                    # EXCLUDE application debug/chat logs
                    if any(exclude in log_lower for exclude in [
                        'augment', 'workspacestorage', 'debug', 'trace', 'info:console',
                        'conversation', 'chat', 'extension', '_performtextedits', 'vscode-app'
                    ]):
                        continue

                    # INCLUDE actual system errors
                    if any(keyword in log_lower for keyword in [
                        'error', 'failed', 'segfault', 'killed', 'abort', 'crash',
                        'oom', 'out of memory', 'kernel panic', 'systemd', 'authentication failure'
                    ]) or 'err' in log_lower:
                        error_logs.append(f"[ERROR] {log}")

                if error_logs:
                    return error_logs[:20]
                else:
                    # Try to get any system errors, even if not crash-related
                    cmd_all = ['journalctl', '--since', '1 hour ago', '--no-pager', '--priority=err', '--lines=20']
                    result_all = subprocess.run(cmd_all, capture_output=True, text=True, timeout=10)
                    if result_all.returncode == 0 and result_all.stdout.strip():
                        all_errors = result_all.stdout.strip().split('\n')
                        return [f"[ERROR] {log}" for log in all_errors[:10]] if all_errors else ["[ERROR] No system errors found"]
                    else:
                        return ["[ERROR] No system errors found in last hour"]

            # If that fails, try with sudo via sequential execution
            try:
                output_dir = self._run_sequential_sudo_commands_with_terminal()
                # Check if error logs were collected
                error_log_file = os.path.join(output_dir, 'error_logs.txt')
                if os.path.exists(error_log_file):
                    with open(error_log_file, 'r') as f:
                        logs = f.read().strip().split('\n')
                        error_logs = []
                        for log in logs:
                            if any(keyword in log.lower() for keyword in
                                  ['code', 'vscode', 'insiders', 'crash', 'segfault', 'killed', 'error', 'failed']):
                                error_logs.append(f"[SUDO] {log}")

                        if error_logs:
                            return error_logs[:20]
                        else:
                            return [f"[SUDO] {log}" for log in logs[:15]] if logs else ["No error logs found with sudo access"]
                else:
                    return ["[SUDO] Terminal opened for error log collection"]
            except Exception as e:
                return [f"Error getting error logs with sequential execution: {e}"]

        except Exception as e:
            return [f"Error accessing error logs: {e}"]

    def _get_application_logs_around_crash(self):
        """Get application-specific logs with proper error handling"""
        try:
            vscode_logs = []
            log_paths = [
                Path.home() / '.config' / 'Code - Insiders' / 'logs',
                Path.home() / '.config' / 'Code' / 'logs',
                Path('/tmp')
            ]

            for log_path in log_paths:
                try:
                    if log_path.exists() and log_path.is_dir():
                        # Look for recent log files
                        for log_file in log_path.rglob('*.log'):
                            try:
                                # Check if file is recent (last 24 hours)
                                if log_file.stat().st_mtime > (time.time() - 86400):
                                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                        content = f.read()
                                        if any(keyword in content.lower() for keyword in
                                              ['error', 'crash', 'segfault', 'exception', 'fatal']):
                                            # Get last 300 chars of relevant content
                                            lines = content.split('\n')
                                            relevant_lines = [line for line in lines if
                                                            any(keyword in line.lower() for keyword in
                                                               ['error', 'crash', 'exception', 'fatal'])]
                                            if relevant_lines:
                                                vscode_logs.append(f"From {log_file.name}: {relevant_lines[-1][:200]}")
                            except (PermissionError, UnicodeDecodeError, OSError):
                                continue
                except (OSError, PermissionError):
                    continue

            if vscode_logs:
                return vscode_logs[:10]
            else:
                # Try to get VSCode process information instead
                try:
                    cmd = ['ps', 'aux']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        vscode_processes = []
                        for line in result.stdout.split('\n'):
                            if any(keyword in line.lower() for keyword in ['code-insiders', 'vscode']):
                                vscode_processes.append(line.strip())

                        if vscode_processes:
                            return [f"VSCode processes found: {len(vscode_processes)} running"] + vscode_processes[:5]
                        else:
                            return ["No VSCode application logs or processes found"]
                    else:
                        return ["No VSCode application logs found"]
                except:
                    return ["No VSCode application logs found"]

        except Exception as e:
            return [f"Error accessing application logs: {e}"]

    def _get_kernel_messages(self):
        """Get kernel messages related to the crash using accessible methods"""
        try:
            # Try dmesg without sudo first
            cmd = ['dmesg', '--time-format=iso']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                relevant = []
                for line in lines[-100:]:  # Last 100 kernel messages
                    if any(keyword in line.lower() for keyword in
                          ['oom', 'killed', 'segfault', 'memory', 'gpu', 'amd', 'drm', 'error', 'warning', 'crash']):
                        relevant.append(line)

                if relevant:
                    return relevant[:15]
                else:
                    # Return recent kernel messages even if not specifically relevant
                    return lines[-10:] if lines else ["No recent kernel messages"]
            else:
                # Try with sudo using sequential execution
                try:
                    output_dir = self._run_sequential_sudo_commands_with_terminal()
                    # Check if kernel messages were collected
                    kernel_log_file = os.path.join(output_dir, 'kernel_messages.txt')
                    if os.path.exists(kernel_log_file):
                        with open(kernel_log_file, 'r') as f:
                            content = f.read().strip()
                            if content:
                                lines = content.split('\n')
                                relevant = []
                                for line in lines[-100:]:  # Last 100 kernel messages
                                    if any(keyword in line.lower() for keyword in
                                          ['oom', 'killed', 'segfault', 'memory', 'gpu', 'amd', 'drm', 'error', 'warning', 'crash']):
                                        relevant.append(f"[SUDO] {line}")

                                if relevant:
                                    return relevant[:15]
                                else:
                                    # Return recent kernel messages with sudo
                                    return [f"[SUDO] {line}" for line in lines[-10:]] if lines else ["No recent kernel messages with sudo"]
                    else:
                        return ["[SUDO] Terminal opened for kernel message collection"]
                except Exception as e:
                    return [f"Error accessing kernel messages: {e}"]
                else:
                    # Fallback: Try alternative kernel log sources
                    kernel_sources = [
                        '/var/log/kern.log',
                        '/var/log/messages',
                        '/var/log/dmesg'
                    ]

                    for log_file in kernel_sources:
                        try:
                            if os.path.exists(log_file) and os.access(log_file, os.R_OK):
                                with open(log_file, 'r') as f:
                                    lines = f.readlines()
                                    recent_lines = lines[-50:]  # Last 50 lines
                                    relevant = []
                                    for line in recent_lines:
                                        if any(keyword in line.lower() for keyword in
                                              ['oom', 'killed', 'kernel', 'memory', 'gpu', 'crash']):
                                            relevant.append(f"[{os.path.basename(log_file)}] {line.strip()}")
                                    if relevant:
                                        return relevant[:10]
                        except:
                            continue

                    return [
                        f"Kernel messages access denied: {result.stderr.strip() if result.stderr else 'Permission denied'}",
                        "Note: dmesg requires elevated privileges on this system",
                        "Checked alternative sources: /var/log/kern.log, /var/log/messages"
                    ]

        except Exception as e:
            return [f"Error accessing kernel messages: {e}"]

    def _get_memory_pressure_data(self):
        """Get accurate memory pressure analysis with evidence-based assessment"""
        try:
            # Get memory information
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()

            memory_data = {}
            for line in meminfo.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    memory_data[key.strip()] = value.strip()

            # Calculate accurate memory pressure indicators
            total_mem = int(memory_data.get('MemTotal', '0').split()[0])
            available_mem = int(memory_data.get('MemAvailable', '0').split()[0])
            free_mem = int(memory_data.get('MemFree', '0').split()[0])
            swap_total = int(memory_data.get('SwapTotal', '0').split()[0])
            swap_free = int(memory_data.get('SwapFree', '0').split()[0])

            if total_mem > 0:
                used_mem = total_mem - available_mem
                memory_usage_percent = (used_mem / total_mem) * 100
                swap_used = swap_total - swap_free
                swap_usage_percent = (swap_used / swap_total) * 100 if swap_total > 0 else 0

                # Get top memory consumers for evidence
                top_processes = []
                try:
                    result = subprocess.run(['ps', 'aux', '--sort=-%mem'],
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')[1:6]  # Top 5 processes
                        for line in lines:
                            parts = line.split()
                            if len(parts) >= 11:
                                pid = parts[1]
                                mem_percent = parts[3]
                                command = ' '.join(parts[10:])[:40]
                                if 'code' in command.lower() or 'vscode' in command.lower():
                                    top_processes.append(f"🔴 VSCode PID {pid}: {mem_percent}% - {command}")
                                else:
                                    top_processes.append(f"   PID {pid}: {mem_percent}% - {command}")
                except:
                    top_processes = ["Unable to get process information"]

                # Determine evidence-based pressure level
                if memory_usage_percent > 85:
                    pressure_level = "🚨 CRITICAL"
                    assessment = "System under severe memory pressure"
                elif memory_usage_percent > 70:
                    pressure_level = "⚠️ HIGH"
                    assessment = "System under significant memory pressure"
                elif memory_usage_percent > 50:
                    pressure_level = "⚡ MODERATE"
                    assessment = "System under moderate memory pressure"
                else:
                    pressure_level = "✅ LOW"
                    assessment = "System memory pressure is low"

                return [
                    f"=== EVIDENCE-BASED MEMORY ANALYSIS ===",
                    f"Total RAM: {total_mem} kB ({total_mem/1024/1024:.1f} GB)",
                    f"Used: {used_mem} kB ({memory_usage_percent:.1f}%)",
                    f"Available: {available_mem} kB ({available_mem/1024/1024:.1f} GB)",
                    f"Free: {free_mem} kB ({free_mem/1024/1024:.1f} GB)",
                    f"Swap Used: {swap_used} kB ({swap_usage_percent:.1f}%)",
                    f"PRESSURE LEVEL: {pressure_level}",
                    f"ASSESSMENT: {assessment}",
                    f"",
                    f"=== TOP MEMORY CONSUMERS ===",
                ] + top_processes
            else:
                return ["❌ Unable to parse memory information"]

        except Exception as e:
            return [f"❌ Error reading memory pressure data: {e}"]

    def _get_process_state_at_crash(self):
        """Get process state information"""
        try:
            process_data = {}

            # Check for VSCode processes
            cmd = ['ps', 'aux']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                vscode_processes = []
                for line in result.stdout.split('\n'):
                    if 'code' in line.lower() and ('insiders' in line.lower() or 'vscode' in line.lower()):
                        vscode_processes.append(line)

                process_data['vscode_processes'] = vscode_processes

            # Check system load
            try:
                with open('/proc/loadavg', 'r') as f:
                    process_data['system_load'] = f.read().strip()
            except:
                pass

            return process_data

        except Exception as e:
            return {'error': f"Error getting process state: {e}"}

    def _compile_evidence(self, crash_data, system_logs, error_logs):
        """Compile comprehensive evidence from all sources with actual message capture"""
        evidence = {
            'crash_indicators': [],
            'system_correlation': [],
            'resource_exhaustion': [],
            'timeline_evidence': []
        }

        # Analyze crash data for comprehensive indicators
        crash_data_lower = crash_data.lower()

        # Memory-related crashes
        if 'out of memory' in crash_data_lower or 'oom' in crash_data_lower:
            evidence['crash_indicators'].append("Memory exhaustion detected in crash data")

        # Signal-based crashes (CRITICAL)
        if 'anom_abend' in crash_data_lower:
            evidence['crash_indicators'].append("ANOM_ABEND: Abnormal process termination detected")

        if 'sig=11' in crash_data_lower or 'sigsegv' in crash_data_lower:
            evidence['crash_indicators'].append("SIGSEGV (sig=11): Segmentation fault detected")

        if 'sig=4' in crash_data_lower or 'sigill' in crash_data_lower:
            evidence['crash_indicators'].append("SIGILL (sig=4): Illegal instruction detected")

        if 'sig=6' in crash_data_lower or 'sigabrt' in crash_data_lower:
            evidence['crash_indicators'].append("SIGABRT (sig=6): Process abort detected")

        if 'sig=9' in crash_data_lower or 'sigkill' in crash_data_lower:
            evidence['crash_indicators'].append("SIGKILL (sig=9): Process killed detected")

        # VSCode-specific crashes
        if 'code-insiders' in crash_data_lower and 'audit' in crash_data_lower:
            evidence['crash_indicators'].append("VSCode Insiders audit trail crash detected")

        if 'segmentation fault' in crash_data_lower:
            evidence['crash_indicators'].append("Segmentation fault detected in crash data")

        if 'webgl' in crash_data_lower and 'deprecated' in crash_data_lower:
            evidence['crash_indicators'].append("WebGL fallback issue detected")

        # Extract actual crash lines from data
        crash_lines = crash_data.split('\n')
        for line in crash_lines:
            line_lower = line.lower()
            if any(signal in line_lower for signal in ['anom_abend', 'sig=', 'segfault', 'killed']):
                evidence['crash_indicators'].append(f"Crash line: {line.strip()}")

        # Correlate with system logs (enhanced)
        for log in system_logs:
            log_lower = log.lower()
            if 'code' in log_lower and any(keyword in log_lower for keyword in ['killed', 'crash', 'error', 'segfault', 'abort']):
                evidence['system_correlation'].append(log)
            if 'drkonqi' in log_lower:  # KDE crash handler
                evidence['system_correlation'].append(log)

        # Check for resource exhaustion evidence (enhanced)
        for log in error_logs:
            log_lower = log.lower()
            if any(keyword in log_lower for keyword in ['memory', 'oom', 'swap', 'killed process']):
                evidence['resource_exhaustion'].append(log)

        # Timeline evidence from crash data
        import re
        timestamp_pattern = r'\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}'
        timestamps = re.findall(timestamp_pattern, crash_data)
        if timestamps:
            evidence['timeline_evidence'] = [f"Crash timestamp: {ts}" for ts in timestamps[:5]]

        return evidence

    def _get_fallback_solutions(self, crash_type):
        """Get fallback solutions when database is unavailable"""
        fallback_solutions = {
            'memory_exhaustion': [
                {
                    'title': 'Clear System Memory',
                    'description': 'Free up system memory and restart memory protection',
                    'commands': ['sudo sysctl vm.drop_caches=3', 'pkill -f "code.*--type=renderer"'],
                    'severity': 'HIGH',
                    'category': 'Memory Management',
                    'source': 'fallback',
                    'verified': False,
                    'effectiveness': 7
                },
                {
                    'title': 'Optimize VSCode Memory',
                    'description': 'Configure VSCode for lower memory usage',
                    'commands': ['code --max-memory=4096', 'code --disable-extensions'],
                    'severity': 'MEDIUM',
                    'category': 'Application Tuning',
                    'source': 'fallback',
                    'verified': False,
                    'effectiveness': 6
                }
            ],
            'renderer_process_crash': [
                {
                    'title': 'Disable GPU Acceleration',
                    'description': 'Start VSCode without GPU acceleration',
                    'commands': ['code --disable-gpu'],
                    'severity': 'HIGH',
                    'category': 'Graphics',
                    'source': 'fallback',
                    'verified': False,
                    'effectiveness': 8
                }
            ],
            'unknown': [
                {
                    'title': 'Safe Mode Restart',
                    'description': 'Restart VSCode in safe mode',
                    'commands': ['code --disable-extensions --disable-gpu'],
                    'severity': 'MEDIUM',
                    'category': 'General',
                    'source': 'fallback',
                    'verified': False,
                    'effectiveness': 5
                }
            ]
        }

        return fallback_solutions.get(crash_type, fallback_solutions['unknown'])

    def correlate_crash_with_clipboard(self, crash_analysis):
        """Correlate crash with clipboard data"""
        try:
            conn = sqlite3.connect(str(CLIPBOARD_DB))
            conn.row_factory = sqlite3.Row
            
            # Get clipboard entries around crash time
            crash_time = datetime.fromisoformat(crash_analysis['timestamp'])
            start_time = crash_time - timedelta(minutes=30)
            end_time = crash_time + timedelta(minutes=5)
            
            cursor = conn.execute('''
                SELECT id, content, timestamp
                FROM clipboard_history 
                WHERE datetime(timestamp) BETWEEN ? AND ?
                ORDER BY timestamp DESC
            ''', (start_time.isoformat(), end_time.isoformat()))
            
            clipboard_entries = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # Find correlations
            correlations = []
            for entry in clipboard_entries:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                time_diff = abs((crash_time - entry_time).total_seconds())
                
                # Check for performance-related content
                content_lower = entry['content'].lower()
                performance_keywords = ['slow', 'lag', 'freeze', 'crash', 'performance', 'cpu', 'memory', 'hang']
                
                relevance_score = sum(1 for keyword in performance_keywords if keyword in content_lower)
                
                if time_diff <= 1800 and relevance_score > 0:  # Within 30 minutes and relevant
                    correlation = {
                        'clipboard_entry': entry,
                        'time_difference_minutes': time_diff / 60,
                        'relevance_score': relevance_score,
                        'correlation_strength': max(0, 100 - (time_diff / 18) + (relevance_score * 10))
                    }
                    correlations.append(correlation)
            
            return sorted(correlations, key=lambda x: x['correlation_strength'], reverse=True)
            
        except Exception as e:
            print(f"Error correlating crash data: {e}")
            return []
    
    def get_crash_summary(self):
        """Get comprehensive crash analysis summary"""
        return {
            'total_crashes': len(self.crash_events),
            'recent_crashes': [crash for crash in self.crash_events if 
                             datetime.fromisoformat(crash['timestamp']) > datetime.now() - timedelta(hours=24)],
            'crash_types': self._get_crash_type_distribution(),
            'severity_distribution': self._get_severity_distribution(),
            'recommendations': self._get_consolidated_recommendations()
        }
    
    def _get_crash_type_distribution(self):
        """Get distribution of crash types"""
        types = {}
        for crash in self.crash_events:
            crash_type = crash.get('crash_type', 'unknown')
            types[crash_type] = types.get(crash_type, 0) + 1
        return types
    
    def _get_severity_distribution(self):
        """Get distribution of crash severities"""
        severities = {}
        for crash in self.crash_events:
            severity = crash.get('severity', 'unknown')
            severities[severity] = severities.get(severity, 0) + 1
        return severities
    
    def _get_consolidated_recommendations(self):
        """Get consolidated recommendations from all crashes"""
        all_recommendations = []
        for crash in self.crash_events:
            all_recommendations.extend(crash.get('recommendations', []))
        
        # Count frequency and return top recommendations
        rec_counts = {}
        for rec in all_recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        return sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)[:10]

# Global correlator instance
crash_correlator = CrashAnalysisCorrelator()

@app.route('/')
def crash_dashboard():
    """Crash analysis dashboard"""
    return render_template_string(CRASH_TEMPLATE)

@app.route('/api/analyze-crash', methods=['POST'])
def analyze_crash():
    """Analyze crash file with intelligent solutions"""
    data = request.get_json()
    crash_file = data.get('crash_file', '/home/owner/Documents/2025_06_26_vscode_crash.txt')

    analysis = crash_correlator.analyze_vscode_crash_file(crash_file)

    if 'error' not in analysis:
        # Add correlation data
        correlations = crash_correlator.correlate_crash_with_clipboard(analysis)
        analysis['clipboard_correlations'] = correlations

        # Add database-driven intelligent solutions
        try:
            crash_type = analysis.get('crash_type', 'unknown')
            crash_data = analysis.get('raw_crash_data', '')

            if crash_correlator.solutions_db:
                # Use performance-optimized search if available
                if crash_correlator.performance_optimizer:
                    db_solutions = crash_correlator.performance_optimizer.optimized_search(crash_data)
                    perf_stats = crash_correlator.performance_optimizer.get_performance_stats()
                else:
                    db_solutions = crash_correlator.solutions_db.find_solutions(crash_data)
                    perf_stats = None

                # Apply intelligent ranking if available
                if crash_correlator.intelligent_ranking and db_solutions:
                    user_context = {
                        'platform': 'linux',  # Could be detected from system
                        'severity': analysis.get('severity', 'medium')
                    }
                    db_solutions = crash_correlator.intelligent_ranking.rank_solutions(
                        db_solutions, crash_data, user_context
                    )

                # Convert database solutions to our format
                intelligent_solutions = []
                immediate_actions = []
                preventive_measures = []

                for solution in db_solutions:
                    solution_item = {
                        'title': solution['solution_title'],
                        'description': solution['solution_description'],
                        'commands': solution['commands'],
                        'category': solution['issue_type'].replace('_', ' ').title(),
                        'severity': solution['severity'].upper(),
                        'source': solution['source_type'],
                        'verified': solution['verified'],
                        'effectiveness': solution['effectiveness_rating'],
                        'source_url': solution.get('source_url', ''),
                        'intelligent_score': solution.get('intelligent_score', 0.5)
                    }

                    # Categorize solutions based on severity and type
                    if solution['severity'] == 'critical' or 'immediate' in solution['solution_title'].lower():
                        immediate_actions.append(solution_item)
                    elif 'prevent' in solution['solution_title'].lower() or 'install' in solution['solution_title'].lower():
                        preventive_measures.append(solution_item)
                    else:
                        intelligent_solutions.append(solution_item)

                # Add database solutions (sorted by intelligent score)
                analysis['intelligent_solutions'] = intelligent_solutions[:5]  # Top 5
                analysis['immediate_actions'] = immediate_actions[:3]  # Top 3
                analysis['preventive_measures'] = preventive_measures[:3]  # Top 3

                # Add enhanced database statistics
                db_stats = crash_correlator.solutions_db.get_database_stats()
                analysis['solutions_database'] = {
                    'total_solutions': db_stats['total_solutions'],
                    'verified_solutions': db_stats['verified_solutions'],
                    'solutions_found': len(db_solutions),
                    'database_available': True,
                    'performance_stats': perf_stats,
                    'intelligent_ranking_enabled': crash_correlator.intelligent_ranking is not None
                }
            else:
                # Fallback to basic solutions if database unavailable
                analysis['intelligent_solutions'] = crash_correlator._get_fallback_solutions(crash_type)
                analysis['immediate_actions'] = []
                analysis['preventive_measures'] = []
                analysis['solutions_database'] = {'database_available': False}

        except Exception as e:
            print(f"Could not add database solutions: {e}")
            # Fallback to basic solutions
            analysis['intelligent_solutions'] = crash_correlator._get_fallback_solutions(analysis.get('crash_type', 'unknown'))
            analysis['immediate_actions'] = []
            analysis['preventive_measures'] = []

    return jsonify(analysis)

@app.route('/api/crash-summary')
def crash_summary():
    """Get crash analysis summary"""
    return jsonify(crash_correlator.get_crash_summary())

@app.route('/api/performance-stats')
def performance_stats_api():
    """API endpoint for performance statistics"""
    try:
        stats = {}

        if crash_correlator.performance_optimizer:
            stats['performance'] = crash_correlator.performance_optimizer.get_performance_stats()

        if crash_correlator.intelligent_ranking:
            stats['learning_insights'] = crash_correlator.intelligent_ranking.get_learning_insights()

        if crash_correlator.solutions_db:
            stats['database'] = crash_correlator.solutions_db.get_database_stats()

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solution-feedback', methods=['POST'])
def solution_feedback_api():
    """API endpoint for recording solution feedback"""
    try:
        data = request.get_json()
        solution_id = data.get('solution_id', 1)
        crash_context = data.get('crash_context', '')
        feedback_type = data.get('feedback_type', 'success')
        effectiveness_score = data.get('effectiveness_score', 0.8)
        comment = data.get('comment', '')

        if crash_correlator.intelligent_ranking:
            crash_correlator.intelligent_ranking.record_solution_feedback(
                solution_id, crash_context, feedback_type, effectiveness_score, comment
            )
            return jsonify({'status': 'success', 'message': 'Feedback recorded'})
        else:
            return jsonify({'error': 'Intelligent ranking not available'}), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/collect-sudo-logs')
def collect_sudo_logs():
    """Trigger single terminal window for sequential sudo log collection"""
    try:
        # Create a single script that runs all sudo commands sequentially
        # This allows the user to enter password once and subsequent commands use cached credentials
        crash_correlator._run_sequential_sudo_commands_with_terminal()

        return jsonify({
            'status': 'success',
            'message': 'Single terminal window opened for sequential sudo log collection',
            'instructions': 'Please enter your sudo password once. Subsequent commands will run automatically.'
        })

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/check-sudo-results')
def check_sudo_results():
    """Check if sequential sudo log collection is complete"""
    try:
        # Check for sequential execution output directory
        if hasattr(crash_correlator, 'last_sudo_output_dir') and crash_correlator.last_sudo_output_dir:
            output_dir = crash_correlator.last_sudo_output_dir

            # Check if output files exist
            import os
            expected_files = ['system_logs.txt', 'kernel_messages.txt', 'error_logs.txt']
            completed_files = []

            for filename in expected_files:
                filepath = os.path.join(output_dir, filename)
                if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    completed_files.append(filename)

            if len(completed_files) >= 2:  # At least 2 out of 3 files completed
                return jsonify({
                    'status': 'complete',
                    'output': f"Sequential execution completed. {len(completed_files)}/{len(expected_files)} log files collected.",
                    'message': 'Sequential sudo log collection complete',
                    'files_collected': completed_files,
                    'output_directory': output_dir
                })
            else:
                return jsonify({
                    'status': 'in_progress',
                    'message': f'Sequential execution in progress. {len(completed_files)}/{len(expected_files)} files completed.',
                    'files_collected': completed_files
                })
        else:
            # Fallback to old method
            output = crash_correlator._read_terminal_output()
            if output:
                return jsonify({
                    'status': 'complete',
                    'output': output,
                    'message': 'Sudo log collection complete'
                })
            else:
                return jsonify({
                    'status': 'in_progress',
                    'message': 'Sequential sudo execution in progress. Please wait for completion.'
                })

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/execute-solution', methods=['POST'])
def execute_solution():
    """Execute a specific solution with real-time feedback"""
    try:
        data = request.get_json()
        solution = data.get('solution', {})
        dry_run = data.get('dry_run', True)

        if not solution:
            return jsonify({'error': 'No solution provided'}), 400

        results = {
            'solution_title': solution.get('title', 'Unknown Solution'),
            'description': solution.get('description', ''),
            'commands_executed': [],
            'success': True,
            'errors': [],
            'dry_run': dry_run,
            'execution_time': 0
        }

        import time
        start_time = time.time()

        for command in solution.get('commands', []):
            try:
                if dry_run:
                    # Simulate execution
                    command_result = {
                        'command': command,
                        'return_code': 0,
                        'stdout': f'DRY RUN: Would execute {command}',
                        'stderr': ''
                    }
                else:
                    # Actually execute command (non-sudo commands only for safety)
                    if command.strip().startswith('sudo'):
                        command_result = {
                            'command': command,
                            'return_code': 1,
                            'stdout': '',
                            'stderr': 'Sudo commands require terminal execution for security'
                        }
                        results['success'] = False
                        results['errors'].append(command_result)
                    else:
                        result = subprocess.run(
                            command,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        command_result = {
                            'command': command,
                            'return_code': result.returncode,
                            'stdout': result.stdout.strip(),
                            'stderr': result.stderr.strip()
                        }

                        if result.returncode != 0:
                            results['success'] = False
                            results['errors'].append(command_result)

                results['commands_executed'].append(command_result)

            except subprocess.TimeoutExpired:
                error_result = {
                    'command': command,
                    'error': 'Command timed out after 30 seconds'
                }
                results['errors'].append(error_result)
                results['success'] = False

            except Exception as e:
                error_result = {
                    'command': command,
                    'error': str(e)
                }
                results['errors'].append(error_result)
                results['success'] = False

        results['execution_time'] = time.time() - start_time

        return jsonify(results)

    except Exception as e:
        logger.error(f"Error executing solution: {e}")
        return jsonify({'error': str(e)}), 500

# Complete Crash Analysis Template
CRASH_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💥 Crash Analysis Correlator</title>
    <style>
        :root {
            --bg-primary: #1a0a0a;
            --bg-secondary: #2a1a1a;
            --bg-surface: #3a2a2a;
            --text-primary: #ffffff;
            --text-secondary: #cccccc;
            --accent-critical: #ff4757;
            --accent-warning: #ffa502;
            --accent-success: #2ed573;
            --accent-info: #3742fa;
            --border-color: #4a3a3a;
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
            padding: 1.5rem 2rem;
            border-bottom: 3px solid var(--accent-critical);
            text-align: center;
        }

        .header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            color: var(--accent-critical);
        }

        .header p {
            color: var(--text-secondary);
            font-size: 1.1rem;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            display: grid;
            gap: 2rem;
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
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--accent-critical);
        }

        .btn {
            background: var(--accent-critical);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            transition: all 0.3s;
            user-select: text;
            -webkit-user-select: text;
            -moz-user-select: text;
            -ms-user-select: text;
        }

        .btn:hover {
            background: #ff3742;
            transform: translateY(-2px);
        }

        .crash-file-input {
            width: 100%;
            background: var(--bg-surface);
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
            color: var(--text-primary);
            font-size: 1rem;
            margin-bottom: 1rem;
        }

        .crash-file-input:focus {
            outline: none;
            border-color: var(--accent-critical);
        }

        .analysis-result {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 1rem;
            display: none;
        }

        .analysis-result.show {
            display: block;
            animation: fadeIn 0.5s ease-in;
        }

        .crash-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .info-card {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1rem;
        }

        .info-card h4 {
            color: var(--accent-warning);
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-card p {
            font-size: 1.1rem;
            font-weight: 600;
        }

        .recommendations {
            background: var(--bg-primary);
            border: 1px solid var(--accent-success);
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 1rem;
        }

        .recommendations h4 {
            color: var(--accent-success);
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }

        .recommendations ul {
            list-style: none;
            padding: 0;
        }

        .recommendations li {
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--border-color);
            position: relative;
            padding-left: 1.5rem;
        }

        .recommendations li::before {
            content: '→';
            position: absolute;
            left: 0;
            color: var(--accent-success);
            font-weight: bold;
        }

        .correlations {
            background: var(--bg-primary);
            border: 1px solid var(--accent-info);
            border-radius: 8px;
            padding: 1.5rem;
            margin-top: 1rem;
        }

        .correlations h4 {
            color: var(--accent-info);
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }

        .correlation-item {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .correlation-strength {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .strength-high { background: var(--accent-critical); color: white; }
        .strength-medium { background: var(--accent-warning); color: white; }
        .strength-low { background: var(--accent-info); color: white; }

        .loading {
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
        }

        .spinner {
            display: inline-block;
            width: 24px;
            height: 24px;
            border: 2px solid var(--border-color);
            border-top: 2px solid var(--accent-critical);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 0.75rem;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .error {
            background: var(--accent-critical);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
        }

        .success {
            background: var(--accent-success);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>💥 Crash Analysis Correlator</h1>
        <p>Advanced crash analysis and correlation with system events</p>
    </header>

    <div class="container">
        <!-- Crash File Analysis -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">VSCode Crash Analysis</h2>
                <button class="btn" onclick="analyzeDefaultCrash()">
                    🔍 Analyze VSCode Crash
                </button>
            </div>

            <div>
                <label for="crashFile" style="display: block; margin-bottom: 0.5rem; color: var(--text-secondary);">
                    Crash File Path:
                </label>
                <input type="text"
                       id="crashFile"
                       class="crash-file-input"
                       value="/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt"
                       placeholder="Enter path to crash file...">

                <button class="btn" onclick="analyzeCrash()" style="width: 100%; margin-bottom: 1rem;">
                    📊 Analyze Crash File
                </button>

                <button class="btn" onclick="collectSudoLogs()" style="width: 100%; background: var(--accent-warning);">
                    🔐 Collect System Logs (Requires Sudo)
                </button>
            </div>

            <div id="analysisResult" class="analysis-result">
                <!-- Analysis results will be populated here -->
            </div>
        </div>

        <!-- Crash Summary -->
        <div class="section">
            <div class="section-header">
                <h2 class="section-title">Crash Summary</h2>
                <button class="btn" onclick="loadCrashSummary()">
                    📈 Refresh Summary
                </button>
            </div>

            <div id="crashSummary">
                <div class="loading">
                    <div class="spinner"></div>
                    <span>Loading crash summary...</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Crash Analysis JavaScript
        class CrashAnalyzer {
            constructor() {
                this.loadCrashSummary();
            }

            async analyzeCrash() {
                const crashFile = document.getElementById('crashFile').value;
                const resultDiv = document.getElementById('analysisResult');

                if (!crashFile.trim()) {
                    this.showError('Please enter a crash file path');
                    return;
                }

                resultDiv.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <span>Analyzing crash file...</span>
                    </div>
                `;
                resultDiv.classList.add('show');

                try {
                    const response = await fetch('/api/analyze-crash', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            crash_file: crashFile
                        })
                    });

                    const analysis = await response.json();

                    if (analysis.error) {
                        this.showError(analysis.error);
                    } else {
                        this.displayAnalysis(analysis);
                    }

                } catch (error) {
                    this.showError('Failed to analyze crash file: ' + error.message);
                }
            }

            async analyzeDefaultCrash() {
                document.getElementById('crashFile').value = '/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt';
                await this.analyzeCrash();
            }

            displayAnalysis(analysis) {
                const resultDiv = document.getElementById('analysisResult');

                const html = `
                    <div class="crash-info">
                        <div class="info-card">
                            <h4>Crash Type</h4>
                            <p>${analysis.crash_type || 'Unknown'}</p>
                        </div>
                        <div class="info-card">
                            <h4>Severity</h4>
                            <p style="color: ${this.getSeverityColor(analysis.severity)}">${analysis.severity || 'Unknown'}</p>
                        </div>
                        <div class="info-card">
                            <h4>File Size</h4>
                            <p>${analysis.file_size || 0} bytes</p>
                        </div>
                        <div class="info-card">
                            <h4>Analysis Time</h4>
                            <p>${new Date(analysis.timestamp).toLocaleString()}</p>
                        </div>
                    </div>

                    ${analysis.evidence ? `
                        <div style="background: var(--bg-primary); border: 2px solid var(--accent-warning); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                            <h3 style="color: var(--accent-warning); margin-bottom: 1rem;">🔍 EVIDENCE & SYSTEM DATA</h3>

                            ${analysis.evidence.crash_indicators && analysis.evidence.crash_indicators.length > 0 ? `
                                <div style="margin-bottom: 1rem;">
                                    <h4 style="color: var(--accent-critical); margin-bottom: 0.5rem;">💥 Crash Indicators:</h4>
                                    <ul style="margin-left: 1rem; color: var(--text-primary);">
                                        ${analysis.evidence.crash_indicators.map(indicator => `<li>${this.escapeHtml(indicator)}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}

                            ${analysis.evidence.system_correlation && analysis.evidence.system_correlation.length > 0 ? `
                                <div style="margin-bottom: 1rem;">
                                    <h4 style="color: var(--accent-info); margin-bottom: 0.5rem;">🖥️ System Log Correlation:</h4>
                                    <div style="background: var(--bg-surface); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.8rem; max-height: 200px; overflow-y: auto;">
                                        ${analysis.evidence.system_correlation.map(log => `<div style="margin-bottom: 0.5rem; word-break: break-all;">${this.escapeHtml(log)}</div>`).join('')}
                                    </div>
                                </div>
                            ` : ''}

                            ${analysis.evidence.resource_exhaustion && analysis.evidence.resource_exhaustion.length > 0 ? `
                                <div style="margin-bottom: 1rem;">
                                    <h4 style="color: var(--accent-critical); margin-bottom: 0.5rem;">⚠️ Resource Exhaustion Evidence:</h4>
                                    <div style="background: var(--bg-surface); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.8rem; max-height: 200px; overflow-y: auto;">
                                        ${analysis.evidence.resource_exhaustion.map(log => `<div style="margin-bottom: 0.5rem; word-break: break-all;">${this.escapeHtml(log)}</div>`).join('')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    ` : ''}

                    ${analysis.system_logs && analysis.system_logs.length > 0 ? `
                        <div style="background: var(--bg-primary); border: 1px solid var(--accent-info); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                            <h3 style="color: var(--accent-info); margin-bottom: 1rem;">📊 SYSTEM LOGS (Last 30 minutes)</h3>
                            <div style="background: var(--bg-surface); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.75rem; max-height: 300px; overflow-y: auto;">
                                ${analysis.system_logs.map(log => `<div style="margin-bottom: 0.5rem; word-break: break-all; ${log.includes('error') || log.includes('killed') ? 'color: var(--accent-critical);' : ''}">${this.escapeHtml(log)}</div>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${analysis.error_logs && analysis.error_logs.length > 0 ? `
                        <div style="background: var(--bg-primary); border: 1px solid var(--accent-critical); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                            <h3 style="color: var(--accent-critical); margin-bottom: 1rem;">🚨 ERROR LOGS</h3>
                            <div style="background: var(--bg-surface); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.75rem; max-height: 300px; overflow-y: auto;">
                                ${analysis.error_logs.map(log => `<div style="margin-bottom: 0.5rem; word-break: break-all; color: var(--accent-critical);">${this.escapeHtml(log)}</div>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${analysis.kernel_messages && analysis.kernel_messages.length > 0 ? `
                        <div style="background: var(--bg-primary); border: 1px solid var(--accent-warning); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                            <h3 style="color: var(--accent-warning); margin-bottom: 1rem;">🔧 KERNEL MESSAGES</h3>
                            <div style="background: var(--bg-surface); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.75rem; max-height: 200px; overflow-y: auto;">
                                ${analysis.kernel_messages.map(msg => `<div style="margin-bottom: 0.5rem; word-break: break-all;">${this.escapeHtml(msg)}</div>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${analysis.memory_pressure_data && analysis.memory_pressure_data.length > 0 ? `
                        <div style="background: var(--bg-primary); border: 1px solid var(--accent-success); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                            <h3 style="color: var(--accent-success); margin-bottom: 1rem;">🧠 MEMORY PRESSURE DATA</h3>
                            <div style="background: var(--bg-surface); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.9rem;">
                                ${analysis.memory_pressure_data.map(line => `<div style="margin-bottom: 0.5rem; ${line.includes('CRITICAL') ? 'color: var(--accent-critical); font-weight: bold;' : line.includes('HIGH') ? 'color: var(--accent-warning); font-weight: bold;' : line.includes('🔴') ? 'color: var(--accent-critical);' : ''}">${this.escapeHtml(line)}</div>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${analysis.raw_crash_data ? `
                        <div style="background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                            <h3 style="color: var(--text-secondary); margin-bottom: 1rem;">📄 RAW CRASH DATA (First 2000 chars)</h3>
                            <div style="background: var(--bg-surface); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.7rem; max-height: 400px; overflow-y: auto; white-space: pre-wrap; word-break: break-all;">
                                ${this.escapeHtml(analysis.raw_crash_data)}
                            </div>
                        </div>
                    ` : ''}

                    ${analysis.intelligent_solutions && analysis.intelligent_solutions.length > 0 ? `
                        <div style="background: var(--bg-primary); border: 1px solid var(--accent-info); border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
                            <h3 style="color: var(--accent-info); margin-bottom: 1rem;">💡 INTELLIGENT SOLUTIONS ${analysis.solutions_database && analysis.solutions_database.database_available ? '(Database-Driven)' : '(Fallback)'}</h3>
                            ${analysis.solutions_database && analysis.solutions_database.database_available ? `
                                <div style="background: var(--bg-surface); padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.9rem;">
                                    <strong style="color: var(--accent-success);">📊 Solutions Database:</strong>
                                    ${analysis.solutions_database.solutions_found} solutions found from ${analysis.solutions_database.total_solutions} total
                                    (${analysis.solutions_database.verified_solutions} verified)
                                </div>
                            ` : ''}
                            ${analysis.intelligent_solutions.map((solution, index) => `
                                <div style="background: var(--bg-surface); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; border-left: 4px solid ${solution.severity === 'HIGH' || solution.severity === 'CRITICAL' ? 'var(--accent-critical)' : solution.severity === 'MEDIUM' ? 'var(--accent-warning)' : 'var(--accent-success)'};">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                        <h4 style="color: var(--text-primary); margin: 0;">${solution.title}</h4>
                                        <div style="display: flex; gap: 0.5rem; align-items: center;">
                                            ${solution.verified ? '<span style="background: var(--accent-success); color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.7rem;">✅ VERIFIED</span>' : ''}
                                            <span style="background: ${solution.severity === 'HIGH' || solution.severity === 'CRITICAL' ? 'var(--accent-critical)' : solution.severity === 'MEDIUM' ? 'var(--accent-warning)' : 'var(--accent-success)'}; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">${solution.severity}</span>
                                            ${solution.effectiveness ? `<span style="background: var(--accent-info); color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.7rem;">${solution.effectiveness}/10</span>` : ''}
                                        </div>
                                    </div>
                                    <p style="color: var(--text-secondary); margin-bottom: 1rem;">${solution.description}</p>
                                    <div style="background: var(--bg-primary); padding: 0.75rem; border-radius: 6px; font-family: monospace; font-size: 0.9rem;">
                                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                            <span><strong style="color: var(--accent-info);">Category:</strong> ${solution.category}</span>
                                            <span><strong style="color: var(--accent-info);">Source:</strong> ${solution.source || 'unknown'}</span>
                                        </div>
                                        <strong style="color: var(--accent-info);">Commands:</strong><br>
                                        ${solution.commands && solution.commands.length > 0 ? solution.commands.map(cmd => `<code style="display: block; margin: 0.25rem 0; padding: 0.25rem; background: var(--bg-surface); border-radius: 3px; user-select: text;">${this.escapeHtml(cmd)}</code>`).join('') : '<em style="color: var(--text-secondary);">No commands specified</em>'}
                                        ${solution.source_url ? `<div style="margin-top: 0.5rem;"><a href="${solution.source_url}" target="_blank" style="color: var(--accent-info); text-decoration: none; font-size: 0.8rem;">📖 View Source</a></div>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}

                    <div class="recommendations">
                        <h4>🔧 Recommended Actions</h4>
                        <ul>
                            ${(analysis.recommendations || []).map(rec => `<li>${rec}</li>`).join('')}
                        </ul>
                    </div>

                    ${analysis.clipboard_correlations && analysis.clipboard_correlations.length > 0 ? `
                        <div class="correlations">
                            <h4>🔗 Clipboard Correlations</h4>
                            ${analysis.clipboard_correlations.slice(0, 5).map(corr => `
                                <div class="correlation-item">
                                    <span class="correlation-strength ${this.getStrengthClass(corr.correlation_strength)}">
                                        ${Math.round(corr.correlation_strength)}% correlation
                                    </span>
                                    <p style="margin-top: 0.5rem; font-size: 0.9rem;">
                                        <strong>Content:</strong> ${this.escapeHtml(corr.clipboard_entry.content.substring(0, 100))}...
                                    </p>
                                    <p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                        ${Math.round(corr.time_difference_minutes)} minutes before crash
                                    </p>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}

                    <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-primary); border-radius: 8px;">
                        <h4 style="color: var(--accent-warning); margin-bottom: 0.5rem;">Root Cause</h4>
                        <p>${analysis.root_cause || 'Unable to determine root cause'}</p>
                    </div>
                `;

                resultDiv.innerHTML = html;
                resultDiv.classList.add('show');
            }

            async loadCrashSummary() {
                const summaryDiv = document.getElementById('crashSummary');

                try {
                    const response = await fetch('/api/crash-summary');
                    const summary = await response.json();

                    const html = `
                        <div class="crash-info">
                            <div class="info-card">
                                <h4>Total Crashes</h4>
                                <p>${summary.total_crashes || 0}</p>
                            </div>
                            <div class="info-card">
                                <h4>Recent Crashes (24h)</h4>
                                <p>${(summary.recent_crashes || []).length}</p>
                            </div>
                            <div class="info-card">
                                <h4>Most Common Type</h4>
                                <p>${this.getMostCommonType(summary.crash_types)}</p>
                            </div>
                            <div class="info-card">
                                <h4>System Status</h4>
                                <p style="color: var(--accent-success)">Monitoring Active</p>
                            </div>
                        </div>

                        ${(summary.consolidated_recommendations || []).length > 0 ? `
                            <div class="recommendations">
                                <h4>🎯 Top Recommendations</h4>
                                <ul>
                                    ${summary.consolidated_recommendations.slice(0, 5).map(([rec, count]) =>
                                        `<li>${rec} <span style="color: var(--text-secondary);">(${count}x)</span></li>`
                                    ).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    `;

                    summaryDiv.innerHTML = html;

                } catch (error) {
                    summaryDiv.innerHTML = `<div class="error">Failed to load crash summary: ${error.message}</div>`;
                }
            }

            showError(message) {
                const resultDiv = document.getElementById('analysisResult');
                resultDiv.innerHTML = `<div class="error">❌ ${message}</div>`;
                resultDiv.classList.add('show');
            }

            getSeverityColor(severity) {
                const colors = {
                    'critical': 'var(--accent-critical)',
                    'high': 'var(--accent-warning)',
                    'medium': 'var(--accent-info)',
                    'low': 'var(--accent-success)'
                };
                return colors[severity] || 'var(--text-primary)';
            }

            getStrengthClass(strength) {
                if (strength > 70) return 'strength-high';
                if (strength > 40) return 'strength-medium';
                return 'strength-low';
            }

            getMostCommonType(crashTypes) {
                if (!crashTypes || Object.keys(crashTypes).length === 0) return 'None';
                const sorted = Object.entries(crashTypes).sort((a, b) => b[1] - a[1]);
                return sorted[0] ? sorted[0][0] : 'None';
            }

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        }

        // Global functions
        function analyzeCrash() {
            window.crashAnalyzer.analyzeCrash();
        }

        function analyzeDefaultCrash() {
            window.crashAnalyzer.analyzeDefaultCrash();
        }

        function loadCrashSummary() {
            window.crashAnalyzer.loadCrashSummary();
        }

        function executeSolution(solution, dryRun = true) {
            window.crashAnalyzer.executeSolution(solution, dryRun);
        }

        function showSolutionDetails(solution) {
            window.crashAnalyzer.showSolutionDetails(solution);
        }

        async function collectSudoLogs() {
            try {
                // Show loading message
                const resultDiv = document.getElementById('analysisResult');
                resultDiv.innerHTML = `
                    <div style="background: var(--accent-warning); color: white; padding: 1.5rem; border-radius: 8px; text-align: center;">
                        <h3>🔐 Opening Terminal for Sudo Access</h3>
                        <p>Terminal windows will open for system log collection.</p>
                        <p><strong>Please enter your sudo password when prompted.</strong></p>
                        <p>After entering passwords, click "Check Results" below.</p>
                        <button onclick="checkSudoResults()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: white; color: var(--accent-warning); border: none; border-radius: 4px; cursor: pointer;">
                            🔍 Check Results
                        </button>
                    </div>
                `;
                resultDiv.classList.add('show');

                // Trigger terminal opening
                const response = await fetch('/api/collect-sudo-logs');
                const result = await response.json();

                if (result.error) {
                    resultDiv.innerHTML = `<div style="background: var(--accent-critical); color: white; padding: 1rem; border-radius: 8px;">❌ ${result.error}</div>`;
                } else {
                    // Update message with success
                    resultDiv.innerHTML = `
                        <div style="background: var(--accent-success); color: white; padding: 1.5rem; border-radius: 8px; text-align: center;">
                            <h3>✅ Terminal Windows Opened</h3>
                            <p>${result.message}</p>
                            <p><strong>${result.instructions}</strong></p>
                            <button onclick="checkSudoResults()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: white; color: var(--accent-success); border: none; border-radius: 4px; cursor: pointer;">
                                🔍 Check Results
                            </button>
                        </div>
                    `;
                }

            } catch (error) {
                const resultDiv = document.getElementById('analysisResult');
                resultDiv.innerHTML = `<div style="background: var(--accent-critical); color: white; padding: 1rem; border-radius: 8px;">❌ Failed to open terminal: ${error.message}</div>`;
                resultDiv.classList.add('show');
            }
        }

        async function checkSudoResults() {
            try {
                const response = await fetch('/api/check-sudo-results');
                const result = await response.json();

                const resultDiv = document.getElementById('analysisResult');

                if (result.status === 'complete') {
                    resultDiv.innerHTML = `
                        <div style="background: var(--accent-success); color: white; padding: 1.5rem; border-radius: 8px; text-align: center;">
                            <h3>✅ Sequential Execution Complete!</h3>
                            <p>${result.message}</p>
                            <p><strong>All sudo commands executed successfully in single terminal.</strong></p>
                            ${result.files_collected ? `<p>📁 Files collected: ${result.files_collected.join(', ')}</p>` : ''}
                            ${result.output_directory ? `<p>📂 Output directory: ${result.output_directory}</p>` : ''}
                            <button onclick="analyzeCrash()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: white; color: var(--accent-success); border: none; border-radius: 4px; cursor: pointer;">
                                📊 Analyze Crash with Collected Data
                            </button>
                        </div>
                    `;
                } else if (result.status === 'in_progress') {
                    resultDiv.innerHTML = `
                        <div style="background: var(--accent-warning); color: white; padding: 1.5rem; border-radius: 8px; text-align: center;">
                            <h3>🔄 Sequential Execution in Progress</h3>
                            <p>${result.message}</p>
                            <p>Commands are running automatically in the single terminal window.</p>
                            ${result.files_collected ? `<p>📁 Files completed: ${result.files_collected.join(', ')}</p>` : ''}
                            <button onclick="checkSudoResults()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: white; color: var(--accent-warning); border: none; border-radius: 4px; cursor: pointer;">
                                🔍 Check Progress
                            </button>
                        </div>
                    `;
                } else if (result.status === 'pending') {
                    resultDiv.innerHTML = `
                        <div style="background: var(--accent-warning); color: white; padding: 1.5rem; border-radius: 8px; text-align: center;">
                            <h3>⏳ Waiting for Sequential Execution</h3>
                            <p>${result.message}</p>
                            <p>Please enter your sudo password in the single terminal window.</p>
                            <button onclick="checkSudoResults()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: white; color: var(--accent-warning); border: none; border-radius: 4px; cursor: pointer;">
                                🔍 Check Again
                            </button>
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<div style="background: var(--accent-critical); color: white; padding: 1rem; border-radius: 8px;">❌ ${result.error || 'Unknown error'}</div>`;
                }

            } catch (error) {
                const resultDiv = document.getElementById('analysisResult');
                resultDiv.innerHTML = `<div style="background: var(--accent-critical); color: white; padding: 1rem; border-radius: 8px;">❌ Failed to check results: ${error.message}</div>`;
            }
        }

        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', () => {
            window.crashAnalyzer = new CrashAnalyzer();
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("💥 Starting Crash Analysis Correlator...")
    print("=" * 60)
    print("🎯 ADVANCED CRASH ANALYSIS & CORRELATION")
    print("📊 VSCode crash analysis and system correlation")
    print("🔗 Clipboard data correlation with crashes")
    print("")
    print("🚀 Features:")
    print("• Verbose crash data analysis")
    print("• Timeline correlation with clipboard")
    print("• Root cause identification")
    print("• Automated recommendations")
    print("• Predictive crash detection")
    print("")
    print("📱 ACCESS: http://localhost:9000")
    print("=" * 60)

# Add missing routes for solution URLs
@app.route('/official_documentation')
def official_documentation():
    """Redirect to actual VSCode documentation"""
    from flask import redirect
    return redirect('https://code.visualstudio.com/docs/supporting/FAQ#_vs-code-is-blank')

@app.route('/api/solution/<solution_id>')
def get_solution_details(solution_id):
    """Get detailed information about a specific solution"""
    try:
        if crash_correlator.solutions_db:
            solution = crash_correlator.solutions_db.get_solution_by_id(solution_id)
            if solution:
                return jsonify(solution)
        return jsonify({'error': 'Solution not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=False)
