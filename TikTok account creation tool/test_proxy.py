"""
Quick test to check if the proxy is working
"""
import asyncio
import subprocess
import sys
import socket
from playwright.async_api import async_playwright

async def test_proxy():
    """Test if the proxy can connect to TikTok"""
    proxy_host = "thehub.proxy-cheap.com"
    proxy_port = "8080"
    proxy_user = "fUtPoBT9IuvRIrw"
    proxy_pass = "iTnxB08AjzRVsws"

    # Get a free local port
    def free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    local_port = free_port()
    remote_uri = f"socks5://{proxy_host}:{proxy_port}#{proxy_user}:{proxy_pass}"

    print(f"Starting pproxy relay on port {local_port}...")
    relay_proc = subprocess.Popen(
        [sys.executable, "-m", "pproxy",
         "-l", f"socks5://127.0.0.1:{local_port}",
         "-r", remote_uri],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for relay to start
    await asyncio.sleep(2)

    try:
        print(f"Testing connection via proxy...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                proxy={"server": f"socks5://127.0.0.1:{local_port}"},
            )
            context = await browser.new_context()
            page = await context.new_page()

            try:
                await page.goto("https://www.tiktok.com/signup/phone-or-email/email", timeout=30000)
                print("✅ Proxy works! Page loaded successfully.")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"❌ Proxy failed: {e}")
            finally:
                await browser.close()
    finally:
        relay_proc.terminate()
        relay_proc.wait(timeout=3)
        print("Proxy relay stopped.")

if __name__ == "__main__":
    asyncio.run(test_proxy())
