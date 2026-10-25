"""
browser_manager.py
──────────────────
Manages the Playwright browser lifecycle and applies all stealth measures.

Key stealth techniques:
  1. headless=False + off-screen window position  → avoids headless fingerprinting
  2. --disable-blink-features=AutomationControlled → removes navigator.webdriver flag
  3. playwright-stealth                            → spoofs Navigator, WebGL, Canvas,
                                                     AudioContext, and Hairline features
  4. Randomised User-Agent                        → makes each session look like a
                                                     different real Chrome browser
  5. Isolated browser context                     → fresh cookies/localStorage per session
  6. Overriding page.evaluate hooks               → patches additional JS fingerprints
"""

from __future__ import annotations

import asyncio
import logging
import random
import socket
import subprocess
import sys
from typing import Optional

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)
from playwright_stealth import Stealth

from utils import Proxy, random_viewport

logger = logging.getLogger("TikTokBot.BrowserManager")


def _free_port() -> int:
    """Return an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

# ──────────────────────────────────────────────────────────────────────────────
# Realistic User-Agent pool (Chrome on Windows, updated periodically)
# ──────────────────────────────────────────────────────────────────────────────

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.122 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.112 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.130 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.199 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.88 Safari/537.36",
    # macOS variants for diversity
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.87 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


def pick_user_agent() -> str:
    return random.choice(_USER_AGENTS)


# ──────────────────────────────────────────────────────────────────────────────
# JS patch injected on every new page before any scripts run
# ──────────────────────────────────────────────────────────────────────────────

# This runs via page.add_init_script() so it fires BEFORE the page's own JS.
_STEALTH_INIT_SCRIPT = """
// 1. Remove webdriver property
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
    configurable: true
});

// 2. Fake plugins array (headless Chrome has 0 plugins)
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const arr = [1, 2, 3, 4, 5];   // mimic a real browser with plugins
        arr.__proto__ = PluginArray.prototype;
        return arr;
    },
    configurable: true
});

// 3. Fake languages
Object.defineProperty(navigator, 'languages', {
    get: () => ['en-US', 'en'],
    configurable: true
});

// 4. Override permissions query (headless returns 'denied' for notifications)
const originalQuery = window.navigator.permissions.query.bind(window.navigator.permissions);
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications'
        ? Promise.resolve({ state: Notification.permission })
        : originalQuery(parameters)
);

// 5. Spoof chrome runtime object present in real Chrome
if (!window.chrome) {
    window.chrome = { runtime: {} };
}

// 6. Canvas noise — add tiny random noise to getImageData output
// This defeats Canvas fingerprinting by making each session's canvas hash unique.
(function() {
    const origGetImageData = CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {
        const imageData = origGetImageData.call(this, x, y, w, h);
        for (let i = 0; i < imageData.data.length; i += 4) {
            // Perturb R/G/B channels by ±1 (imperceptible visually)
            imageData.data[i]     = Math.min(255, Math.max(0, imageData.data[i]     + (Math.random() < 0.5 ? 1 : -1)));
            imageData.data[i + 1] = Math.min(255, Math.max(0, imageData.data[i + 1] + (Math.random() < 0.5 ? 1 : -1)));
            imageData.data[i + 2] = Math.min(255, Math.max(0, imageData.data[i + 2] + (Math.random() < 0.5 ? 1 : -1)));
        }
        return imageData;
    };
})();

// 7. WebGL vendor / renderer spoof
(function() {
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';          // UNMASKED_VENDOR_WEBGL
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';  // UNMASKED_RENDERER_WEBGL
        return getParameter.call(this, parameter);
    };
})();
"""


# ──────────────────────────────────────────────────────────────────────────────
# BrowserManager class
# ──────────────────────────────────────────────────────────────────────────────

class BrowserManager:
    """
    Manages a single Playwright Browser + BrowserContext pair for one
    account creation session.

    Usage:
        async with BrowserManager(proxy=proxy) as bm:
            page = await bm.new_page()
            ...
    """

    def __init__(self, proxy: Optional[Proxy] = None) -> None:
        self.proxy      = proxy
        self.user_agent = pick_user_agent()
        self.viewport   = random_viewport()

        self._playwright: Optional[Playwright]     = None
        self._browser:    Optional[Browser]        = None
        self._context:    Optional[BrowserContext] = None
        self._relay_proc: Optional[subprocess.Popen] = None  # local pproxy relay

    # ── Context manager ──────────────────────────────────────────────────────

    async def __aenter__(self) -> "BrowserManager":
        await self._launch()
        return self

    async def __aexit__(self, *_) -> None:
        await self.close()

    # ── Launch ───────────────────────────────────────────────────────────────

    async def _launch(self) -> None:
        """Launch the Chromium browser with all stealth arguments applied."""
        self._playwright = await async_playwright().start()

        # ── SOCKS5 auth relay ────────────────────────────────────────────────
        # Playwright/Chromium doesn't support SOCKS5 with username:password.
        # We spin up a local pproxy relay that handles auth and gives Playwright
        # an unauthenticated socks5://127.0.0.1:PORT to connect through.
        proxy_dict = None
        if self.proxy and self.proxy.username:
            local_port = _free_port()
            remote_uri = (
                f"socks5://{self.proxy.host}:{self.proxy.port}"
                f"#{self.proxy.username}:{self.proxy.password}"
            )
            # Make robust against VSCode 'Play' button using global python
            import os
            venv_python = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
            python_exe = venv_python if os.path.exists(venv_python) else sys.executable

            logger.info(f"Starting SOCKS5 relay on port {local_port}...")
            self._relay_proc = subprocess.Popen(
                [python_exe, "-m", "pproxy",
                 "-l", f"socks5://127.0.0.1:{local_port}",
                 "-r", remote_uri],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            # Wait for relay to start and verify it's running
            await asyncio.sleep(2.0)
            
            # Check if relay process is still running
            if self._relay_proc.poll() is not None:
                # Relay process exited immediately - proxy likely invalid
                stdout, stderr = self._relay_proc.communicate()
                logger.error(f"Proxy relay failed to start. Stderr: {stderr}")
                raise RuntimeError(f"Proxy relay failed - invalid proxy credentials or server down: {self.proxy}")
            
            # Verify relay is listening on the port
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(1.0)
                result = test_sock.connect_ex(("127.0.0.1", local_port))
                test_sock.close()
                if result != 0:
                    logger.error(f"Proxy relay not listening on port {local_port}")
                    raise RuntimeError(f"Proxy relay not listening - check pproxy installation")
            except Exception as e:
                logger.error(f"Failed to verify proxy relay: {e}")
                raise RuntimeError(f"Proxy relay verification failed: {e}")
            
            proxy_dict = {"server": f"socks5://127.0.0.1:{local_port}"}
            logger.info(f"Local SOCKS5 relay verified on port {local_port} → {self.proxy}")
        elif self.proxy:
            # No auth needed — use directly
            proxy_dict = self.proxy.to_playwright_dict()
            logger.info(f"Using proxy directly (no auth): {self.proxy}")

        launch_args = [
            # ── Core anti-detection flags ──────────────────────────────────
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-gpu",                     # Reduces fingerprint surface
            "--disable-accelerated-2d-canvas",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-features=IsolateOrigins,site-per-process",

            # ── Window placed completely off-screen ────────────────────────
            # This is the key trick: the window runs fully (not headless) but
            # is invisible to the user and doesn't consume desktop resources.
            "--window-position=-2000,-2000",
            "--window-size=1280,800",

            # ── Remove Chrome's "controlled by automated software" banner ──
            "--disable-infobars",
            "--excludeSwitches=enable-automation",
            "--useAutomationExtension=false",
        ]

        # Exclude automation-exposing switches that Playwright adds by default
        ignore_default_args = [
            "--enable-automation",
            "--enable-blink-features=IdleDetection",
        ]

        self._browser = await self._playwright.chromium.launch(
            headless=False,                    # NEVER True — see module docstring
            args=launch_args,
            ignore_default_args=ignore_default_args,
            proxy=proxy_dict,
        )

        # Create isolated context: fresh cookies, localStorage, fingerprint
        self._context = await self._browser.new_context(
            user_agent=self.user_agent,
            viewport=self.viewport,
            locale="en-US",
            timezone_id="America/New_York",
            # Mimic a real desktop Chrome browser's accepted types
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
            },
            bypass_csp=False,   # Keep CSP active so we look real
        )

        logger.info(
            f"Browser launched — UA: {self.user_agent[:50]}… | "
            f"Viewport: {self.viewport['width']}x{self.viewport['height']} | "
            f"Proxy: {self.proxy or 'None'}"
        )

    # ── Page factory ─────────────────────────────────────────────────────────

    async def new_page(self) -> Page:
        """
        Open a new page in the current context and apply all stealth patches.
        Returns a fully-hardened Page ready for navigation.
        """
        if self._context is None:
            raise RuntimeError("BrowserManager not initialised — call __aenter__ first.")

        page = await self._context.new_page()

        # Apply playwright-stealth (patches Navigator, WebGL, Canvas, Hairline…)
        await Stealth().apply_stealth_async(page)

        # Inject our custom JS init script (runs before page scripts)
        await page.add_init_script(_STEALTH_INIT_SCRIPT)

        logger.debug("New stealth page created.")
        return page

    # ── Cleanup ──────────────────────────────────────────────────────────────

    async def close(self) -> None:
        """Gracefully close the context, browser, and Playwright instance."""
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception as exc:
            logger.warning(f"Error during browser close: {exc}")
        finally:
            # Shut down the local SOCKS5 relay if we started one
            if self._relay_proc:
                try:
                    self._relay_proc.terminate()
                    self._relay_proc.wait(timeout=3)
                except Exception:
                    pass
                self._relay_proc = None
            self._context   = None
            self._browser   = None
            self._playwright = None
            logger.debug("Browser closed.")
