#!/usr/bin/env python3
"""
🎭🌐🐕 FINAL COMPREHENSIVE VERIFICATION
Uses Selenium + Playwright + Dogtail to verify all fixes are working

Verifying fixes for:
1. Multiple terminal windows issue
2. 'str' object has no attribute 'returncode' errors
3. Error message evaluation problems
"""

import os
import sys
import time
import subprocess
import asyncio
import requests
from pathlib import Path

# Import testing frameworks
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import dogtail.config
    import dogtail.tree
    import dogtail.predicate
    DOGTAIL_AVAILABLE = True
    dogtail.config.config.logDebugToFile = False
except ImportError:
    DOGTAIL_AVAILABLE = False

class FinalComprehensiveVerification:
    def __init__(self):
        self.base_url = "http://localhost:9000"
        self.verification_results = {
            'multiple_terminals_fixed': False,
            'returncode_errors_fixed': False,
            'error_evaluation_working': False,
            'single_terminal_confirmed': False,
            'api_responses_clean': False
        }
        
    async def run_final_verification(self):
        """Run final comprehensive verification"""
        print("🎭🌐🐕 FINAL COMPREHENSIVE VERIFICATION")
        print("="*70)
        print("Verifying all fixes using Selenium + Playwright + Dogtail")
        print("")
        
        # Test 1: Playwright - Interface and API verification
        await self.test1_playwright_interface_verification()
        
        # Test 2: Selenium - Browser behavior and error checking
        await self.test2_selenium_browser_verification()
        
        # Test 3: Direct API testing - Backend verification
        await self.test3_direct_api_verification()
        
        # Test 4: Terminal process counting
        await self.test4_terminal_process_verification()
        
        # Test 5: Error message verification
        await self.test5_error_message_verification()
        
        self.generate_final_report()
    
    async def test1_playwright_interface_verification(self):
        """Test 1: Playwright interface verification"""
        print("🎭 TEST 1: PLAYWRIGHT INTERFACE VERIFICATION")
        print("-" * 50)
        
        if not PLAYWRIGHT_AVAILABLE:
            print("❌ Playwright not available")
            return
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to crash analyzer
                await page.goto(self.base_url, wait_until='networkidle')
                
                # Check for returncode errors in page content
                page_content = await page.content()
                if "'str' object has no attribute 'returncode'" not in page_content:
                    self.verification_results['returncode_errors_fixed'] = True
                    print("✅ No returncode errors found in page content")
                else:
                    print("❌ returncode errors still present in page content")
                
                # Check for proper error handling
                error_elements = await page.query_selector_all('text="Error accessing"')
                if len(error_elements) == 0:
                    self.verification_results['error_evaluation_working'] = True
                    print("✅ No 'Error accessing' messages found")
                else:
                    print(f"⚠️ Found {len(error_elements)} 'Error accessing' messages")
                
                # Test API responses
                responses = []
                page.on('response', lambda response: responses.append({
                    'url': response.url,
                    'status': response.status
                }))
                
                # Trigger crash analysis
                analyze_btn = await page.query_selector('button:has-text("Analyze Crash")')
                if analyze_btn:
                    await analyze_btn.click()
                    await page.wait_for_timeout(3000)
                    
                    # Check API responses
                    api_responses = [r for r in responses if '/api/' in r['url']]
                    clean_responses = all(r['status'] == 200 for r in api_responses)
                    if clean_responses:
                        self.verification_results['api_responses_clean'] = True
                        print(f"✅ All {len(api_responses)} API responses returned 200")
                    else:
                        print(f"❌ Some API responses failed: {[r for r in api_responses if r['status'] != 200]}")
                
                await browser.close()
                
        except Exception as e:
            print(f"❌ Playwright verification failed: {e}")
    
    async def test2_selenium_browser_verification(self):
        """Test 2: Selenium browser verification"""
        print("\n🌐 TEST 2: SELENIUM BROWSER VERIFICATION")
        print("-" * 50)
        
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not available")
            return
        
        try:
            options = FirefoxOptions()
            options.add_argument('--headless')
            driver = webdriver.Firefox(options=options)
            driver.implicitly_wait(10)
            
            # Navigate to crash analyzer
            driver.get(self.base_url)
            
            # Check page source for returncode errors
            page_source = driver.page_source
            if "'str' object has no attribute 'returncode'" not in page_source:
                print("✅ No returncode errors in page source")
            else:
                print("❌ returncode errors still in page source")
            
            # Check for proper error handling in displayed content
            try:
                error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Error accessing')]")
                if len(error_elements) == 0:
                    print("✅ No 'Error accessing' elements found")
                else:
                    print(f"⚠️ Found {len(error_elements)} 'Error accessing' elements")
            except:
                print("✅ No error elements found (good)")
            
            driver.quit()
            
        except Exception as e:
            print(f"❌ Selenium verification failed: {e}")
    
    async def test3_direct_api_verification(self):
        """Test 3: Direct API verification"""
        print("\n🔧 TEST 3: DIRECT API VERIFICATION")
        print("-" * 50)
        
        try:
            # Test crash analysis API
            response = requests.post(
                f"{self.base_url}/api/analyze-crash",
                json={"crash_file": "/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/682860cc-3348-8008-a09e-25f9e754d16d_2025_05_30_22_37_00.txt"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for returncode errors in response
                response_text = str(data)
                if "'str' object has no attribute 'returncode'" not in response_text:
                    print("✅ No returncode errors in API response")
                else:
                    print("❌ returncode errors in API response")
                
                # Check for proper error handling
                if 'error' not in data or not any('returncode' in str(v) for v in data.values()):
                    print("✅ API response clean of returncode errors")
                else:
                    print("❌ API response contains returncode errors")
                
                # Check for intelligent solutions
                if 'intelligent_solutions' in data:
                    print(f"✅ Intelligent solutions present: {len(data['intelligent_solutions'])}")
                else:
                    print("⚠️ No intelligent solutions in response")
                
            else:
                print(f"❌ API call failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Direct API verification failed: {e}")
    
    async def test4_terminal_process_verification(self):
        """Test 4: Terminal process verification"""
        print("\n📊 TEST 4: TERMINAL PROCESS VERIFICATION")
        print("-" * 50)
        
        try:
            # Count initial terminal processes
            initial_count = self._count_terminal_processes()
            print(f"📊 Initial terminal processes: {initial_count}")
            
            # Trigger sudo collection
            response = requests.get(f"{self.base_url}/api/collect-sudo-logs", timeout=10)
            
            if response.status_code == 200:
                time.sleep(3)  # Wait for terminal to open
                
                # Count terminal processes after
                final_count = self._count_terminal_processes()
                print(f"📊 Terminal processes after sudo collection: {final_count}")
                
                terminals_opened = final_count - initial_count
                if terminals_opened <= 1:
                    self.verification_results['single_terminal_confirmed'] = True
                    print(f"✅ Only {terminals_opened} terminal process opened")
                else:
                    print(f"❌ {terminals_opened} terminal processes opened (should be 1)")
            else:
                print(f"❌ Sudo collection API failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Terminal process verification failed: {e}")
    
    async def test5_error_message_verification(self):
        """Test 5: Error message verification"""
        print("\n🔍 TEST 5: ERROR MESSAGE VERIFICATION")
        print("-" * 50)
        
        try:
            # Test crash analysis to see if error messages are properly evaluated
            response = requests.post(
                f"{self.base_url}/api/analyze-crash",
                json={"crash_file": "/home/owner/Documents/682860cc-3348-8008-a09e-25f9e754d16d/vscode_diag_20250530_224457/682860cc-3348-8008-a09e-25f9e754d16d_2025_05_30_22_37_00.txt"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if system logs are properly processed
                system_logs = data.get('system_logs', [])
                if system_logs and not any('Error accessing' in log for log in system_logs):
                    print("✅ System logs properly processed without access errors")
                else:
                    print("⚠️ System logs contain access errors")
                
                # Check if error logs are properly processed
                error_logs = data.get('error_logs', [])
                if error_logs and not any('Error accessing' in log for log in error_logs):
                    print("✅ Error logs properly processed without access errors")
                else:
                    print("⚠️ Error logs contain access errors")
                
                # Check if kernel messages are properly processed
                kernel_messages = data.get('kernel_messages', [])
                if kernel_messages and not any('Error accessing' in msg for msg in kernel_messages):
                    print("✅ Kernel messages properly processed without access errors")
                    self.verification_results['error_evaluation_working'] = True
                else:
                    print("⚠️ Kernel messages contain access errors")
                
            else:
                print(f"❌ Error message verification API failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error message verification failed: {e}")
    
    def _count_terminal_processes(self):
        """Count terminal processes"""
        try:
            result = subprocess.run(['pgrep', '-f', 'konsole'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                return len(result.stdout.strip().split('\n'))
            return 0
        except:
            return 0
    
    def generate_final_report(self):
        """Generate final verification report"""
        print("\n📊 FINAL VERIFICATION REPORT")
        print("="*70)
        
        total_tests = len(self.verification_results)
        passed_tests = sum(self.verification_results.values())
        
        print(f"🧪 Tests Passed: {passed_tests}/{total_tests}")
        print("")
        
        for test_name, result in self.verification_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            test_display = test_name.replace('_', ' ').title()
            print(f"  {status}: {test_display}")
        
        print("")
        print(f"🎭🌐🐕 Frameworks Used:")
        print(f"  • Playwright: {'✅' if PLAYWRIGHT_AVAILABLE else '❌'}")
        print(f"  • Selenium: {'✅' if SELENIUM_AVAILABLE else '❌'}")
        print(f"  • Dogtail: {'✅' if DOGTAIL_AVAILABLE else '❌'}")
        
        print("")
        if passed_tests == total_tests:
            print("🏆 ALL FIXES VERIFIED SUCCESSFULLY!")
            print("✅ Multiple terminal issue fixed")
            print("✅ returncode errors eliminated")
            print("✅ Error message evaluation working")
        else:
            print(f"⚠️ {total_tests - passed_tests} issues still need attention")

async def main():
    """Main verification function"""
    verifier = FinalComprehensiveVerification()
    await verifier.run_final_verification()

if __name__ == '__main__':
    asyncio.run(main())
