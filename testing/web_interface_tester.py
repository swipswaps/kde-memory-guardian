#!/usr/bin/env python3
"""
🎭 Playwright Web Interface Tester
Comprehensive testing and screenshot capture for all clipboard management interfaces
"""

import asyncio
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright
import requests
from datetime import datetime

class WebInterfaceTester:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.screenshots_dir = self.base_dir / "screenshots"
        self.reports_dir = self.base_dir / "reports"
        
        # Create directories
        self.screenshots_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'interfaces': {},
            'summary': {}
        }
        
        # Interface configurations
        self.interfaces = {
            'database_server': {
                'url': 'http://localhost:5000',
                'name': 'Database Management Server',
                'expected_elements': [
                    'h1:has-text("KDE Memory Guardian")',
                    'text="Total Entries"',
                    'text="Database Size"',
                    'button:has-text("SQLite Browser")'
                ]
            },
            'enhanced_hub': {
                'url': 'http://localhost:3001',
                'name': 'Enhanced Data Integration Hub',
                'expected_elements': [
                    'text="Enhanced Data Integration"',
                    'text="Interactive Visualizations"',
                    'text="Data Sources"',
                    '.visualization-container'
                ]
            },
            'react_app': {
                'url': 'http://localhost:3000',
                'name': 'React Clipboard Visualizer',
                'expected_elements': [
                    'text="Clipboard Intelligence"',
                    'text="Intelligence Dashboard"',
                    'text="Chart Type Selector"',
                    'text="Data Table"'
                ]
            }
        }

    async def test_api_endpoints(self):
        """Test API endpoints before UI testing"""
        print("🔍 Testing API endpoints...")
        
        api_tests = {
            'database_stats': 'http://localhost:5000/api/stats',
            'enhanced_stats': 'http://localhost:3001/api/enhanced-stats',
            'clipboard_history': 'http://localhost:3001/api/clipboard/history'
        }
        
        api_results = {}
        
        for name, url in api_tests.items():
            try:
                response = requests.get(url, timeout=5)
                api_results[name] = {
                    'status': response.status_code,
                    'success': response.status_code == 200,
                    'data_size': len(response.text) if response.status_code == 200 else 0
                }
                
                if name == 'clipboard_history' and response.status_code == 200:
                    try:
                        data = response.json()
                        api_results[name]['entry_count'] = len(data) if isinstance(data, list) else 0
                    except:
                        api_results[name]['entry_count'] = 0
                        
                print(f"  ✅ {name}: {response.status_code} ({api_results[name].get('data_size', 0)} bytes)")
                
            except Exception as e:
                api_results[name] = {
                    'status': 'error',
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {name}: {str(e)}")
        
        self.test_results['api_tests'] = api_results
        return api_results

    async def capture_interface_screenshot(self, page, interface_key, interface_config):
        """Capture screenshot and analyze interface"""
        print(f"📸 Testing {interface_config['name']}...")
        
        try:
            # Navigate to interface
            await page.goto(interface_config['url'], wait_until='networkidle', timeout=10000)
            
            # Wait for page to load
            await page.wait_for_timeout(3000)
            
            # Take full page screenshot
            screenshot_path = self.screenshots_dir / f"{interface_key}_{int(time.time())}.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)
            
            # Test expected elements
            element_results = {}
            for element_selector in interface_config['expected_elements']:
                try:
                    element = await page.wait_for_selector(element_selector, timeout=2000)
                    element_results[element_selector] = {
                        'found': True,
                        'visible': await element.is_visible() if element else False
                    }
                except:
                    element_results[element_selector] = {
                        'found': False,
                        'visible': False
                    }
            
            # Get page title and basic info
            title = await page.title()
            url = page.url
            
            # Check for JavaScript errors
            js_errors = []
            page.on('pageerror', lambda error: js_errors.append(str(error)))
            
            # Get page content stats
            content = await page.content()
            
            interface_result = {
                'url': url,
                'title': title,
                'screenshot': str(screenshot_path),
                'content_length': len(content),
                'elements_found': sum(1 for r in element_results.values() if r['found']),
                'elements_total': len(element_results),
                'element_details': element_results,
                'js_errors': js_errors,
                'success': len(js_errors) == 0 and sum(1 for r in element_results.values() if r['found']) > 0
            }
            
            self.test_results['interfaces'][interface_key] = interface_result
            
            success_rate = (interface_result['elements_found'] / interface_result['elements_total']) * 100
            print(f"  ✅ Screenshot saved: {screenshot_path}")
            print(f"  📊 Elements found: {interface_result['elements_found']}/{interface_result['elements_total']} ({success_rate:.1f}%)")
            
            if js_errors:
                print(f"  ⚠️  JavaScript errors: {len(js_errors)}")
            
            return interface_result
            
        except Exception as e:
            error_result = {
                'url': interface_config['url'],
                'error': str(e),
                'success': False
            }
            self.test_results['interfaces'][interface_key] = error_result
            print(f"  ❌ Error testing {interface_config['name']}: {str(e)}")
            return error_result

    async def test_interactive_elements(self, page, interface_key):
        """Test interactive elements specific to each interface"""
        print(f"🖱️  Testing interactive elements for {interface_key}...")
        
        interactions = []
        
        try:
            if interface_key == 'database_server':
                # Test SQL query interface
                sql_textarea = await page.query_selector('#sql-query')
                if sql_textarea:
                    await sql_textarea.fill('SELECT COUNT(*) FROM clipboard_history;')
                    interactions.append('sql_query_filled')
                
                # Test execute button
                execute_btn = await page.query_selector('button:has-text("Execute Query")')
                if execute_btn:
                    await execute_btn.click()
                    await page.wait_for_timeout(1000)
                    interactions.append('execute_query_clicked')
            
            elif interface_key == 'enhanced_hub':
                # Test data source cards
                clipboard_card = await page.query_selector('[data-source="clipboard"]')
                if clipboard_card:
                    await clipboard_card.click()
                    await page.wait_for_timeout(1000)
                    interactions.append('clipboard_card_clicked')
            
            elif interface_key == 'react_app':
                # Test chart type selector
                chart_selector = await page.query_selector('.chart-type-selector')
                if chart_selector:
                    interactions.append('chart_selector_found')
        
        except Exception as e:
            print(f"  ⚠️  Interaction error: {str(e)}")
        
        return interactions

    async def run_comprehensive_test(self):
        """Run comprehensive test of all interfaces"""
        print("🎭 Starting Playwright Web Interface Testing...")
        print("=" * 60)
        
        # Test APIs first
        await self.test_api_endpoints()
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Test each interface
            for interface_key, interface_config in self.interfaces.items():
                print(f"\n🌐 Testing {interface_config['name']}...")
                
                # Capture screenshot and analyze
                result = await self.capture_interface_screenshot(page, interface_key, interface_config)
                
                if result.get('success'):
                    # Test interactive elements
                    interactions = await self.test_interactive_elements(page, interface_key)
                    result['interactions'] = interactions
            
            await browser.close()
        
        # Generate summary
        self.generate_summary()
        
        # Save detailed report
        report_path = self.reports_dir / f"test_report_{int(time.time())}.json"
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📋 Detailed report saved: {report_path}")
        
        return self.test_results

    def generate_summary(self):
        """Generate test summary"""
        total_interfaces = len(self.interfaces)
        successful_interfaces = sum(1 for r in self.test_results['interfaces'].values() if r.get('success', False))
        
        api_tests = self.test_results.get('api_tests', {})
        successful_apis = sum(1 for r in api_tests.values() if r.get('success', False))
        
        self.test_results['summary'] = {
            'total_interfaces': total_interfaces,
            'successful_interfaces': successful_interfaces,
            'interface_success_rate': (successful_interfaces / total_interfaces) * 100 if total_interfaces > 0 else 0,
            'total_api_tests': len(api_tests),
            'successful_api_tests': successful_apis,
            'api_success_rate': (successful_apis / len(api_tests)) * 100 if api_tests else 0,
            'overall_success': successful_interfaces == total_interfaces and successful_apis == len(api_tests)
        }

    def print_summary(self):
        """Print test summary to console"""
        summary = self.test_results['summary']
        
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        print(f"📊 Interface Tests: {summary['successful_interfaces']}/{summary['total_interfaces']} "
              f"({summary['interface_success_rate']:.1f}% success)")
        
        print(f"🔗 API Tests: {summary['successful_api_tests']}/{summary['total_api_tests']} "
              f"({summary['api_success_rate']:.1f}% success)")
        
        print(f"🎯 Overall Success: {'✅ PASS' if summary['overall_success'] else '❌ FAIL'}")
        
        # Print interface details
        print("\n📱 INTERFACE DETAILS:")
        for interface_key, result in self.test_results['interfaces'].items():
            interface_name = self.interfaces[interface_key]['name']
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            print(f"  {status} {interface_name}")
            
            if 'elements_found' in result:
                print(f"    📊 Elements: {result['elements_found']}/{result['elements_total']}")
            
            if result.get('error'):
                print(f"    ❌ Error: {result['error']}")
        
        # Print API details
        print("\n🔗 API DETAILS:")
        for api_name, result in self.test_results.get('api_tests', {}).items():
            status = "✅ PASS" if result.get('success') else "❌ FAIL"
            print(f"  {status} {api_name}")
            
            if 'entry_count' in result:
                print(f"    📊 Entries: {result['entry_count']}")
            elif 'data_size' in result:
                print(f"    📊 Data: {result['data_size']} bytes")
            
            if result.get('error'):
                print(f"    ❌ Error: {result['error']}")

async def main():
    """Main testing function"""
    tester = WebInterfaceTester()
    
    try:
        results = await tester.run_comprehensive_test()
        tester.print_summary()
        
        return results
        
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(main())
