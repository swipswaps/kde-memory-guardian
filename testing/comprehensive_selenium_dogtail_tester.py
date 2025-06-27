#!/usr/bin/env python3
"""
🎭🐕 Comprehensive Selenium + Dogtail Testing Suite
Complete testing of crash analyzer with sudo data integration

Features:
- Selenium WebDriver testing for cross-browser compatibility
- Dogtail accessibility testing for screen reader support
- Terminal-sudo workflow testing
- Data integration verification
- Text selection validation
- Complete user workflow simulation
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path

# Configure environment
os.environ['AT_SPI_BUS_TYPE'] = 'session'
os.environ['DISPLAY'] = ':0'
os.environ['QT_ACCESSIBILITY'] = '1'

# Import testing frameworks
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available")

try:
    import dogtail.config
    import dogtail.tree
    import dogtail.predicate
    import dogtail.utils
    DOGTAIL_AVAILABLE = True
    
    # Configure dogtail
    dogtail.config.config.logDebugToFile = False
    dogtail.config.config.searchCutoffCount = 20
    dogtail.config.config.actionDelay = 1.0
    
except ImportError:
    DOGTAIL_AVAILABLE = False
    print("⚠️ Dogtail not available")

class ComprehensiveSeleniumDogtailTester:
    def __init__(self):
        self.test_results = []
        self.driver = None
        self.interfaces = {
            9000: "💥 Crash Analysis Correlator"
        }
        
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            return False
        
        try:
            options = FirefoxOptions()
            # Don't use headless for terminal interaction testing
            # options.add_argument('--headless')
            
            self.driver = webdriver.Firefox(options=options)
            self.driver.implicitly_wait(10)
            print("✅ Selenium WebDriver initialized")
            return True
            
        except Exception as e:
            print(f"❌ Selenium setup failed: {e}")
            return False
    
    def test_selenium_interface_loading(self):
        """Test interface loading with Selenium"""
        if not self.driver:
            return {"status": "SKIP", "reason": "Selenium not available"}
        
        try:
            print("🌐 Testing interface loading with Selenium...")
            
            self.driver.get("http://localhost:9000")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check title
            title = self.driver.title
            print(f"📄 Page title: {title}")
            
            # Check for key elements
            analyze_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Analyze VSCode Crash')]")
            sudo_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Collect System Logs')]")
            crash_input = self.driver.find_element(By.ID, "crashFile")
            
            print("✅ All key interface elements found")
            
            return {
                "status": "PASS",
                "title": title,
                "elements_found": {
                    "analyze_button": bool(analyze_btn),
                    "sudo_button": bool(sudo_btn),
                    "crash_input": bool(crash_input)
                }
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def test_selenium_text_selection(self):
        """Test text selection functionality with Selenium"""
        if not self.driver:
            return {"status": "SKIP", "reason": "Selenium not available"}
        
        try:
            print("📝 Testing text selection with Selenium...")
            
            # Test button text selection
            sudo_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Collect System Logs')]")
            
            # Triple click to select text
            actions = ActionChains(self.driver)
            actions.click(sudo_btn).click(sudo_btn).click(sudo_btn).perform()
            
            # Check if text is selected
            selected_text = self.driver.execute_script("return window.getSelection().toString();")
            
            text_selectable = "Collect System Logs" in selected_text
            print(f"📋 Text selection working: {text_selectable}")
            
            return {
                "status": "PASS" if text_selectable else "FAIL",
                "selected_text": selected_text,
                "text_selectable": text_selectable
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def test_selenium_sudo_workflow(self):
        """Test complete sudo workflow with Selenium"""
        if not self.driver:
            return {"status": "SKIP", "reason": "Selenium not available"}
        
        try:
            print("🔐 Testing sudo workflow with Selenium...")
            
            # Click sudo collection button
            sudo_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Collect System Logs')]")
            sudo_btn.click()
            
            # Wait for response
            time.sleep(3)
            
            # Check for terminal opening message
            try:
                terminal_msg = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Opening Terminal')]"))
                )
                terminal_opened = True
                print("✅ Terminal opening message displayed")
            except:
                terminal_opened = False
                print("⚠️ Terminal opening message not found")
            
            # Check for check results button
            try:
                check_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Check Results')]")
                check_button_found = True
                print("✅ Check Results button found")
            except:
                check_button_found = False
                print("⚠️ Check Results button not found")
            
            return {
                "status": "PASS" if (terminal_opened or check_button_found) else "FAIL",
                "terminal_message": terminal_opened,
                "check_button": check_button_found
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def test_selenium_crash_analysis(self):
        """Test crash analysis with Selenium"""
        if not self.driver:
            return {"status": "SKIP", "reason": "Selenium not available"}
        
        try:
            print("📊 Testing crash analysis with Selenium...")
            
            # Click analyze button
            analyze_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Analyze Crash File')]")
            analyze_btn.click()
            
            # Wait for analysis to complete
            time.sleep(5)
            
            # Check for analysis results
            try:
                crash_type = self.driver.find_element(By.XPATH, "//*[contains(text(), 'memory_exhaustion')]")
                analysis_complete = True
                print("✅ Crash analysis completed")
            except:
                analysis_complete = False
                print("⚠️ Crash analysis results not found")
            
            # Check for evidence sections
            evidence_sections = []
            section_texts = ["EVIDENCE", "SYSTEM LOGS", "ERROR LOGS", "KERNEL MESSAGES", "MEMORY PRESSURE"]
            
            for section in section_texts:
                try:
                    element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{section}')]")
                    evidence_sections.append(section)
                except:
                    pass
            
            print(f"📋 Evidence sections found: {len(evidence_sections)}")
            
            return {
                "status": "PASS" if analysis_complete else "PARTIAL",
                "analysis_complete": analysis_complete,
                "evidence_sections": evidence_sections,
                "sections_count": len(evidence_sections)
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def test_dogtail_accessibility(self):
        """Test accessibility with Dogtail"""
        if not DOGTAIL_AVAILABLE:
            return {"status": "SKIP", "reason": "Dogtail not available"}
        
        try:
            print("🐕 Testing accessibility with Dogtail...")
            
            # Setup accessibility
            subprocess.run(['at-spi-bus-launcher', '--launch-immediately'], 
                         check=False, timeout=5, capture_output=True)
            time.sleep(2)
            
            # Get desktop
            desktop = dogtail.tree.root
            print(f"✅ Desktop accessible: {desktop.name}")
            
            # Find Firefox
            firefox_app = None
            for name in ['firefox', 'Firefox', 'Mozilla Firefox']:
                try:
                    firefox_app = desktop.application(name)
                    print(f"✅ Found Firefox: {name}")
                    break
                except:
                    continue
            
            if firefox_app:
                windows = firefox_app.windows()
                print(f"✅ Firefox windows: {len(windows)}")
                
                if windows:
                    window = windows[0]
                    
                    # Test accessibility features
                    try:
                        buttons = window.findChildren(lambda x: x.roleName == 'push button')
                        headings = window.findChildren(lambda x: x.roleName == 'heading')
                        
                        return {
                            "status": "PASS",
                            "firefox_accessible": True,
                            "buttons_found": len(buttons),
                            "headings_found": len(headings),
                            "accessibility_working": True
                        }
                        
                    except Exception as e:
                        return {
                            "status": "PARTIAL",
                            "firefox_accessible": True,
                            "error": str(e)
                        }
                else:
                    return {
                        "status": "FAIL",
                        "firefox_accessible": True,
                        "error": "No Firefox windows found"
                    }
            else:
                return {
                    "status": "FAIL",
                    "firefox_accessible": False,
                    "error": "Firefox not found in accessibility tree"
                }
                
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def test_data_integration(self):
        """Test if sudo data is properly integrated"""
        try:
            print("🔗 Testing sudo data integration...")
            
            # Check for sudo output files
            import glob
            sudo_files = glob.glob('/tmp/crash_analysis_*.txt')
            
            # Make API call to check integration
            import requests
            response = requests.post('http://localhost:9000/api/analyze-crash', 
                                   json={'crash_file': '/home/owner/Documents/2025_06_26_vcscode_crash.txt'},
                                   timeout=10)
            
            if response.status_code == 200:
                analysis = response.json()
                
                # Check for sudo data markers
                sudo_markers = 0
                for key, value in analysis.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and '[SUDO]' in item:
                                sudo_markers += 1
                
                return {
                    "status": "PASS" if sudo_markers > 0 else "PARTIAL",
                    "sudo_files_found": len(sudo_files),
                    "sudo_markers_in_analysis": sudo_markers,
                    "integration_working": sudo_markers > 0
                }
            else:
                return {
                    "status": "FAIL",
                    "error": f"API call failed: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e)
            }
    
    def run_comprehensive_tests(self):
        """Run all tests"""
        print("🎭🐕 COMPREHENSIVE SELENIUM + DOGTAIL TESTING")
        print("=" * 60)
        
        # Setup Selenium
        selenium_ready = self.setup_selenium()
        
        # Test 1: Interface loading
        if selenium_ready:
            result = self.test_selenium_interface_loading()
            self.test_results.append(("Selenium Interface Loading", result))
        
        # Test 2: Text selection
        if selenium_ready:
            result = self.test_selenium_text_selection()
            self.test_results.append(("Selenium Text Selection", result))
        
        # Test 3: Sudo workflow
        if selenium_ready:
            result = self.test_selenium_sudo_workflow()
            self.test_results.append(("Selenium Sudo Workflow", result))
        
        # Test 4: Crash analysis
        if selenium_ready:
            result = self.test_selenium_crash_analysis()
            self.test_results.append(("Selenium Crash Analysis", result))
        
        # Test 5: Dogtail accessibility
        result = self.test_dogtail_accessibility()
        self.test_results.append(("Dogtail Accessibility", result))
        
        # Test 6: Data integration
        result = self.test_data_integration()
        self.test_results.append(("Sudo Data Integration", result))
        
        # Generate report
        self.generate_comprehensive_report()
        
        # Cleanup
        if self.driver:
            self.driver.quit()
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        print("\n🎭🐕 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        passed = len([r for _, r in self.test_results if r.get("status") == "PASS"])
        total = len(self.test_results)
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {total - passed}")
        print(f"   📈 Success Rate: {(passed/total*100):.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for test_name, result in self.test_results:
            status_icon = "✅" if result.get("status") == "PASS" else "❌" if result.get("status") == "FAIL" else "⚠️"
            print(f"   {status_icon} {test_name}: {result.get('status', 'UNKNOWN')}")
            
            if result.get("error"):
                print(f"      Error: {result['error']}")
        
        # Save detailed report
        with open('comprehensive_test_report.json', 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'summary': {'total': total, 'passed': passed, 'failed': total - passed},
                'results': self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved: comprehensive_test_report.json")

def main():
    """Main testing function"""
    tester = ComprehensiveSeleniumDogtailTester()
    tester.run_comprehensive_tests()

if __name__ == '__main__':
    main()
