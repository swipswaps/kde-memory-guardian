#!/usr/bin/env python3
"""
🔍 React App Data Loading Debugger
Specifically debug why React app isn't showing clipboard data
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def debug_react_app():
    """Debug React app data loading issues"""
    print("🔍 Debugging React App Data Loading...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser for debugging
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Enable console logging
        page.on('console', lambda msg: print(f"🖥️  Console: {msg.text}"))
        page.on('pageerror', lambda error: print(f"❌ Page Error: {error}"))
        
        try:
            print("📱 Loading React app...")
            await page.goto('http://localhost:3000', wait_until='networkidle', timeout=15000)
            
            # Wait for app to load
            await page.wait_for_timeout(5000)
            
            print("🔍 Checking page content...")
            
            # Check for specific text content
            content_checks = [
                "Clipboard Intelligence",
                "Intelligence Dashboard", 
                "Chart Type Selector",
                "Data Table",
                "entries",
                "clipboardData.length",
                "API Connection Test"
            ]
            
            for text in content_checks:
                try:
                    element = await page.wait_for_selector(f'text="{text}"', timeout=2000)
                    if element:
                        is_visible = await element.is_visible()
                        print(f"  ✅ Found '{text}' (visible: {is_visible})")
                    else:
                        print(f"  ❌ Not found: '{text}'")
                except:
                    print(f"  ❌ Not found: '{text}'")
            
            # Check for data loading indicators
            print("\n🔍 Checking data loading...")
            
            # Look for entry count displays
            try:
                # Check for any text containing "entries"
                entries_elements = await page.query_selector_all('text=/\\d+.*entries/')
                if entries_elements:
                    for elem in entries_elements:
                        text = await elem.text_content()
                        print(f"  📊 Found entry count: {text}")
                else:
                    print("  ❌ No entry count displays found")
            except Exception as e:
                print(f"  ❌ Error checking entries: {e}")
            
            # Check debug info section
            try:
                debug_section = await page.query_selector('text="Debug Info:"')
                if debug_section:
                    # Get the parent container with debug info
                    debug_container = await debug_section.evaluate_handle('el => el.parentElement')
                    debug_text = await debug_container.text_content()
                    print(f"  🐛 Debug Info Found:\n{debug_text}")
                else:
                    print("  ❌ No debug info section found")
            except Exception as e:
                print(f"  ❌ Error checking debug info: {e}")
            
            # Check network requests
            print("\n🌐 Checking network activity...")
            
            # Monitor API calls
            api_calls = []
            
            def handle_response(response):
                if 'api' in response.url:
                    api_calls.append({
                        'url': response.url,
                        'status': response.status,
                        'size': len(response.headers.get('content-length', '0'))
                    })
                    print(f"  🔗 API Call: {response.url} -> {response.status}")
            
            page.on('response', handle_response)
            
            # Trigger a refresh to see API calls
            await page.reload(wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            print(f"\n📊 Total API calls detected: {len(api_calls)}")
            
            # Check JavaScript console for errors
            print("\n🔍 Checking for JavaScript execution...")
            
            # Execute some JavaScript to check app state
            try:
                app_state = await page.evaluate("""
                    () => {
                        return {
                            hasReact: typeof React !== 'undefined',
                            hasClipboardData: typeof window.clipboardData !== 'undefined',
                            documentReady: document.readyState,
                            elementsCount: document.querySelectorAll('*').length,
                            hasApiCalls: window.fetch !== undefined
                        };
                    }
                """)
                
                print("  🔍 JavaScript State:")
                for key, value in app_state.items():
                    print(f"    {key}: {value}")
                    
            except Exception as e:
                print(f"  ❌ Error checking JavaScript state: {e}")
            
            # Take a screenshot for manual inspection
            screenshot_path = "react_debug_screenshot.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n📸 Debug screenshot saved: {screenshot_path}")
            
            # Keep browser open for manual inspection
            print("\n⏸️  Browser kept open for manual inspection...")
            print("   Press Enter to close and continue...")
            input()
            
        except Exception as e:
            print(f"❌ Error during debugging: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_react_app())
