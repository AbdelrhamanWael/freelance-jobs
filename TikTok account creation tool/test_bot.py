"""
Simple test to verify the bot can navigate to TikTok and interact with the form
"""
import asyncio
import sys
import io
from browser_manager import BrowserManager
from playwright.async_api import Page

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

async def test_navigation():
    """Test basic navigation without proxy"""
    print("Testing navigation to TikTok signup page...")
    
    async with BrowserManager(proxy=None) as bm:
        page = await bm.new_page()
        
        try:
            print("Navigating to TikTok signup...")
            await page.goto(
                "https://www.tiktok.com/signup/phone-or-email/email",
                wait_until="domcontentloaded",
                timeout=30000,
            )
            
            print("SUCCESS: Page loaded successfully!")
            print(f"Page title: {await page.title()}")
            print(f"Page URL: {page.url}")
            
            # Take a screenshot
            await page.screenshot(path="test_navigation.png")
            print("Screenshot saved to test_navigation.png")
            
            # Wait a bit to see the page
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"ERROR: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(test_navigation())
