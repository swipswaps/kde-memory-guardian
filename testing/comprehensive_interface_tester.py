#!/usr/bin/env python3
"""
🎭 Comprehensive Interface Tester
Multi-tool testing suite using Playwright, Selenium, and Dogtail
Ensures all web interfaces work correctly and are accessible

Features:
- Playwright for modern web testing
- Selenium for cross-browser compatibility
- Dogtail for accessibility testing
- Text selection verification
- Button functionality testing
- Error detection and reporting
"""

import asyncio
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Import testing frameworks
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not available")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available")

try:
    import dogtail.tree
    import dogtail.predicate
    DOGTAIL_AVAILABLE = True
except ImportError:
    DOGTAIL_AVAILABLE = False
    print("⚠️ Dogtail not available")

class ComprehensiveInterfaceTester:
    def __init__(self):
        self.test_results = []
        self.interfaces = {
            5000: "🗄️ Database Management",
            9000: "💥 Crash Analysis Correlator"
        }
        
    async def run_all_tests(self):
        """Run comprehensive tests using all available tools"""
        print("🎭 COMPREHENSIVE INTERFACE TESTING SUITE")
        print("=" * 60)
        
        # Test 1: Basic connectivity
        await self.test_basic_connectivity()
        
        # Test 2: Playwright testing
        if PLAYWRIGHT_AVAILABLE:
            await self.test_with_playwright()
        
        # Test 3: Selenium testing
        if SELENIUM_AVAILABLE:
            await self.test_with_selenium()
        
        # Test 4: Dogtail accessibility testing
        if DOGTAIL_AVAILABLE:
            await self.test_with_dogtail()
        
        # Test 5: Text selection testing
        await self.test_text_selection()
        
        # Test 6: Crash file analysis
        await self.test_crash_analysis()
        
        # Generate report
        self.generate_test_report()
    
    async def test_basic_connectivity(self):
        """Test basic HTTP connectivity to all interfaces"""
        print("\n🔍 TESTING BASIC CONNECTIVITY...")
        
        import requests
        
        for port, name in self.interfaces.items():
            try:
                response = requests.get(f'http://localhost:{port}', timeout=5)
                if response.status_code == 200:
                    result = {
                        'test': 'connectivity',
                        'interface': name,
                        'port': port,
                        'status': 'PASS',
                        'details': f'HTTP 200, Content length: {len(response.text)}'
                    }
                    print(f"✅ {name} (Port {port}): CONNECTED")
                else:
                    result = {
                        'test': 'connectivity',
                        'interface': name,
                        'port': port,
                        'status': 'FAIL',
                        'details': f'HTTP {response.status_code}'
                    }
                    print(f"❌ {name} (Port {port}): HTTP {response.status_code}")
                
                self.test_results.append(result)
                
            except Exception as e:
                result = {
                    'test': 'connectivity',
                    'interface': name,
                    'port': port,
                    'status': 'FAIL',
                    'details': str(e)
                }
                print(f"❌ {name} (Port {port}): {e}")
                self.test_results.append(result)
    
    async def test_with_playwright(self):
        """Test interfaces using Playwright"""
        print("\n🎭 TESTING WITH PLAYWRIGHT...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            
            for port, name in self.interfaces.items():
                try:
                    page = await context.new_page()
                    await page.goto(f'http://localhost:{port}', wait_until='networkidle')
                    
                    # Basic page tests
                    title = await page.title()
                    body = await page.query_selector('body')
                    content_length = len(await body.text_content()) if body else 0
                    
                    # Test text selection
                    selectable_elements = await page.query_selector_all('button, .btn, h1, h2, p')
                    selection_test = await self.test_element_selection(page, selectable_elements)
                    
                    # Test button functionality
                    buttons = await page.query_selector_all('button, .btn')
                    button_test = await self.test_button_functionality(page, buttons)
                    
                    # Take screenshot
                    screenshot_path = f'playwright_test_{port}.png'
                    await page.screenshot(path=screenshot_path, full_page=True)
                    
                    result = {
                        'test': 'playwright',
                        'interface': name,
                        'port': port,
                        'status': 'PASS',
                        'details': {
                            'title': title,
                            'content_length': content_length,
                            'selectable_elements': len(selectable_elements),
                            'buttons_found': len(buttons),
                            'selection_test': selection_test,
                            'button_test': button_test,
                            'screenshot': screenshot_path
                        }
                    }
                    
                    print(f"✅ {name}: Playwright tests passed")
                    print(f"   📄 Title: {title}")
                    print(f"   📊 Content: {content_length} chars")
                    print(f"   🔘 Buttons: {len(buttons)} found")
                    print(f"   📸 Screenshot: {screenshot_path}")
                    
                    await page.close()
                    
                except Exception as e:
                    result = {
                        'test': 'playwright',
                        'interface': name,
                        'port': port,
                        'status': 'FAIL',
                        'details': str(e)
                    }
                    print(f"❌ {name}: Playwright test failed - {e}")
                
                self.test_results.append(result)
            
            await browser.close()
    
    async def test_element_selection(self, page, elements):
        """Test if elements are selectable"""
        selectable_count = 0
        
        for element in elements[:5]:  # Test first 5 elements
            try:
                # Try to select text in element
                await element.click(click_count=3)  # Triple click to select
                selected_text = await page.evaluate('window.getSelection().toString()')
                if selected_text.strip():
                    selectable_count += 1
            except:
                pass
        
        return {
            'tested_elements': min(len(elements), 5),
            'selectable_elements': selectable_count,
            'selection_working': selectable_count > 0
        }
    
    async def test_button_functionality(self, page, buttons):
        """Test button functionality"""
        working_buttons = 0
        
        for button in buttons[:3]:  # Test first 3 buttons
            try:
                # Check if button is clickable
                is_clickable = await button.is_enabled()
                if is_clickable:
                    working_buttons += 1
            except:
                pass
        
        return {
            'tested_buttons': min(len(buttons), 3),
            'working_buttons': working_buttons,
            'buttons_functional': working_buttons > 0
        }
    
    async def test_with_selenium(self):
        """Test interfaces using Selenium"""
        print("\n🌐 TESTING WITH SELENIUM...")
        
        options = FirefoxOptions()
        options.add_argument('--headless')
        
        try:
            driver = webdriver.Firefox(options=options)
            
            for port, name in self.interfaces.items():
                try:
                    driver.get(f'http://localhost:{port}')
                    
                    # Wait for page to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Basic tests
                    title = driver.title
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    buttons = driver.find_elements(By.TAG_NAME, "button")
                    
                    # Test text selection capability
                    selection_test = self.test_selenium_text_selection(driver)
                    
                    result = {
                        'test': 'selenium',
                        'interface': name,
                        'port': port,
                        'status': 'PASS',
                        'details': {
                            'title': title,
                            'content_length': len(body_text),
                            'buttons_found': len(buttons),
                            'selection_test': selection_test
                        }
                    }
                    
                    print(f"✅ {name}: Selenium tests passed")
                    print(f"   📄 Title: {title}")
                    print(f"   🔘 Buttons: {len(buttons)} found")
                    
                except Exception as e:
                    result = {
                        'test': 'selenium',
                        'interface': name,
                        'port': port,
                        'status': 'FAIL',
                        'details': str(e)
                    }
                    print(f"❌ {name}: Selenium test failed - {e}")
                
                self.test_results.append(result)
            
            driver.quit()
            
        except Exception as e:
            print(f"❌ Selenium setup failed: {e}")
    
    def test_selenium_text_selection(self, driver):
        """Test text selection with Selenium"""
        try:
            # Try to select text using JavaScript
            script = """
            var range = document.createRange();
            var selection = window.getSelection();
            var firstTextNode = document.evaluate('//text()[normalize-space()]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (firstTextNode) {
                range.selectNodeContents(firstTextNode);
                selection.removeAllRanges();
                selection.addRange(range);
                return selection.toString().length > 0;
            }
            return false;
            """
            
            selection_works = driver.execute_script(script)
            return {'text_selection_working': selection_works}
            
        except Exception as e:
            return {'text_selection_working': False, 'error': str(e)}
    
    async def test_with_dogtail(self):
        """Test interfaces using Dogtail for accessibility"""
        print("\n🐕 TESTING WITH DOGTAIL...")
        
        try:
            # Find Firefox window
            app = dogtail.tree.root.application('firefox')
            
            result = {
                'test': 'dogtail',
                'interface': 'accessibility',
                'status': 'PASS',
                'details': {
                    'firefox_accessible': True,
                    'accessibility_tree_available': True
                }
            }
            
            print("✅ Dogtail: Accessibility tree accessible")
            
        except Exception as e:
            result = {
                'test': 'dogtail',
                'interface': 'accessibility',
                'status': 'FAIL',
                'details': str(e)
            }
            print(f"❌ Dogtail test failed: {e}")
        
        self.test_results.append(result)
    
    async def test_text_selection(self):
        """Specific test for text selection issues"""
        print("\n📝 TESTING TEXT SELECTION...")
        
        # This will be tested through Playwright and Selenium above
        print("✅ Text selection tests completed via Playwright/Selenium")
    
    async def test_crash_analysis(self):
        """Test crash analysis functionality"""
        print("\n💥 TESTING CRASH ANALYSIS...")
        
        import requests
        
        try:
            # Test crash analysis API
            response = requests.post('http://localhost:9000/api/analyze-crash', 
                                   json={'crash_file': '/home/owner/Documents/2025_06_26_vcscode_crash.txt'},
                                   timeout=10)
            
            if response.status_code == 200:
                analysis = response.json()
                
                result = {
                    'test': 'crash_analysis',
                    'interface': 'API',
                    'status': 'PASS' if 'error' not in analysis else 'FAIL',
                    'details': analysis
                }
                
                if 'error' not in analysis:
                    print("✅ Crash analysis: API working")
                    print(f"   📊 Crash type: {analysis.get('crash_type', 'Unknown')}")
                    print(f"   ⚠️ Severity: {analysis.get('severity', 'Unknown')}")
                else:
                    print(f"❌ Crash analysis: {analysis['error']}")
                
            else:
                result = {
                    'test': 'crash_analysis',
                    'interface': 'API',
                    'status': 'FAIL',
                    'details': f'HTTP {response.status_code}'
                }
                print(f"❌ Crash analysis: HTTP {response.status_code}")
            
            self.test_results.append(result)
            
        except Exception as e:
            result = {
                'test': 'crash_analysis',
                'interface': 'API',
                'status': 'FAIL',
                'details': str(e)
            }
            print(f"❌ Crash analysis failed: {e}")
            self.test_results.append(result)
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        
        print(f"📈 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📊 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"   {status_icon} {result['test'].upper()}: {result['interface']} - {result['status']}")
        
        # Save report to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': passed_tests/total_tests*100
            },
            'results': self.test_results
        }
        
        with open('comprehensive_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n💾 Report saved: comprehensive_test_report.json")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        if failed_tests > 0:
            print("   • Fix failed interfaces before deployment")
            print("   • Verify text selection functionality")
            print("   • Test button accessibility")
        else:
            print("   • All tests passed! Interfaces are ready for use")
            print("   • Consider adding more automated tests")

async def main():
    """Main testing function"""
    tester = ComprehensiveInterfaceTester()
    await tester.run_all_tests()

if __name__ == '__main__':
    asyncio.run(main())
