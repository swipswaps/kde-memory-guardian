#!/usr/bin/env python3
"""
🧠 Intelligent Diagnostic Engine
Analyzes error, system, and application messages to provide precise solutions

Features:
- Pattern recognition for common issues
- Solution database with step-by-step fixes
- Real-time system correlation
- Actionable recommendations
- Automated fix suggestions
"""

import os
import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntelligentDiagnosticEngine:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.crash_data_dir = Path("/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457")
        
        # Solution database with precise fixes
        self.solution_database = {
            'memory_exhaustion': {
                'patterns': [
                    r'out of memory',
                    r'memory exhausted',
                    r'cannot allocate memory',
                    r'killed.*memory',
                    r'oom.*killed'
                ],
                'severity': 'HIGH',
                'category': 'Memory Management',
                'solutions': [
                    {
                        'title': 'Immediate Memory Relief',
                        'commands': [
                            'sudo sysctl vm.drop_caches=3',
                            'sudo systemctl restart earlyoom',
                            'pkill -f "code.*--type=renderer"'
                        ],
                        'description': 'Clear system caches and restart memory protection'
                    },
                    {
                        'title': 'VSCode Memory Optimization',
                        'commands': [
                            'code --max-memory=4096',
                            'code --disable-extensions'
                        ],
                        'description': 'Restart VSCode with memory limits and disabled extensions'
                    },
                    {
                        'title': 'System Memory Monitoring',
                        'commands': [
                            'sudo systemctl enable --now nohang',
                            'echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf'
                        ],
                        'description': 'Enable advanced memory protection and optimize swap usage'
                    }
                ]
            },
            'gpu_driver_issues': {
                'patterns': [
                    r'gpu.*error',
                    r'graphics.*driver',
                    r'opengl.*error',
                    r'vulkan.*error',
                    r'dri.*error'
                ],
                'severity': 'MEDIUM',
                'category': 'Graphics/GPU',
                'solutions': [
                    {
                        'title': 'GPU Driver Reset',
                        'commands': [
                            'sudo modprobe -r amdgpu',
                            'sudo modprobe amdgpu',
                            'sudo systemctl restart display-manager'
                        ],
                        'description': 'Reset AMD GPU driver and display manager'
                    },
                    {
                        'title': 'VSCode GPU Acceleration Disable',
                        'commands': [
                            'code --disable-gpu',
                            'code --disable-gpu-sandbox'
                        ],
                        'description': 'Disable GPU acceleration in VSCode to prevent crashes'
                    }
                ]
            },
            'extension_conflicts': {
                'patterns': [
                    r'extension.*error',
                    r'extension.*crash',
                    r'plugin.*error',
                    r'marketplace.*error'
                ],
                'severity': 'MEDIUM',
                'category': 'Extensions',
                'solutions': [
                    {
                        'title': 'Extension Safe Mode',
                        'commands': [
                            'code --disable-extensions',
                            'code --list-extensions --show-versions'
                        ],
                        'description': 'Start VSCode in safe mode and list problematic extensions'
                    },
                    {
                        'title': 'Extension Reset',
                        'commands': [
                            'rm -rf ~/.vscode/extensions',
                            'code --install-extension ms-python.python'
                        ],
                        'description': 'Reset all extensions and reinstall essential ones'
                    }
                ]
            },
            'filesystem_issues': {
                'patterns': [
                    r'no space left',
                    r'disk.*full',
                    r'filesystem.*error',
                    r'permission denied',
                    r'input/output error'
                ],
                'severity': 'HIGH',
                'category': 'Filesystem',
                'solutions': [
                    {
                        'title': 'Disk Space Cleanup',
                        'commands': [
                            'sudo journalctl --vacuum-time=7d',
                            'sudo dnf clean all',
                            'rm -rf ~/.cache/vscode-*'
                        ],
                        'description': 'Clean system logs, package cache, and VSCode cache'
                    },
                    {
                        'title': 'Permission Fix',
                        'commands': [
                            'sudo chown -R $USER:$USER ~/.vscode',
                            'sudo chown -R $USER:$USER ~/.config/Code'
                        ],
                        'description': 'Fix VSCode directory permissions'
                    }
                ]
            },
            'wayland_x11_issues': {
                'patterns': [
                    r'wayland.*error',
                    r'x11.*error',
                    r'display.*error',
                    r'xwayland.*crash'
                ],
                'severity': 'MEDIUM',
                'category': 'Display System',
                'solutions': [
                    {
                        'title': 'Force X11 Mode',
                        'commands': [
                            'export GDK_BACKEND=x11',
                            'code --enable-features=UseOzonePlatform --ozone-platform=x11'
                        ],
                        'description': 'Force VSCode to use X11 instead of Wayland'
                    },
                    {
                        'title': 'Wayland Compatibility',
                        'commands': [
                            'code --enable-features=WaylandWindowDecorations',
                            'code --ozone-platform-hint=auto'
                        ],
                        'description': 'Enable Wayland compatibility features'
                    }
                ]
            }
        }
    
    def analyze_crash_data(self) -> Dict:
        """Analyze all crash data files and identify issues"""
        logger.info("🔍 Analyzing crash data for intelligent diagnostics...")
        
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'issues_found': [],
            'system_status': {},
            'recommendations': [],
            'immediate_actions': [],
            'preventive_measures': []
        }
        
        # Analyze each log file
        log_files = list(self.crash_data_dir.glob("*.txt"))
        logger.info(f"📁 Found {len(log_files)} log files to analyze")
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                file_analysis = self._analyze_log_content(content, log_file.name)
                if file_analysis['issues']:
                    analysis_results['issues_found'].extend(file_analysis['issues'])
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not analyze {log_file}: {e}")
        
        # Generate intelligent recommendations
        analysis_results['recommendations'] = self._generate_recommendations(analysis_results['issues_found'])
        analysis_results['immediate_actions'] = self._generate_immediate_actions(analysis_results['issues_found'])
        analysis_results['preventive_measures'] = self._generate_preventive_measures(analysis_results['issues_found'])
        
        return analysis_results
    
    def _analyze_log_content(self, content: str, filename: str) -> Dict:
        """Analyze log content for known patterns"""
        issues = []
        
        for issue_type, config in self.solution_database.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    # Get context around the match
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()
                    
                    issue = {
                        'type': issue_type,
                        'severity': config['severity'],
                        'category': config['category'],
                        'pattern_matched': pattern,
                        'context': context,
                        'source_file': filename,
                        'line_number': content[:match.start()].count('\n') + 1,
                        'solutions': config['solutions']
                    }
                    issues.append(issue)
        
        return {'issues': issues}
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[Dict]:
        """Generate intelligent recommendations based on issues found"""
        recommendations = []
        
        # Group issues by category
        categories = {}
        for issue in issues:
            category = issue['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(issue)
        
        # Generate category-specific recommendations
        for category, category_issues in categories.items():
            severity_counts = {}
            for issue in category_issues:
                severity = issue['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            recommendation = {
                'category': category,
                'issue_count': len(category_issues),
                'severity_breakdown': severity_counts,
                'priority': 'HIGH' if 'HIGH' in severity_counts else 'MEDIUM',
                'recommended_actions': []
            }
            
            # Add specific actions for this category
            for issue in category_issues[:3]:  # Top 3 issues
                recommendation['recommended_actions'].extend(issue['solutions'])
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_immediate_actions(self, issues: List[Dict]) -> List[Dict]:
        """Generate immediate actions to take"""
        immediate_actions = []
        
        # High priority issues first
        high_priority_issues = [issue for issue in issues if issue['severity'] == 'HIGH']
        
        for issue in high_priority_issues[:5]:  # Top 5 critical issues
            for solution in issue['solutions'][:2]:  # Top 2 solutions per issue
                action = {
                    'title': f"Fix {issue['type'].replace('_', ' ').title()}",
                    'description': solution['description'],
                    'commands': solution['commands'],
                    'category': issue['category'],
                    'urgency': 'IMMEDIATE'
                }
                immediate_actions.append(action)
        
        return immediate_actions
    
    def _generate_preventive_measures(self, issues: List[Dict]) -> List[Dict]:
        """Generate preventive measures to avoid future issues"""
        preventive_measures = [
            {
                'title': 'Enhanced Memory Protection',
                'description': 'Install and configure advanced memory management tools',
                'commands': [
                    'sudo dnf install -y earlyoom nohang',
                    'sudo systemctl enable --now earlyoom',
                    'sudo systemctl enable --now nohang',
                    'echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf'
                ],
                'category': 'System Hardening'
            },
            {
                'title': 'VSCode Optimization',
                'description': 'Configure VSCode for stability and performance',
                'commands': [
                    'mkdir -p ~/.config/Code/User',
                    'echo \'{"window.titleBarStyle": "custom", "extensions.autoUpdate": false}\' > ~/.config/Code/User/settings.json'
                ],
                'category': 'Application Tuning'
            },
            {
                'title': 'System Monitoring',
                'description': 'Set up continuous system monitoring',
                'commands': [
                    'sudo systemctl enable --now systemd-oomd',
                    'echo "* soft memlock unlimited" | sudo tee -a /etc/security/limits.conf'
                ],
                'category': 'Monitoring'
            }
        ]
        
        return preventive_measures
    
    def execute_solution(self, solution: Dict, dry_run: bool = True) -> Dict:
        """Execute a solution with proper error handling"""
        logger.info(f"🔧 {'Simulating' if dry_run else 'Executing'} solution: {solution['title']}")
        
        results = {
            'solution': solution['title'],
            'success': True,
            'outputs': [],
            'errors': [],
            'dry_run': dry_run
        }
        
        for command in solution['commands']:
            try:
                if dry_run:
                    logger.info(f"📋 Would execute: {command}")
                    results['outputs'].append(f"DRY RUN: {command}")
                else:
                    logger.info(f"⚡ Executing: {command}")
                    result = subprocess.run(
                        command, 
                        shell=True, 
                        capture_output=True, 
                        text=True, 
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        results['outputs'].append(f"✅ {command}: {result.stdout.strip()}")
                    else:
                        results['errors'].append(f"❌ {command}: {result.stderr.strip()}")
                        results['success'] = False
                        
            except subprocess.TimeoutExpired:
                results['errors'].append(f"⏰ {command}: Command timed out")
                results['success'] = False
            except Exception as e:
                results['errors'].append(f"💥 {command}: {str(e)}")
                results['success'] = False
        
        return results
    
    def generate_diagnostic_report(self) -> str:
        """Generate a comprehensive diagnostic report"""
        analysis = self.analyze_crash_data()
        
        report = f"""
🧠 INTELLIGENT DIAGNOSTIC REPORT
Generated: {analysis['timestamp']}
{'='*60}

📊 SUMMARY:
- Issues Found: {len(analysis['issues_found'])}
- Categories Affected: {len(set(issue['category'] for issue in analysis['issues_found']))}
- High Priority Issues: {len([i for i in analysis['issues_found'] if i['severity'] == 'HIGH'])}

🔍 DETAILED ANALYSIS:
"""
        
        # Group issues by category for better presentation
        categories = {}
        for issue in analysis['issues_found']:
            category = issue['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(issue)
        
        for category, issues in categories.items():
            report += f"\n📂 {category.upper()}:\n"
            for i, issue in enumerate(issues[:3], 1):  # Top 3 per category
                report += f"  {i}. {issue['type'].replace('_', ' ').title()}\n"
                report += f"     Severity: {issue['severity']}\n"
                report += f"     Source: {issue['source_file']}\n"
                report += f"     Context: {issue['context'][:100]}...\n"
        
        report += f"\n🚀 IMMEDIATE ACTIONS:\n"
        for i, action in enumerate(analysis['immediate_actions'][:5], 1):
            report += f"  {i}. {action['title']}\n"
            report += f"     {action['description']}\n"
            for cmd in action['commands']:
                report += f"     $ {cmd}\n"
        
        report += f"\n🛡️ PREVENTIVE MEASURES:\n"
        for i, measure in enumerate(analysis['preventive_measures'], 1):
            report += f"  {i}. {measure['title']}\n"
            report += f"     {measure['description']}\n"
        
        return report

def main():
    """Main diagnostic function"""
    engine = IntelligentDiagnosticEngine()
    
    print("🧠 INTELLIGENT DIAGNOSTIC ENGINE")
    print("="*50)
    
    # Generate and display report
    report = engine.generate_diagnostic_report()
    print(report)
    
    # Save detailed analysis
    analysis = engine.analyze_crash_data()
    with open('intelligent_diagnostic_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Detailed analysis saved to: intelligent_diagnostic_analysis.json")
    print(f"📁 Analyzed crash data from: {engine.crash_data_dir}")

if __name__ == '__main__':
    main()
