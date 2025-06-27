#!/usr/bin/env python3
"""
🔍 Actual Crash Analyzer - Real Analysis Display
Based on lnav's log analysis patterns and crash-analysis tools from GitHub
Shows ACTUAL analysis of real crash data, not frameworks
"""

import re
import json
from datetime import datetime
from pathlib import Path

class ActualCrashAnalyzer:
    """
    Real crash analyzer that displays actual analysis
    Based on patterns from lnav, systemd-analyze, and crash analysis tools
    """
    
    def __init__(self):
        # Signal definitions from Linux kernel source
        self.signal_meanings = {
            4: {
                'name': 'SIGILL',
                'description': 'Illegal instruction',
                'common_causes': [
                    'Corrupted binary or shared library',
                    'CPU architecture mismatch',
                    'Memory corruption affecting code segment',
                    'JIT compilation errors',
                    'Hardware CPU errors'
                ],
                'severity': 'CRITICAL'
            },
            11: {
                'name': 'SIGSEGV', 
                'description': 'Segmentation violation',
                'common_causes': [
                    'Null pointer dereference',
                    'Buffer overflow/underflow',
                    'Use after free',
                    'Stack overflow',
                    'Memory corruption'
                ],
                'severity': 'CRITICAL'
            },
            6: {
                'name': 'SIGABRT',
                'description': 'Process abort signal',
                'common_causes': [
                    'Assertion failure',
                    'Memory allocation failure',
                    'Unhandled exception',
                    'Resource exhaustion',
                    'Deliberate abort() call'
                ],
                'severity': 'HIGH'
            }
        }
        
        # VSCode-specific patterns from GitHub issues analysis
        self.vscode_patterns = {
            'electron_crash': r'electron.*crash|renderer.*crash',
            'memory_exhaustion': r'out of memory|oom|memory.*exhausted',
            'gpu_issues': r'gpu.*error|webgl.*error|graphics.*error',
            'extension_crash': r'extension.*crash|addon.*crash',
            'file_corruption': r'corrupt.*file|invalid.*file|bad.*file'
        }
    
    def analyze_crash_file(self, file_path):
        """Analyze actual crash file and display real analysis"""
        print(f"🔍 ANALYZING ACTUAL CRASH FILE: {file_path}")
        print("="*80)
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return None
        
        # Extract crash events
        crash_events = self.extract_crash_events(content)
        
        # Analyze patterns
        analysis = self.perform_crash_analysis(crash_events, content)
        
        # Display analysis
        self.display_analysis(analysis)
        
        return analysis
    
    def extract_crash_events(self, content):
        """Extract actual crash events from log content"""
        events = []
        
        # Pattern for ANOM_ABEND events (based on audit log format)
        anom_pattern = r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}).*?ANOM_ABEND.*?pid=(\d+).*?comm="([^"]+)".*?sig=(\d+)'
        
        for match in re.finditer(anom_pattern, content):
            timestamp_str, pid, command, signal = match.groups()
            
            # Parse timestamp (add current year)
            try:
                timestamp = datetime.strptime(f"2025 {timestamp_str}", "%Y %b %d %H:%M:%S")
            except:
                timestamp = None
            
            event = {
                'timestamp': timestamp,
                'timestamp_str': timestamp_str,
                'pid': int(pid),
                'command': command,
                'signal': int(signal),
                'raw_line': match.group(0)
            }
            events.append(event)
        
        return events
    
    def perform_crash_analysis(self, crash_events, full_content):
        """Perform actual analysis of crash patterns"""
        analysis = {
            'crash_summary': {},
            'signal_analysis': {},
            'timeline_analysis': {},
            'pattern_analysis': {},
            'severity_assessment': {},
            'recommendations': []
        }
        
        if not crash_events:
            analysis['crash_summary'] = {'status': 'No crash events found'}
            return analysis
        
        # Crash Summary
        analysis['crash_summary'] = {
            'total_crashes': len(crash_events),
            'unique_signals': len(set(event['signal'] for event in crash_events)),
            'affected_processes': len(set(event['pid'] for event in crash_events)),
            'time_span': self.calculate_time_span(crash_events),
            'crash_frequency': self.calculate_frequency(crash_events)
        }
        
        # Signal Analysis
        signal_counts = {}
        for event in crash_events:
            sig = event['signal']
            if sig not in signal_counts:
                signal_counts[sig] = []
            signal_counts[sig].append(event)
        
        analysis['signal_analysis'] = {}
        for signal, events in signal_counts.items():
            signal_info = self.signal_meanings.get(signal, {
                'name': f'SIG{signal}',
                'description': 'Unknown signal',
                'common_causes': ['Unknown'],
                'severity': 'UNKNOWN'
            })
            
            analysis['signal_analysis'][signal] = {
                'signal_name': signal_info['name'],
                'description': signal_info['description'],
                'count': len(events),
                'severity': signal_info['severity'],
                'common_causes': signal_info['common_causes'],
                'affected_pids': [e['pid'] for e in events]
            }
        
        # Timeline Analysis
        analysis['timeline_analysis'] = self.analyze_timeline(crash_events)
        
        # Pattern Analysis
        analysis['pattern_analysis'] = self.analyze_patterns(full_content)
        
        # Severity Assessment
        analysis['severity_assessment'] = self.assess_severity(crash_events, analysis)
        
        # Generate Recommendations
        analysis['recommendations'] = self.generate_recommendations(analysis)
        
        return analysis
    
    def calculate_time_span(self, events):
        """Calculate time span of crashes"""
        if len(events) < 2:
            return "Single event"
        
        timestamps = [e['timestamp'] for e in events if e['timestamp']]
        if not timestamps:
            return "Unknown timespan"
        
        earliest = min(timestamps)
        latest = max(timestamps)
        duration = latest - earliest
        
        if duration.total_seconds() < 3600:
            return f"{duration.total_seconds()/60:.1f} minutes"
        else:
            return f"{duration.total_seconds()/3600:.1f} hours"
    
    def calculate_frequency(self, events):
        """Calculate crash frequency"""
        if len(events) < 2:
            return "Single occurrence"
        
        timestamps = [e['timestamp'] for e in events if e['timestamp']]
        if len(timestamps) < 2:
            return "Unknown frequency"
        
        duration = max(timestamps) - min(timestamps)
        if duration.total_seconds() == 0:
            return "Multiple crashes at same time"
        
        frequency = len(events) / (duration.total_seconds() / 3600)  # crashes per hour
        
        if frequency > 10:
            return f"Very high ({frequency:.1f}/hour)"
        elif frequency > 1:
            return f"High ({frequency:.1f}/hour)"
        else:
            return f"Moderate ({frequency:.2f}/hour)"
    
    def analyze_timeline(self, events):
        """Analyze crash timeline patterns"""
        if not events:
            return {}
        
        # Group by time periods
        timeline = {}
        for event in events:
            if event['timestamp']:
                hour = event['timestamp'].hour
                if hour not in timeline:
                    timeline[hour] = []
                timeline[hour].append(event)
        
        # Find patterns
        peak_hours = sorted(timeline.keys(), key=lambda h: len(timeline[h]), reverse=True)
        
        return {
            'crashes_by_hour': {str(h): len(timeline[h]) for h in timeline},
            'peak_crash_hours': peak_hours[:3],
            'pattern': 'Clustered' if len(peak_hours) <= 2 else 'Distributed'
        }
    
    def analyze_patterns(self, content):
        """Analyze content for known patterns"""
        patterns_found = {}
        
        for pattern_name, regex in self.vscode_patterns.items():
            matches = re.findall(regex, content, re.IGNORECASE)
            if matches:
                patterns_found[pattern_name] = len(matches)
        
        return patterns_found
    
    def assess_severity(self, events, analysis):
        """Assess overall severity"""
        severity_score = 0
        factors = []
        
        # Signal severity
        for signal_data in analysis['signal_analysis'].values():
            if signal_data['severity'] == 'CRITICAL':
                severity_score += 10
                factors.append(f"Critical signal: {signal_data['signal_name']}")
            elif signal_data['severity'] == 'HIGH':
                severity_score += 5
                factors.append(f"High severity signal: {signal_data['signal_name']}")
        
        # Frequency severity
        crash_count = analysis['crash_summary']['total_crashes']
        if crash_count > 5:
            severity_score += 5
            factors.append(f"High crash frequency: {crash_count} crashes")
        elif crash_count > 2:
            severity_score += 2
            factors.append(f"Multiple crashes: {crash_count} crashes")
        
        # Determine overall severity
        if severity_score >= 15:
            overall = "CRITICAL"
        elif severity_score >= 8:
            overall = "HIGH"
        elif severity_score >= 3:
            overall = "MEDIUM"
        else:
            overall = "LOW"
        
        return {
            'overall_severity': overall,
            'severity_score': severity_score,
            'contributing_factors': factors
        }
    
    def generate_recommendations(self, analysis):
        """Generate actual recommendations based on analysis"""
        recommendations = []
        
        # Signal-specific recommendations
        for signal, data in analysis['signal_analysis'].items():
            if signal == 4:  # SIGILL
                recommendations.extend([
                    "🔧 Reinstall VSCode Insiders to fix potential binary corruption",
                    "🔍 Check for CPU architecture compatibility issues",
                    "💾 Verify system memory integrity with memtest86",
                    "🚫 Disable hardware acceleration in VSCode settings"
                ])
            elif signal == 11:  # SIGSEGV
                recommendations.extend([
                    "🧹 Clear VSCode extension cache and disable problematic extensions",
                    "💾 Increase system memory or add swap space",
                    "🔧 Update graphics drivers and disable GPU acceleration",
                    "📁 Check for corrupted workspace files"
                ])
            elif signal == 6:  # SIGABRT
                recommendations.extend([
                    "📊 Monitor system resources during VSCode usage",
                    "🔧 Reset VSCode settings to defaults",
                    "🧹 Clear temporary files and caches",
                    "📝 Check VSCode logs for assertion failures"
                ])
        
        # Frequency-based recommendations
        if analysis['crash_summary']['total_crashes'] > 3:
            recommendations.extend([
                "⚠️ Consider switching to stable VSCode instead of Insiders",
                "🔄 Set up automatic crash reporting and monitoring",
                "💾 Implement regular workspace backups"
            ])
        
        return list(set(recommendations))  # Remove duplicates
    
    def display_analysis(self, analysis):
        """Display the actual analysis results"""
        print("\n📊 CRASH ANALYSIS RESULTS")
        print("="*50)
        
        # Crash Summary
        summary = analysis['crash_summary']
        print(f"📋 Total Crashes: {summary.get('total_crashes', 0)}")
        print(f"🎯 Unique Signals: {summary.get('unique_signals', 0)}")
        print(f"🔄 Affected Processes: {summary.get('affected_processes', 0)}")
        print(f"⏱️ Time Span: {summary.get('time_span', 'Unknown')}")
        print(f"📈 Frequency: {summary.get('crash_frequency', 'Unknown')}")
        
        # Signal Analysis
        print(f"\n🚨 SIGNAL ANALYSIS")
        print("-"*30)
        for signal, data in analysis['signal_analysis'].items():
            print(f"Signal {signal} ({data['signal_name']}):")
            print(f"  📝 Description: {data['description']}")
            print(f"  📊 Count: {data['count']}")
            print(f"  ⚠️ Severity: {data['severity']}")
            print(f"  🎯 Affected PIDs: {data['affected_pids']}")
            print(f"  🔍 Common Causes:")
            for cause in data['common_causes']:
                print(f"    • {cause}")
            print()
        
        # Severity Assessment
        severity = analysis['severity_assessment']
        print(f"⚠️ OVERALL SEVERITY: {severity.get('overall_severity', 'UNKNOWN')}")
        print(f"📊 Severity Score: {severity.get('severity_score', 0)}/20")
        print("🔍 Contributing Factors:")
        for factor in severity.get('contributing_factors', []):
            print(f"  • {factor}")
        
        # Recommendations
        print(f"\n💡 ACTIONABLE RECOMMENDATIONS")
        print("-"*40)
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print(f"\n✅ ANALYSIS COMPLETE - {len(analysis['recommendations'])} recommendations generated")

def main():
    """Main function to run actual crash analysis"""
    analyzer = ActualCrashAnalyzer()
    
    # Analyze the actual crash file
    crash_file = "/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt"
    
    print("🎯 ACTUAL CRASH ANALYSIS - NOT A FRAMEWORK")
    print("Based on lnav patterns and Linux crash analysis tools")
    print("="*80)
    
    analysis = analyzer.analyze_crash_file(crash_file)
    
    if analysis:
        print(f"\n📁 Analysis saved to: crash_analysis_results.json")
        with open('crash_analysis_results.json', 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

if __name__ == "__main__":
    main()
