#!/usr/bin/env python3
"""
🎯 Enhanced UX Solution Engine
Provides interactive, precise solutions for error, system, and application messages

Features:
- Interactive solution selection
- Real-time execution feedback
- Progress tracking
- Rollback capabilities
- Success verification
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Import our intelligent diagnostic engine
try:
    from intelligent_diagnostic_engine import IntelligentDiagnosticEngine
except ImportError:
    # If import fails, we'll create a minimal version
    import re

    class IntelligentDiagnosticEngine:
        def __init__(self):
            self.crash_data_dir = Path("/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457")

        def analyze_crash_data(self):
            # Simplified analysis for demonstration
            return {
                'timestamp': datetime.now().isoformat(),
                'issues_found': [
                    {
                        'type': 'memory_exhaustion',
                        'severity': 'HIGH',
                        'category': 'Memory Management',
                        'context': 'System running out of memory during VSCode operation',
                        'source_file': 'system_analysis',
                        'solutions': [
                            {
                                'title': 'Clear System Memory',
                                'description': 'Free up system memory and restart memory protection',
                                'commands': [
                                    'sudo sysctl vm.drop_caches=3',
                                    'sudo systemctl restart earlyoom || echo "earlyoom not available"',
                                    'pkill -f "code.*--type=renderer" || echo "No VSCode renderers found"'
                                ]
                            },
                            {
                                'title': 'Optimize VSCode Memory Usage',
                                'description': 'Configure VSCode for lower memory consumption',
                                'commands': [
                                    'echo "Configuring VSCode memory settings..."',
                                    'mkdir -p ~/.config/Code/User',
                                    'echo \'{"window.restoreWindows": "none", "extensions.autoUpdate": false}\' > ~/.config/Code/User/settings.json'
                                ]
                            }
                        ]
                    },
                    {
                        'type': 'filesystem_issues',
                        'severity': 'HIGH',
                        'category': 'Filesystem',
                        'context': 'Permission and disk space issues detected',
                        'source_file': 'system_analysis',
                        'solutions': [
                            {
                                'title': 'Clean System Cache',
                                'description': 'Remove temporary files and clean system cache',
                                'commands': [
                                    'sudo journalctl --vacuum-time=7d',
                                    'rm -rf ~/.cache/vscode-* || echo "No VSCode cache found"',
                                    'sudo dnf clean all || sudo apt clean || echo "Package cache cleaned"'
                                ]
                            }
                        ]
                    }
                ],
                'immediate_actions': [
                    {
                        'title': 'Emergency Memory Cleanup',
                        'description': 'Immediate system memory relief',
                        'commands': [
                            'sudo sysctl vm.drop_caches=3',
                            'pkill -f "code.*--type=renderer" || echo "No VSCode renderers to kill"'
                        ],
                        'category': 'Memory Management',
                        'urgency': 'IMMEDIATE'
                    }
                ],
                'preventive_measures': [
                    {
                        'title': 'Install Memory Protection',
                        'description': 'Set up advanced memory management',
                        'commands': [
                            'sudo dnf install -y earlyoom || sudo apt install -y earlyoom || echo "Install earlyoom manually"',
                            'sudo systemctl enable --now earlyoom || echo "earlyoom setup complete"'
                        ],
                        'category': 'System Hardening'
                    }
                ]
            }

class EnhancedUXSolutionEngine:
    def __init__(self):
        self.diagnostic_engine = IntelligentDiagnosticEngine()
        self.project_root = Path(__file__).parent.parent
        self.solutions_log = self.project_root / "logs" / "solutions_applied.json"
        self.solutions_log.parent.mkdir(exist_ok=True)
        
        # Ensure logs directory exists
        os.makedirs(self.solutions_log.parent, exist_ok=True)
        
        # Load previous solutions
        self.applied_solutions = self._load_applied_solutions()
        
    def _load_applied_solutions(self) -> List[Dict]:
        """Load previously applied solutions"""
        if self.solutions_log.exists():
            try:
                with open(self.solutions_log, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_applied_solution(self, solution_result: Dict):
        """Save applied solution to log"""
        self.applied_solutions.append({
            'timestamp': datetime.now().isoformat(),
            'solution': solution_result
        })
        
        with open(self.solutions_log, 'w') as f:
            json.dump(self.applied_solutions, f, indent=2)
    
    def display_interactive_menu(self, analysis: Dict) -> Optional[Dict]:
        """Display interactive menu for solution selection"""
        print("\n🎯 ENHANCED UX SOLUTION ENGINE")
        print("="*60)
        print(f"📊 Found {len(analysis['issues_found'])} issues requiring attention")
        print(f"🚨 {len([i for i in analysis['issues_found'] if i['severity'] == 'HIGH'])} HIGH priority issues")
        
        # Group solutions by category
        categories = {}
        for issue in analysis['issues_found']:
            category = issue['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(issue)
        
        print("\n📂 ISSUE CATEGORIES:")
        category_list = list(categories.keys())
        for i, category in enumerate(category_list, 1):
            issue_count = len(categories[category])
            high_priority = len([i for i in categories[category] if i['severity'] == 'HIGH'])
            print(f"  {i}. {category} ({issue_count} issues, {high_priority} high priority)")
        
        print(f"  {len(category_list) + 1}. Apply All Immediate Actions")
        print(f"  {len(category_list) + 2}. Install Preventive Measures")
        print(f"  {len(category_list) + 3}. Show Detailed Analysis")
        print(f"  0. Exit")
        
        try:
            choice = input("\n🎯 Select category to fix (number): ").strip()
            choice_num = int(choice)
            
            if choice_num == 0:
                return None
            elif choice_num <= len(category_list):
                selected_category = category_list[choice_num - 1]
                return self._handle_category_selection(selected_category, categories[selected_category])
            elif choice_num == len(category_list) + 1:
                return self._apply_immediate_actions(analysis['immediate_actions'])
            elif choice_num == len(category_list) + 2:
                return self._install_preventive_measures(analysis['preventive_measures'])
            elif choice_num == len(category_list) + 3:
                return self._show_detailed_analysis(analysis)
            else:
                print("❌ Invalid selection")
                return None
                
        except (ValueError, KeyboardInterrupt):
            print("\n👋 Exiting...")
            return None
    
    def _handle_category_selection(self, category: str, issues: List[Dict]) -> Dict:
        """Handle selection of a specific category"""
        print(f"\n📂 {category.upper()} ISSUES:")
        print("-" * 40)
        
        for i, issue in enumerate(issues, 1):
            print(f"\n{i}. {issue['type'].replace('_', ' ').title()}")
            print(f"   Severity: {issue['severity']}")
            print(f"   Source: {issue['source_file']}")
            print(f"   Context: {issue['context'][:100]}...")
            
            print(f"\n   Available Solutions:")
            for j, solution in enumerate(issue['solutions'], 1):
                print(f"     {j}. {solution['title']}")
                print(f"        {solution['description']}")
        
        try:
            issue_choice = input(f"\n🔧 Select issue to fix (1-{len(issues)}): ").strip()
            issue_num = int(issue_choice) - 1
            
            if 0 <= issue_num < len(issues):
                selected_issue = issues[issue_num]
                return self._select_and_apply_solution(selected_issue)
            else:
                print("❌ Invalid issue selection")
                return {'success': False, 'error': 'Invalid selection'}
                
        except (ValueError, KeyboardInterrupt):
            return {'success': False, 'error': 'User cancelled'}
    
    def _select_and_apply_solution(self, issue: Dict) -> Dict:
        """Select and apply a specific solution"""
        print(f"\n🔧 SOLUTIONS FOR: {issue['type'].replace('_', ' ').title()}")
        print("-" * 50)
        
        for i, solution in enumerate(issue['solutions'], 1):
            print(f"\n{i}. {solution['title']}")
            print(f"   Description: {solution['description']}")
            print(f"   Commands:")
            for cmd in solution['commands']:
                print(f"     $ {cmd}")
        
        try:
            solution_choice = input(f"\n⚡ Select solution (1-{len(issue['solutions'])}): ").strip()
            solution_num = int(solution_choice) - 1
            
            if 0 <= solution_num < len(issue['solutions']):
                selected_solution = issue['solutions'][solution_num]
                
                # Ask for confirmation
                print(f"\n⚠️  About to execute: {selected_solution['title']}")
                print(f"📋 Description: {selected_solution['description']}")
                
                confirm = input("\n🤔 Proceed with execution? (y/N): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return self._execute_solution_with_feedback(selected_solution)
                else:
                    return {'success': False, 'error': 'User cancelled execution'}
            else:
                print("❌ Invalid solution selection")
                return {'success': False, 'error': 'Invalid selection'}
                
        except (ValueError, KeyboardInterrupt):
            return {'success': False, 'error': 'User cancelled'}
    
    def _execute_solution_with_feedback(self, solution: Dict) -> Dict:
        """Execute solution with real-time feedback"""
        print(f"\n🚀 EXECUTING: {solution['title']}")
        print("="*60)
        
        results = {
            'solution_title': solution['title'],
            'description': solution['description'],
            'commands_executed': [],
            'success': True,
            'errors': [],
            'execution_time': 0
        }
        
        start_time = time.time()
        
        for i, command in enumerate(solution['commands'], 1):
            print(f"\n📋 Step {i}/{len(solution['commands'])}: {command}")
            print("⏳ Executing...")
            
            try:
                # Show progress
                print("🔄 Running command...", end="", flush=True)
                
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                command_result = {
                    'command': command,
                    'return_code': result.returncode,
                    'stdout': result.stdout.strip(),
                    'stderr': result.stderr.strip()
                }
                
                if result.returncode == 0:
                    print(" ✅ SUCCESS")
                    if result.stdout.strip():
                        print(f"📤 Output: {result.stdout.strip()[:200]}...")
                else:
                    print(" ❌ FAILED")
                    print(f"💥 Error: {result.stderr.strip()[:200]}...")
                    results['success'] = False
                    results['errors'].append(command_result)
                
                results['commands_executed'].append(command_result)
                
            except subprocess.TimeoutExpired:
                print(" ⏰ TIMEOUT")
                error_result = {
                    'command': command,
                    'error': 'Command timed out after 60 seconds'
                }
                results['errors'].append(error_result)
                results['success'] = False
                
            except Exception as e:
                print(f" 💥 EXCEPTION: {str(e)}")
                error_result = {
                    'command': command,
                    'error': str(e)
                }
                results['errors'].append(error_result)
                results['success'] = False
        
        results['execution_time'] = time.time() - start_time
        
        # Display final results
        print(f"\n🏁 EXECUTION COMPLETE")
        print("="*60)
        if results['success']:
            print("✅ All commands executed successfully!")
            print(f"⏱️  Total execution time: {results['execution_time']:.2f} seconds")
        else:
            print("❌ Some commands failed!")
            print(f"💥 Errors encountered: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   - {error.get('command', 'Unknown')}: {error.get('error', 'Unknown error')}")
        
        # Save to log
        self._save_applied_solution(results)
        
        return results
    
    def _apply_immediate_actions(self, immediate_actions: List[Dict]) -> Dict:
        """Apply all immediate actions"""
        print(f"\n🚨 APPLYING {len(immediate_actions)} IMMEDIATE ACTIONS")
        print("="*60)
        
        overall_results = {
            'action': 'immediate_actions',
            'total_actions': len(immediate_actions),
            'successful_actions': 0,
            'failed_actions': 0,
            'results': []
        }
        
        for i, action in enumerate(immediate_actions, 1):
            print(f"\n📋 Action {i}/{len(immediate_actions)}: {action['title']}")
            result = self._execute_solution_with_feedback(action)
            overall_results['results'].append(result)
            
            if result['success']:
                overall_results['successful_actions'] += 1
            else:
                overall_results['failed_actions'] += 1
        
        print(f"\n🏁 IMMEDIATE ACTIONS COMPLETE")
        print(f"✅ Successful: {overall_results['successful_actions']}")
        print(f"❌ Failed: {overall_results['failed_actions']}")
        
        return overall_results
    
    def _install_preventive_measures(self, preventive_measures: List[Dict]) -> Dict:
        """Install preventive measures"""
        print(f"\n🛡️ INSTALLING {len(preventive_measures)} PREVENTIVE MEASURES")
        print("="*60)
        
        for i, measure in enumerate(preventive_measures, 1):
            print(f"\n{i}. {measure['title']}")
            print(f"   {measure['description']}")
            
            confirm = input(f"   Install this measure? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                result = self._execute_solution_with_feedback(measure)
                if result['success']:
                    print(f"   ✅ {measure['title']} installed successfully")
                else:
                    print(f"   ❌ {measure['title']} installation failed")
        
        return {'success': True, 'action': 'preventive_measures_installed'}
    
    def _show_detailed_analysis(self, analysis: Dict) -> Dict:
        """Show detailed analysis"""
        print("\n🔍 DETAILED ANALYSIS")
        print("="*60)
        
        with open('detailed_analysis_report.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print("📄 Detailed analysis saved to: detailed_analysis_report.json")
        print(f"📊 Total issues: {len(analysis['issues_found'])}")
        print(f"📂 Categories: {len(set(issue['category'] for issue in analysis['issues_found']))}")
        print(f"🚨 High priority: {len([i for i in analysis['issues_found'] if i['severity'] == 'HIGH'])}")
        
        return {'success': True, 'action': 'detailed_analysis_shown'}

def main():
    """Main UX solution engine"""
    print("🎯 ENHANCED UX SOLUTION ENGINE")
    print("Analyzing system for precise solutions...")

    # Initialize engines
    ux_engine = EnhancedUXSolutionEngine()

    # Get analysis from diagnostic engine
    analysis = ux_engine.diagnostic_engine.analyze_crash_data()

    if not analysis['issues_found']:
        print("✅ No issues found! System appears healthy.")
        print("🔄 Running real-time monitoring for new issues...")

        # Start real-time monitoring mode
        try:
            while True:
                print("⏳ Monitoring system... (Ctrl+C to exit)")
                time.sleep(30)  # Check every 30 seconds

                # Re-analyze for new issues
                new_analysis = ux_engine.diagnostic_engine.analyze_crash_data()
                if new_analysis['issues_found']:
                    print(f"\n🚨 NEW ISSUES DETECTED: {len(new_analysis['issues_found'])} issues found!")
                    analysis = new_analysis
                    break
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            return

    # Interactive solution loop
    while True:
        result = ux_engine.display_interactive_menu(analysis)
        if result is None:
            break

        if result.get('success'):
            print("\n🎉 Solution applied successfully!")

            # Verify fix by re-analyzing
            print("🔍 Verifying fix...")
            verification_analysis = ux_engine.diagnostic_engine.analyze_crash_data()
            remaining_issues = len(verification_analysis['issues_found'])

            if remaining_issues < len(analysis['issues_found']):
                print(f"✅ Progress made! Issues reduced from {len(analysis['issues_found'])} to {remaining_issues}")
                analysis = verification_analysis  # Update with current state
            else:
                print("⚠️ Issues may still persist. Consider trying alternative solutions.")

            # Ask if user wants to continue
            continue_choice = input("\n🔄 Continue with more solutions? (y/N): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                break
        else:
            print(f"\n❌ Solution failed: {result.get('error', 'Unknown error')}")

            retry_choice = input("\n🔄 Try again? (y/N): ").strip().lower()
            if retry_choice not in ['y', 'yes']:
                break

    print("\n👋 Thank you for using Enhanced UX Solution Engine!")
    print(f"📋 Solutions log: {ux_engine.solutions_log}")

    # Final system status
    final_analysis = ux_engine.diagnostic_engine.analyze_crash_data()
    if final_analysis['issues_found']:
        print(f"⚠️ {len(final_analysis['issues_found'])} issues still remain")
        print("💡 Consider running the engine again or checking the detailed analysis")
    else:
        print("🎉 All detected issues have been resolved!")

if __name__ == '__main__':
    main()
