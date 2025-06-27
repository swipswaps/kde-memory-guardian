#!/usr/bin/env python3
"""
Comprehensive Testing Implementation with Selenium, Playwright, and Dogtail
As requested by user - actual implementation, not just acknowledgment
"""

import asyncio
import time
import subprocess
import sys
from pathlib import Path

# Test imports and availability
def test_framework_availability():
    """Test that all requested frameworks are available"""
    results = {}
    
    # Test Selenium
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        results['selenium'] = True
        print("✅ Selenium: Available")
    except ImportError as e:
        results['selenium'] = False
        print(f"❌ Selenium: Not available - {e}")
    
    # Test Playwright
    try:
        from playwright.async_api import async_playwright
        results['playwright'] = True
        print("✅ Playwright: Available")
    except ImportError as e:
        results['playwright'] = False
        print(f"❌ Playwright: Not available - {e}")
    
    # Test Dogtail
    try:
        import dogtail.tree
        import dogtail.predicate
        from dogtail.config import config
        results['dogtail'] = True
        print("✅ Dogtail: Available")
    except ImportError as e:
        results['dogtail'] = False
        print(f"❌ Dogtail: Not available - {e}")
    
    return results

def selenium_crash_analyzer_test():
    """Selenium test of crash analyzer interface"""
    print("\n🔍 SELENIUM TESTING:")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Navigate to crash analyzer
            print("  📱 Navigating to http://localhost:9000")
            driver.get("http://localhost:9000")
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Test crash file input
            crash_input = driver.find_element(By.ID, "crashFile")
            if crash_input:
                print("  ✅ Crash file input found")
                # Test if text is selectable
                crash_input.click()
                driver.execute_script("arguments[0].select();", crash_input)
                selected_text = driver.execute_script("return window.getSelection().toString();")
                print(f"  📝 Input text selectable: {bool(selected_text) or 'placeholder text'}")
            
            # Test analyze button
            analyze_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Analyze')]")
            if analyze_buttons:
                print(f"  🔘 Found {len(analyze_buttons)} analyze buttons")
                for i, btn in enumerate(analyze_buttons):
                    btn_text = btn.text
                    print(f"    Button {i+1}: {btn_text}")
                    
                    # Test button text selectability
                    btn.click()
                    driver.execute_script("arguments[0].focus(); window.getSelection().selectAllChildren(arguments[0]);", btn)
                    selected = driver.execute_script("return window.getSelection().toString();")
                    print(f"    Text selectable: {bool(selected)}")
            
            # Test solution links
            solution_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'official_documentation')]")
            if solution_links:
                print(f"  🔗 Found {len(solution_links)} solution links")
                for link in solution_links:
                    href = link.get_attribute('href')
                    print(f"    Link: {href}")
                    
                    # Test link functionality
                    original_window = driver.current_window_handle
                    link.click()
                    time.sleep(2)
                    
                    # Check if redirect worked
                    if len(driver.window_handles) > 1:
                        driver.switch_to.window(driver.window_handles[-1])
                        current_url = driver.current_url
                        print(f"    Redirected to: {current_url}")
                        driver.close()
                        driver.switch_to.window(original_window)
                    else:
                        print(f"    Current URL: {driver.current_url}")
            
            print("  ✅ Selenium test completed successfully")
            return True
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"  ❌ Selenium test failed: {e}")
        return False

async def playwright_crash_analyzer_test():
    """Playwright test of crash analyzer interface"""
    print("\n🎭 PLAYWRIGHT TESTING:")
    
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Navigate to crash analyzer
                print("  📱 Navigating to http://localhost:9000")
                await page.goto("http://localhost:9000", wait_until="networkidle")
                
                # Test page title
                title = await page.title()
                print(f"  📄 Page title: {title}")
                
                # Test crash file input
                crash_input = await page.query_selector("#crashFile")
                if crash_input:
                    print("  ✅ Crash file input found")
                    
                    # Test input value and selectability
                    input_value = await crash_input.get_attribute("value")
                    print(f"  📝 Input value: {input_value}")
                    
                    # Test text selection
                    await crash_input.click(click_count=3)
                    selected_text = await page.evaluate("window.getSelection().toString()")
                    print(f"  📝 Text selection works: {bool(selected_text)}")
                
                # Test analyze buttons
                analyze_buttons = await page.query_selector_all("button")
                analyze_btns = [btn for btn in analyze_buttons if "analyze" in (await btn.text_content()).lower()]
                
                if analyze_btns:
                    print(f"  🔘 Found {len(analyze_btns)} analyze buttons")
                    for i, btn in enumerate(analyze_btns):
                        btn_text = await btn.text_content()
                        print(f"    Button {i+1}: {btn_text}")
                        
                        # Test button text selectability
                        await btn.click(click_count=3)
                        selected = await page.evaluate("window.getSelection().toString()")
                        print(f"    Text selectable: {bool(selected)}")
                
                # Test solution URLs
                solution_links = await page.query_selector_all("a[href*='official_documentation']")
                if solution_links:
                    print(f"  🔗 Found {len(solution_links)} solution links")
                    for link in solution_links:
                        href = await link.get_attribute("href")
                        print(f"    Link: {href}")
                        
                        # Test link functionality
                        async with context.expect_page() as new_page_info:
                            await link.click()
                        new_page = await new_page_info.value
                        await new_page.wait_for_load_state()
                        
                        final_url = new_page.url
                        print(f"    Final URL: {final_url}")
                        await new_page.close()
                
                # Take screenshot for evidence
                await page.screenshot(path="playwright_crash_analyzer_test.png", full_page=True)
                print("  📸 Screenshot saved: playwright_crash_analyzer_test.png")
                
                print("  ✅ Playwright test completed successfully")
                return True
                
            finally:
                await browser.close()
                
    except Exception as e:
        print(f"  ❌ Playwright test failed: {e}")
        return False

def dogtail_crash_analyzer_test():
    """Dogtail test of crash analyzer interface"""
    print("\n🐕 DOGTAIL TESTING:")
    
    try:
        import dogtail.tree
        import dogtail.predicate
        from dogtail.config import config
        
        # Configure dogtail
        config.logDebugToFile = False
        config.logDebugToStdOut = False
        
        # Find browser window
        print("  🔍 Searching for browser window...")
        desktop = dogtail.tree.root
        
        # Look for browser windows (Chrome, Firefox, etc.)
        browser_apps = ['chrome', 'firefox', 'chromium']
        browser_window = None
        
        for app_name in browser_apps:
            try:
                app = desktop.application(app_name)
                if app:
                    browser_window = app
                    print(f"  ✅ Found browser: {app_name}")
                    break
            except:
                continue
        
        if not browser_window:
            print("  ❌ No browser window found")
            return False
        
        # Test accessibility of crash analyzer elements
        try:
            # Look for input fields
            inputs = browser_window.findChildren(dogtail.predicate.GenericPredicate(roleName='entry'))
            print(f"  📝 Found {len(inputs)} input fields")
            
            for i, input_field in enumerate(inputs):
                if input_field.text:
                    print(f"    Input {i+1}: {input_field.text[:50]}...")
                    
                    # Test if input is accessible
                    try:
                        input_field.click()
                        input_field.typeText("test")
                        print(f"    Input {i+1} is accessible")
                    except:
                        print(f"    Input {i+1} is not accessible")
            
            # Look for buttons
            buttons = browser_window.findChildren(dogtail.predicate.GenericPredicate(roleName='push button'))
            print(f"  🔘 Found {len(buttons)} buttons")
            
            for i, button in enumerate(buttons):
                if button.name:
                    print(f"    Button {i+1}: {button.name}")
                    
                    # Test button accessibility
                    try:
                        button.click()
                        print(f"    Button {i+1} is clickable")
                    except:
                        print(f"    Button {i+1} is not clickable")
            
            # Look for links
            links = browser_window.findChildren(dogtail.predicate.GenericPredicate(roleName='link'))
            print(f"  🔗 Found {len(links)} links")
            
            for i, link in enumerate(links):
                if link.name:
                    print(f"    Link {i+1}: {link.name}")
            
            print("  ✅ Dogtail test completed successfully")
            return True
            
        except Exception as e:
            print(f"  ❌ Dogtail accessibility test failed: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ Dogtail test failed: {e}")
        return False

def run_comprehensive_tests():
    """Run all three testing frameworks as requested"""
    print("🧪 COMPREHENSIVE TESTING WITH SELENIUM, PLAYWRIGHT, AND DOGTAIL")
    print("=" * 70)
    
    # Check framework availability
    availability = test_framework_availability()
    
    results = {}
    
    # Run Selenium tests
    if availability['selenium']:
        results['selenium'] = selenium_crash_analyzer_test()
    else:
        results['selenium'] = False
        print("⚠️ Skipping Selenium tests - not available")
    
    # Run Playwright tests
    if availability['playwright']:
        results['playwright'] = asyncio.run(playwright_crash_analyzer_test())
    else:
        results['playwright'] = False
        print("⚠️ Skipping Playwright tests - not available")
    
    # Run Dogtail tests
    if availability['dogtail']:
        results['dogtail'] = dogtail_crash_analyzer_test()
    else:
        results['dogtail'] = False
        print("⚠️ Skipping Dogtail tests - not available")
    
    # Summary
    print("\n📊 TEST RESULTS SUMMARY:")
    print("=" * 30)
    for framework, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{framework.upper()}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nOVERALL: {total_passed}/{total_tests} frameworks passed")
    
    return results

if __name__ == "__main__":
    run_comprehensive_tests()
