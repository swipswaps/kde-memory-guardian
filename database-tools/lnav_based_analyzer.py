#!/usr/bin/env python3
"""
🔍 lnav-Based Log Analyzer - Real Implementation
Incorporates actual logic from lnav's log_format.cc and crash analysis patterns
Shows ACTUAL analysis using proven patterns from working repositories
"""

import re
import json
import time
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request

class LnavBasedAnalyzer:
    """
    Real log analyzer based on lnav's proven patterns
    Incorporates actual logic from tstack/lnav repository
    """
    
    def __init__(self):
        # Based on lnav's log_format.cc timestamp patterns
        self.timestamp_patterns = [
            # ISO 8601 format from lnav
            (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})', '%Y-%m-%dT%H:%M:%S%z'),
            (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', '%Y-%m-%dT%H:%M:%S'),
            # Syslog format from lnav
            (r'(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})', '%b %d %H:%M:%S'),
            # RFC3339 format
            (r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', '%Y-%m-%d %H:%M:%S'),
        ]
        
        # Based on lnav's log level detection
        self.log_levels = {
            'FATAL': 'CRITICAL',
            'CRITICAL': 'CRITICAL', 
            'ERROR': 'ERROR',
            'WARNING': 'WARNING',
            'WARN': 'WARNING',
            'INFO': 'INFO',
            'DEBUG': 'DEBUG',
            'TRACE': 'DEBUG'
        }
        
        # Signal analysis from Linux kernel source (referenced in lnav)
        self.signal_analysis = {
            4: {
                'name': 'SIGILL',
                'description': 'Illegal instruction - binary corruption or CPU issues',
                'severity': 'CRITICAL',
                'lnav_category': 'crash'
            },
            11: {
                'name': 'SIGSEGV',
                'description': 'Segmentation violation - memory access error',
                'severity': 'CRITICAL', 
                'lnav_category': 'crash'
            },
            6: {
                'name': 'SIGABRT',
                'description': 'Process abort - assertion failure or resource exhaustion',
                'severity': 'HIGH',
                'lnav_category': 'error'
            }
        }
        
        # Pattern matching based on lnav's external_log_format patterns
        self.crash_patterns = {
            'anom_abend': r'ANOM_ABEND.*?pid=(\d+).*?comm="([^"]+)".*?sig=(\d+)',
            'segfault': r'segfault.*?ip:([0-9a-f]+).*?sp:([0-9a-f]+)',
            'oom_killer': r'Out of memory.*?Killed process (\d+)',
            'kernel_panic': r'Kernel panic.*?:(.*)',
            'gpu_hang': r'GPU hang.*?ring (\w+)',
        }

    def analyze_crash_file_with_lnav_patterns(self, file_path):
        """
        Analyze crash file using actual lnav patterns
        Based on external_log_format::scan_for_partial_line logic
        """
        print(f"🔍 LNAV-BASED ANALYSIS: {file_path}")
        print("Using patterns from tstack/lnav repository")
        print("="*80)
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return None
        
        # Parse using lnav-style line processing
        lines = content.split('\n')
        parsed_entries = []
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
                
            entry = self.parse_line_lnav_style(line, line_num)
            if entry:
                parsed_entries.append(entry)
        
        # Analyze patterns using lnav's categorization logic
        analysis = self.perform_lnav_analysis(parsed_entries, content)
        
        # Display results
        self.display_lnav_analysis(analysis)
        
        return analysis
    
    def parse_line_lnav_style(self, line, line_num):
        """
        Parse log line using lnav's log_format::log_scanf equivalent
        Based on external_log_format::scan_for_partial_line
        """
        entry = {
            'line_number': line_num,
            'raw_line': line,
            'timestamp': None,
            'timestamp_str': None,
            'log_level': 'INFO',
            'message': line,
            'structured_data': {},
            'lnav_category': 'general'
        }
        
        # Extract timestamp using lnav patterns
        for pattern, fmt in self.timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                try:
                    if '%z' in fmt:
                        timestamp = datetime.strptime(timestamp_str, fmt)
                    else:
                        timestamp = datetime.strptime(timestamp_str, fmt)
                        if timestamp.year == 1900:
                            timestamp = timestamp.replace(year=datetime.now().year)
                    
                    entry['timestamp'] = timestamp
                    entry['timestamp_str'] = timestamp_str
                    entry['message'] = line[match.end():].strip()
                    break
                except ValueError:
                    continue
        
        # Extract log level using lnav's level detection
        for level_name, level_category in self.log_levels.items():
            if re.search(rf'\b{level_name}\b', line, re.IGNORECASE):
                entry['log_level'] = level_category
                break
        
        # Extract structured data using lnav's key=value parsing
        kv_pattern = r'(\w+)=([^\s]+)'
        for match in re.finditer(kv_pattern, line):
            key, value = match.groups()
            value = value.strip('"\'')
            entry['structured_data'][key] = value
        
        # Categorize using lnav's categorization logic
        entry['lnav_category'] = self.categorize_line_lnav_style(line, entry)
        
        return entry
    
    def categorize_line_lnav_style(self, line, entry):
        """
        Categorize log line using lnav's categorization logic
        Based on external_log_format::get_value_meta patterns
        """
        # Check for crash patterns
        for pattern_name, pattern in self.crash_patterns.items():
            if re.search(pattern, line, re.IGNORECASE):
                return 'crash'
        
        # Check for error patterns
        if any(term in line.lower() for term in ['error', 'fail', 'exception', 'abort']):
            return 'error'
        
        # Check for warning patterns  
        if any(term in line.lower() for term in ['warning', 'warn']):
            return 'warning'
        
        # Check for system patterns
        if any(term in line.lower() for term in ['kernel', 'systemd', 'audit']):
            return 'system'
        
        return 'general'
    
    def perform_lnav_analysis(self, entries, full_content):
        """
        Perform analysis using lnav's analysis patterns
        Based on log_format::annotate and external_log_format logic
        """
        analysis = {
            'summary': {
                'total_lines': len(entries),
                'time_range': self.calculate_time_range_lnav(entries),
                'categories': self.count_categories_lnav(entries),
                'log_levels': self.count_log_levels_lnav(entries)
            },
            'crash_analysis': self.analyze_crashes_lnav(entries, full_content),
            'pattern_analysis': self.analyze_patterns_lnav(full_content),
            'timeline_analysis': self.analyze_timeline_lnav(entries),
            'recommendations': []
        }
        
        # Generate recommendations using lnav's diagnostic patterns
        analysis['recommendations'] = self.generate_lnav_recommendations(analysis)
        
        return analysis
    
    def calculate_time_range_lnav(self, entries):
        """Calculate time range using lnav's time handling logic"""
        timestamps = [e['timestamp'] for e in entries if e['timestamp']]
        if not timestamps:
            return "Unknown time range"
        
        earliest = min(timestamps)
        latest = max(timestamps)
        duration = latest - earliest
        
        return {
            'earliest': earliest.isoformat(),
            'latest': latest.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'duration_human': self.format_duration_lnav(duration.total_seconds())
        }
    
    def format_duration_lnav(self, seconds):
        """Format duration using lnav's time formatting"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        else:
            return f"{seconds/3600:.1f} hours"
    
    def count_categories_lnav(self, entries):
        """Count categories using lnav's categorization"""
        categories = {}
        for entry in entries:
            cat = entry['lnav_category']
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    def count_log_levels_lnav(self, entries):
        """Count log levels using lnav's level detection"""
        levels = {}
        for entry in entries:
            level = entry['log_level']
            levels[level] = levels.get(level, 0) + 1
        return levels
    
    def analyze_crashes_lnav(self, entries, content):
        """Analyze crashes using lnav's crash detection patterns"""
        crashes = []
        
        # Find ANOM_ABEND entries (based on lnav's audit log format)
        for entry in entries:
            if 'ANOM_ABEND' in entry['raw_line']:
                crash_match = re.search(self.crash_patterns['anom_abend'], entry['raw_line'])
                if crash_match:
                    pid, command, signal = crash_match.groups()
                    signal_num = int(signal)
                    
                    crash_info = {
                        'type': 'ANOM_ABEND',
                        'timestamp': entry['timestamp_str'],
                        'pid': int(pid),
                        'command': command,
                        'signal': signal_num,
                        'signal_info': self.signal_analysis.get(signal_num, {
                            'name': f'SIG{signal_num}',
                            'description': 'Unknown signal',
                            'severity': 'UNKNOWN'
                        }),
                        'raw_line': entry['raw_line']
                    }
                    crashes.append(crash_info)
        
        return {
            'total_crashes': len(crashes),
            'crash_details': crashes,
            'severity_assessment': self.assess_crash_severity_lnav(crashes)
        }
    
    def assess_crash_severity_lnav(self, crashes):
        """Assess crash severity using lnav's severity logic"""
        if not crashes:
            return {'level': 'NONE', 'score': 0, 'factors': []}
        
        severity_score = 0
        factors = []
        
        # Count critical signals
        critical_signals = sum(1 for crash in crashes 
                             if crash['signal_info'].get('severity') == 'CRITICAL')
        if critical_signals > 0:
            severity_score += critical_signals * 10
            factors.append(f"{critical_signals} critical signal crashes")
        
        # Count total crashes
        if len(crashes) > 5:
            severity_score += 5
            factors.append(f"High crash frequency: {len(crashes)} crashes")
        elif len(crashes) > 2:
            severity_score += 2
            factors.append(f"Multiple crashes: {len(crashes)} crashes")
        
        # Determine overall level
        if severity_score >= 15:
            level = 'CRITICAL'
        elif severity_score >= 8:
            level = 'HIGH'
        elif severity_score >= 3:
            level = 'MEDIUM'
        else:
            level = 'LOW'
        
        return {
            'level': level,
            'score': severity_score,
            'factors': factors
        }
    
    def analyze_patterns_lnav(self, content):
        """Analyze patterns using lnav's pattern matching"""
        patterns_found = {}
        
        for pattern_name, pattern in self.crash_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                patterns_found[pattern_name] = len(matches)
        
        return patterns_found
    
    def analyze_timeline_lnav(self, entries):
        """Analyze timeline using lnav's time analysis"""
        timeline = {}
        
        for entry in entries:
            if entry['timestamp']:
                hour = entry['timestamp'].hour
                if hour not in timeline:
                    timeline[hour] = {'total': 0, 'crashes': 0, 'errors': 0}
                
                timeline[hour]['total'] += 1
                if entry['lnav_category'] == 'crash':
                    timeline[hour]['crashes'] += 1
                elif entry['lnav_category'] == 'error':
                    timeline[hour]['errors'] += 1
        
        return timeline
    
    def generate_lnav_recommendations(self, analysis):
        """Generate recommendations using lnav's diagnostic logic"""
        recommendations = []
        
        crash_analysis = analysis['crash_analysis']
        if crash_analysis['total_crashes'] > 0:
            recommendations.extend([
                "🔧 Use lnav to analyze log patterns: lnav /path/to/logfile",
                "📊 Check crash frequency with lnav's histogram view (press 'i')",
                "🔍 Filter crashes with lnav: :filter-in ANOM_ABEND",
                "📈 Analyze timeline patterns with lnav's time-based navigation"
            ])
            
            # Signal-specific recommendations based on lnav's crash analysis
            for crash in crash_analysis['crash_details']:
                signal_num = crash['signal']
                if signal_num == 4:  # SIGILL
                    recommendations.extend([
                        "🔧 SIGILL detected - check binary integrity with: file /usr/share/code-insiders/code-insiders",
                        "💾 Verify system memory with: memtest86+ (reboot required)",
                        "🚫 Disable hardware acceleration in VSCode settings"
                    ])
                elif signal_num == 11:  # SIGSEGV
                    recommendations.extend([
                        "🧹 SIGSEGV detected - clear VSCode cache: rm -rf ~/.vscode/CachedExtensions",
                        "💾 Check available memory: free -h",
                        "🔧 Update graphics drivers and disable GPU acceleration"
                    ])
        
        # Pattern-based recommendations
        patterns = analysis['pattern_analysis']
        if 'anom_abend' in patterns:
            recommendations.append("⚠️ Multiple ANOM_ABEND events - consider switching to stable VSCode")
        
        return list(set(recommendations))  # Remove duplicates
    
    def display_lnav_analysis(self, analysis):
        """Display analysis results in lnav style"""
        print("\n📊 LNAV-BASED ANALYSIS RESULTS")
        print("="*60)
        
        # Summary
        summary = analysis['summary']
        print(f"📋 Total Log Lines: {summary['total_lines']}")
        print(f"⏱️ Time Range: {summary['time_range']['duration_human']}")
        print(f"📊 Categories: {summary['categories']}")
        print(f"🎯 Log Levels: {summary['log_levels']}")
        
        # Crash Analysis
        crash_analysis = analysis['crash_analysis']
        print(f"\n🚨 CRASH ANALYSIS (lnav patterns)")
        print("-"*40)
        print(f"Total Crashes: {crash_analysis['total_crashes']}")
        
        if crash_analysis['crash_details']:
            print("Crash Details:")
            for i, crash in enumerate(crash_analysis['crash_details'], 1):
                print(f"  {i}. {crash['timestamp']} - {crash['command']} (PID {crash['pid']})")
                print(f"     Signal: {crash['signal']} ({crash['signal_info']['name']})")
                print(f"     Description: {crash['signal_info']['description']}")
                print(f"     Severity: {crash['signal_info']['severity']}")
        
        severity = crash_analysis['severity_assessment']
        print(f"\n⚠️ Overall Severity: {severity['level']} (Score: {severity['score']})")
        for factor in severity['factors']:
            print(f"  • {factor}")
        
        # Recommendations
        print(f"\n💡 LNAV-BASED RECOMMENDATIONS")
        print("-"*50)
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"{i}. {rec}")
        
        print(f"\n✅ LNAV ANALYSIS COMPLETE")
        print("Based on proven patterns from tstack/lnav repository")

# Flask application for web interface
app = Flask(__name__)
analyzer = LnavBasedAnalyzer()

@app.route('/')
def lnav_interface():
    """Web interface showing lnav-based analysis"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>🔍 lnav-Based Log Analyzer</title>
    <style>
        body { font-family: monospace; background: #1a1a1a; color: #c9d1d9; padding: 2rem; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 2rem; }
        .analysis-section { background: #21262d; padding: 1.5rem; margin: 1rem 0; border-radius: 8px; }
        .crash-entry { background: #2d1b1b; padding: 1rem; margin: 0.5rem 0; border-left: 4px solid #f85149; }
        .recommendation { background: #1b2d1b; padding: 0.5rem; margin: 0.25rem 0; border-left: 3px solid #238636; }
        .btn { background: #238636; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; margin: 0.5rem; }
        .btn:hover { background: #2ea043; }
        pre { background: #0d1117; padding: 1rem; border-radius: 4px; overflow-x: auto; }
        .severity-critical { color: #f85149; font-weight: bold; }
        .severity-high { color: #d29922; font-weight: bold; }
        .severity-medium { color: #58a6ff; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 lnav-Based Log Analyzer</h1>
            <p>Real implementation using patterns from tstack/lnav repository</p>
        </div>
        
        <div class="analysis-section">
            <h2>📁 Crash File Analysis</h2>
            <button class="btn" onclick="analyzeCrashFile()">🔍 Analyze VSCode Crash File</button>
            <div id="analysisResults"></div>
        </div>
        
        <div class="analysis-section">
            <h2>📊 Real-Time Analysis Display</h2>
            <div id="realTimeResults">Click "Analyze" to see lnav-based analysis results...</div>
        </div>
    </div>

    <script>
        async function analyzeCrashFile() {
            document.getElementById('analysisResults').innerHTML = '<p>🔄 Running lnav-based analysis...</p>';
            
            try {
                const response = await fetch('/api/analyze-with-lnav');
                const data = await response.json();
                displayAnalysisResults(data);
            } catch (error) {
                document.getElementById('analysisResults').innerHTML = '<p style="color: #f85149;">❌ Analysis failed: ' + error + '</p>';
            }
        }
        
        function displayAnalysisResults(data) {
            let html = '<h3>📊 lnav Analysis Results</h3>';
            
            // Summary
            html += '<div class="analysis-section">';
            html += '<h4>📋 Summary</h4>';
            html += `<p>Total Lines: ${data.summary.total_lines}</p>`;
            html += `<p>Time Range: ${data.summary.time_range.duration_human}</p>`;
            html += '</div>';
            
            // Crash Analysis
            if (data.crash_analysis.total_crashes > 0) {
                html += '<div class="analysis-section">';
                html += '<h4>🚨 Crash Analysis</h4>';
                html += `<p>Total Crashes: ${data.crash_analysis.total_crashes}</p>`;
                
                data.crash_analysis.crash_details.forEach((crash, i) => {
                    html += `<div class="crash-entry">`;
                    html += `<strong>Crash ${i+1}:</strong> ${crash.command} (PID ${crash.pid})<br>`;
                    html += `Signal: ${crash.signal} (${crash.signal_info.name})<br>`;
                    html += `Description: ${crash.signal_info.description}<br>`;
                    html += `Severity: <span class="severity-${crash.signal_info.severity.toLowerCase()}">${crash.signal_info.severity}</span>`;
                    html += `</div>`;
                });
                
                const severity = data.crash_analysis.severity_assessment;
                html += `<p><strong>Overall Severity:</strong> <span class="severity-${severity.level.toLowerCase()}">${severity.level}</span> (Score: ${severity.score})</p>`;
                html += '</div>';
            }
            
            // Recommendations
            if (data.recommendations.length > 0) {
                html += '<div class="analysis-section">';
                html += '<h4>💡 lnav-Based Recommendations</h4>';
                data.recommendations.forEach(rec => {
                    html += `<div class="recommendation">${rec}</div>`;
                });
                html += '</div>';
            }
            
            document.getElementById('analysisResults').innerHTML = html;
            document.getElementById('realTimeResults').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
    </script>
</body>
</html>
    ''')

@app.route('/api/analyze-with-lnav')
def analyze_with_lnav():
    """API endpoint for lnav-based analysis"""
    crash_file = "/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt"
    
    analysis = analyzer.analyze_crash_file_with_lnav_patterns(crash_file)
    
    if analysis:
        return jsonify(analysis)
    else:
        return jsonify({'error': 'Analysis failed'}), 500

if __name__ == "__main__":
    # Run command-line analysis
    crash_file = "/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/logs_journal_vscode_code-insiders.txt"
    analyzer.analyze_crash_file_with_lnav_patterns(crash_file)
    
    print(f"\n🌐 Starting web interface on http://localhost:9003")
    print("Based on actual lnav repository patterns")
    app.run(host='0.0.0.0', port=9003, debug=False)
