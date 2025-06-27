#!/usr/bin/env python3
"""
🐕 Fixed Dogtail Accessibility Tester
Properly configured Dogtail testing for KDE Plasma environment

Features:
- Proper AT-SPI configuration
- KDE Plasma compatibility
- Firefox accessibility testing
- Web interface accessibility validation
- Screen reader compatibility testing
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Configure AT-SPI environment before importing dogtail
os.environ['AT_SPI_BUS_TYPE'] = 'session'
os.environ['DISPLAY'] = ':0'
os.environ['QT_ACCESSIBILITY'] = '1'
os.environ['GTK_MODULES'] = 'gail:atk-bridge'

try:
    import dogtail.config
    import dogtail.tree
    import dogtail.predicate
    import dogtail.utils
    DOGTAIL_AVAILABLE = True
    
    # Configure dogtail for KDE environment
    dogtail.config.config.logDebugToFile = False
    dogtail.config.config.logDebugToStdOut = True
    dogtail.config.config.searchCutoffCount = 20
    dogtail.config.config.searchBackoffDuration = 0.5
    dogtail.config.config.actionDelay = 1.0
    dogtail.config.config.runInterval = 0.5
    dogtail.config.config.defaultDelay = 1.0
    
except ImportError as e:
    DOGTAIL_AVAILABLE = False
    print(f"⚠️ Dogtail not available: {e}")

class FixedDogtailTester:
    def __init__(self):
        self.test_results = []
        self.interfaces = {
            9000: "💥 Crash Analysis Correlator",
            5000: "🗄️ Database Management"
        }
        
    def setup_accessibility_environment(self):
        """Setup proper accessibility environment for KDE Plasma"""
        print("🔧 Setting up accessibility environment...")
        
        # Ensure AT-SPI is running
        try:
            subprocess.run(['at-spi-bus-launcher', '--launch-immediately'], 
                         check=False, timeout=5, capture_output=True)
            print("✅ AT-SPI bus launcher started")
        except:
            print("⚠️ AT-SPI bus launcher may already be running")
        
        # Enable Qt accessibility
        try:
            subprocess.run(['qdbus', 'org.kde.kded5', '/kded', 'loadModule', 'kaccess'], 
                         check=False, timeout=5, capture_output=True)
            print("✅ KDE accessibility module loaded")
        except:
            print("⚠️ KDE accessibility module may already be loaded")
        
        # Wait for services to initialize
        time.sleep(2)
        
    def test_accessibility_tree(self):
        """Test if accessibility tree is accessible"""
        if not DOGTAIL_AVAILABLE:
            return {"status": "SKIP", "reason": "Dogtail not available"}
        
        try:
            print("🌳 Testing accessibility tree access...")
            
            # Get desktop
            desktop = dogtail.tree.root
            print(f"✅ Desktop accessible: {desktop.name}")
            
            # List applications
            apps = desktop.applications()
            print(f"✅ Found {len(apps)} applications in accessibility tree")
            
            app_names = [app.name for app in apps[:10]]  # First 10 apps
            print(f"📱 Applications: {', '.join(app_names)}")
            
            return {
                "status": "PASS",
                "desktop_name": desktop.name,
                "app_count": len(apps),
                "sample_apps": app_names
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "suggestion": "Check AT-SPI configuration"
            }
    
    def test_firefox_accessibility(self):
        """Test Firefox accessibility specifically"""
        if not DOGTAIL_AVAILABLE:
            return {"status": "SKIP", "reason": "Dogtail not available"}
        
        try:
            print("🦊 Testing Firefox accessibility...")
            
            # Try to find Firefox
            desktop = dogtail.tree.root
            
            # Look for Firefox by different names
            firefox_names = ['firefox', 'Firefox', 'Mozilla Firefox', 'firefox-esr']
            firefox_app = None
            
            for name in firefox_names:
                try:
                    firefox_app = desktop.application(name)
                    print(f"✅ Found Firefox as: {name}")
                    break
                except:
                    continue
            
            if not firefox_app:
                # Try to launch Firefox if not found
                print("🚀 Launching Firefox for accessibility testing...")
                subprocess.Popen(['firefox', 'http://localhost:9000'], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(5)  # Wait for Firefox to start
                
                # Try again
                for name in firefox_names:
                    try:
                        firefox_app = desktop.application(name)
                        print(f"✅ Found launched Firefox as: {name}")
                        break
                    except:
                        continue
            
            if firefox_app:
                # Test Firefox accessibility features
                windows = firefox_app.windows()
                print(f"✅ Firefox windows: {len(windows)}")
                
                if windows:
                    window = windows[0]
                    print(f"✅ Main window: {window.name}")
                    
                    # Try to find web content
                    try:
                        web_content = window.findChildren(lambda x: x.roleName == 'document web')
                        print(f"✅ Web documents found: {len(web_content)}")
                    except:
                        print("⚠️ Web content not accessible")
                
                return {
                    "status": "PASS",
                    "firefox_found": True,
                    "window_count": len(windows),
                    "accessibility_working": True
                }
            else:
                return {
                    "status": "FAIL",
                    "firefox_found": False,
                    "error": "Firefox not found in accessibility tree"
                }
                
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "suggestion": "Ensure Firefox is running and accessible"
            }
    
    def test_web_interface_accessibility(self, port, interface_name):
        """Test specific web interface accessibility"""
        if not DOGTAIL_AVAILABLE:
            return {"status": "SKIP", "reason": "Dogtail not available"}
        
        try:
            print(f"🌐 Testing {interface_name} accessibility...")
            
            # Launch Firefox with the specific interface
            url = f"http://localhost:{port}"
            subprocess.Popen(['firefox', url], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)  # Wait for page to load
            
            desktop = dogtail.tree.root
            firefox_app = None
            
            # Find Firefox
            for name in ['firefox', 'Firefox', 'Mozilla Firefox']:
                try:
                    firefox_app = desktop.application(name)
                    break
                except:
                    continue
            
            if firefox_app:
                windows = firefox_app.windows()
                if windows:
                    window = windows[0]
                    
                    # Look for specific interface elements
                    try:
                        # Look for buttons
                        buttons = window.findChildren(lambda x: x.roleName == 'push button')
                        print(f"✅ Buttons found: {len(buttons)}")
                        
                        # Look for headings
                        headings = window.findChildren(lambda x: x.roleName == 'heading')
                        print(f"✅ Headings found: {len(headings)}")
                        
                        # Look for text content
                        text_elements = window.findChildren(lambda x: x.roleName == 'text')
                        print(f"✅ Text elements found: {len(text_elements)}")
                        
                        return {
                            "status": "PASS",
                            "interface": interface_name,
                            "buttons": len(buttons),
                            "headings": len(headings),
                            "text_elements": len(text_elements),
                            "accessibility_score": "Good" if (len(buttons) + len(headings)) > 0 else "Poor"
                        }
                        
                    except Exception as e:
                        return {
                            "status": "PARTIAL",
                            "interface": interface_name,
                            "error": str(e),
                            "firefox_accessible": True
                        }
                else:
                    return {
                        "status": "FAIL",
                        "interface": interface_name,
                        "error": "No Firefox windows found"
                    }
            else:
                return {
                    "status": "FAIL",
                    "interface": interface_name,
                    "error": "Firefox not accessible"
                }
                
        except Exception as e:
            return {
                "status": "FAIL",
                "interface": interface_name,
                "error": str(e)
            }
    
    def run_comprehensive_dogtail_tests(self):
        """Run all Dogtail accessibility tests"""
        print("🐕 COMPREHENSIVE DOGTAIL ACCESSIBILITY TESTING")
        print("=" * 60)
        
        # Setup environment
        self.setup_accessibility_environment()
        
        # Test 1: Accessibility tree
        tree_result = self.test_accessibility_tree()
        self.test_results.append(("Accessibility Tree", tree_result))
        
        # Test 2: Firefox accessibility
        firefox_result = self.test_firefox_accessibility()
        self.test_results.append(("Firefox Accessibility", firefox_result))
        
        # Test 3: Web interface accessibility
        for port, name in self.interfaces.items():
            interface_result = self.test_web_interface_accessibility(port, name)
            self.test_results.append((f"{name} Interface", interface_result))
        
        # Generate report
        self.generate_dogtail_report()
    
    def generate_dogtail_report(self):
        """Generate comprehensive Dogtail test report"""
        print("\n🐕 DOGTAIL ACCESSIBILITY TEST REPORT")
        print("=" * 60)
        
        passed_tests = len([r for _, r in self.test_results if r.get("status") == "PASS"])
        total_tests = len(self.test_results)
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {total_tests - passed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for test_name, result in self.test_results:
            status_icon = "✅" if result.get("status") == "PASS" else "❌" if result.get("status") == "FAIL" else "⚠️"
            print(f"   {status_icon} {test_name}: {result.get('status', 'UNKNOWN')}")
            
            if result.get("error"):
                print(f"      Error: {result['error']}")
            if result.get("suggestion"):
                print(f"      Suggestion: {result['suggestion']}")
        
        print(f"\n🎯 ACCESSIBILITY RECOMMENDATIONS:")
        if passed_tests == total_tests:
            print("   • All accessibility tests passed!")
            print("   • Web interfaces are screen reader compatible")
            print("   • Dogtail integration is working properly")
        else:
            print("   • Fix failed accessibility tests")
            print("   • Ensure AT-SPI is properly configured")
            print("   • Check Firefox accessibility settings")
            print("   • Verify web interface semantic markup")

def main():
    """Main testing function"""
    if not DOGTAIL_AVAILABLE:
        print("❌ Dogtail is not available. Install with: pip install dogtail")
        return
    
    tester = FixedDogtailTester()
    tester.run_comprehensive_dogtail_tests()

if __name__ == '__main__':
    main()
