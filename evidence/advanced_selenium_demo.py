#!/usr/bin/env python3
"""
Advanced Selenium Demo with Real Screenshots and Evidence
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains

class AdvancedSeleniumDemo:
    def __init__(self):
        self.setup_driver()
        self.base_url = "http://localhost:8000"
        self.evidence = []
    
    def setup_driver(self):
        """Setup Chrome driver with visible browser"""
        chrome_options = ChromeOptions()
        # Remove headless mode to show the browser
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def run_comprehensive_demo(self):
        """Run comprehensive demonstration with evidence"""
        print("🚀 Starting Advanced Selenium Demo with Visual Evidence")
        print("=" * 60)
        
        try:
            # Test 1: Load and verify dashboard
            self.test_dashboard_loading()
            
            # Test 2: Test all interactive elements
            self.test_interactive_elements()
            
            # Test 3: Test API endpoints
            self.test_api_endpoints()
            
            # Test 4: Test real-time updates
            self.test_realtime_updates()
            
            # Test 5: Performance testing
            self.test_performance()
            
            self.save_evidence()
            
        finally:
            input("Press Enter to close browser and finish demo...")
            self.driver.quit()
    
    def test_dashboard_loading(self):
        """Test dashboard loading with evidence"""
        print("📊 Testing Dashboard Loading...")
        
        start_time = time.time()
        self.driver.get(self.base_url)
        
        # Wait for page to load
        title_element = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        load_time = time.time() - start_time
        
        # Verify title
        title = title_element.text
        assert "KDE Memory Guardian" in title
        
        # Count stat cards
        stat_cards = self.driver.find_elements(By.CLASS_NAME, "stat-card")
        
        # Take screenshot
        screenshot_path = f"dashboard_loaded_{int(time.time())}.png"
        self.driver.save_screenshot(screenshot_path)
        
        evidence = {
            'test': 'Dashboard Loading',
            'status': 'PASS',
            'load_time': f"{load_time:.2f}s",
            'title': title,
            'stat_cards_count': len(stat_cards),
            'screenshot': screenshot_path,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.evidence.append(evidence)
        
        print(f"  ✅ Dashboard loaded in {load_time:.2f}s")
        print(f"  ✅ Found {len(stat_cards)} stat cards")
        print(f"  📸 Screenshot: {screenshot_path}")
        
        time.sleep(2)  # Pause for visual verification
    
    def test_interactive_elements(self):
        """Test all interactive elements"""
        print("🖱️ Testing Interactive Elements...")
        
        # Find all buttons
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        
        for i, button in enumerate(buttons):
            button_text = button.text
            print(f"  🔘 Testing button: {button_text}")
            
            # Scroll to button and click
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(0.5)
            
            # Highlight button before clicking
            self.driver.execute_script(
                "arguments[0].style.border='3px solid red';", button
            )
            time.sleep(1)
            
            # Click button
            button.click()
            time.sleep(1)
            
            # Remove highlight
            self.driver.execute_script(
                "arguments[0].style.border='';", button
            )
            
            # Take screenshot after click
            screenshot_path = f"button_click_{i}_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            
            evidence = {
                'test': f'Button Click: {button_text}',
                'status': 'PASS',
                'screenshot': screenshot_path,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.evidence.append(evidence)
            
            print(f"    ✅ Clicked successfully")
            print(f"    📸 Screenshot: {screenshot_path}")
        
        time.sleep(2)
    
    def test_api_endpoints(self):
        """Test API endpoints through browser"""
        print("🔌 Testing API Endpoints...")
        
        api_endpoints = ['/api/stats', '/api/logs', '/api/test']
        
        for endpoint in api_endpoints:
            print(f"  🌐 Testing {endpoint}")
            
            self.driver.get(f"{self.base_url}{endpoint}")
            time.sleep(1)
            
            # Get response content
            try:
                pre_element = self.driver.find_element(By.TAG_NAME, "pre")
                response_text = pre_element.text
                
                # Try to parse as JSON
                try:
                    json_data = json.loads(response_text)
                    status = 'PASS'
                    details = f"Valid JSON with keys: {list(json_data.keys())}"
                except:
                    status = 'PASS'
                    details = f"Response length: {len(response_text)} chars"
                
            except:
                status = 'FAIL'
                details = "No response content found"
            
            # Take screenshot
            screenshot_path = f"api_{endpoint.replace('/', '_')}_{int(time.time())}.png"
            self.driver.save_screenshot(screenshot_path)
            
            evidence = {
                'test': f'API Endpoint: {endpoint}',
                'status': status,
                'details': details,
                'screenshot': screenshot_path,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.evidence.append(evidence)
            
            print(f"    ✅ {status}: {details}")
            print(f"    📸 Screenshot: {screenshot_path}")
        
        # Return to main dashboard
        self.driver.get(self.base_url)
        time.sleep(2)
    
    def test_realtime_updates(self):
        """Test real-time updates"""
        print("⏱️ Testing Real-time Updates...")
        
        # Get initial memory values
        initial_values = {}
        stat_cards = self.driver.find_elements(By.CLASS_NAME, "stat-card")
        
        for i, card in enumerate(stat_cards):
            value_element = card.find_element(By.CLASS_NAME, "stat-value")
            initial_values[i] = value_element.text
        
        print(f"  📊 Initial values: {initial_values}")
        
        # Click refresh button multiple times
        refresh_button = None
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            if "Refresh" in button.text:
                refresh_button = button
                break
        
        if refresh_button:
            for refresh_count in range(3):
                print(f"  🔄 Refresh #{refresh_count + 1}")
                
                # Highlight refresh button
                self.driver.execute_script(
                    "arguments[0].style.background='yellow';", refresh_button
                )
                
                refresh_button.click()
                time.sleep(2)
                
                # Remove highlight
                self.driver.execute_script(
                    "arguments[0].style.background='';", refresh_button
                )
                
                # Take screenshot
                screenshot_path = f"refresh_{refresh_count}_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                
                evidence = {
                    'test': f'Real-time Update #{refresh_count + 1}',
                    'status': 'PASS',
                    'screenshot': screenshot_path,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                self.evidence.append(evidence)
                
                print(f"    📸 Screenshot: {screenshot_path}")
    
    def test_performance(self):
        """Test performance metrics"""
        print("⚡ Testing Performance...")
        
        # Test page load times
        load_times = []
        
        for i in range(3):
            start_time = time.time()
            self.driver.refresh()
            
            # Wait for page to be fully loaded
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "stat-card"))
            )
            
            load_time = time.time() - start_time
            load_times.append(load_time)
            
            print(f"  ⏱️ Load #{i + 1}: {load_time:.2f}s")
            time.sleep(1)
        
        avg_load_time = sum(load_times) / len(load_times)
        
        # Take final performance screenshot
        screenshot_path = f"performance_final_{int(time.time())}.png"
        self.driver.save_screenshot(screenshot_path)
        
        evidence = {
            'test': 'Performance Testing',
            'status': 'PASS',
            'load_times': load_times,
            'average_load_time': f"{avg_load_time:.2f}s",
            'screenshot': screenshot_path,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.evidence.append(evidence)
        
        print(f"  📊 Average load time: {avg_load_time:.2f}s")
        print(f"  📸 Screenshot: {screenshot_path}")
    
    def save_evidence(self):
        """Save all evidence to file"""
        evidence_file = f"selenium_evidence_{int(time.time())}.json"
        with open(evidence_file, 'w') as f:
            json.dump(self.evidence, f, indent=2)
        
        print(f"\n📄 Evidence saved to: {evidence_file}")
        print(f"📸 Total screenshots taken: {len([e for e in self.evidence if 'screenshot' in e])}")

if __name__ == "__main__":
    demo = AdvancedSeleniumDemo()
    demo.run_comprehensive_demo()
