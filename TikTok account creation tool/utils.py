"""
utils.py
────────
Shared utility helpers:
  - Logging setup
  - Human-like mouse + keyboard helpers (Playwright)
  - Proxy file loader
  - Random data generators (DOB, passwords, usernames)
  - Bezier curve mouse movement
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import random
import re
import string
import time
from pathlib import Path
from typing import Optional

from faker import Faker
from playwright.async_api import Page

import config

# ──────────────────────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────────────────────

def setup_logging() -> logging.Logger:
    """Configure file + console logging with timestamp and level."""
    logger = logging.getLogger("TikTokBot")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s :: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler (full debug)
    fh = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    # Console handler (info+)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


logger = setup_logging()


# ──────────────────────────────────────────────────────────────────────────────
# Proxy Helpers
# ──────────────────────────────────────────────────────────────────────────────

class Proxy:
    """Represents a single proxy entry parsed from proxies.txt."""

    def __init__(self, host: str, port: str, username: str = "", password: str = ""):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    @classmethod
    def from_line(cls, line: str) -> "Proxy":
        """
        Parse a proxy line. Supported formats:
          IP:Port
          IP:Port:User:Pass
        """
        parts = line.strip().split(":")
        if len(parts) == 2:
            return cls(parts[0], parts[1])
        elif len(parts) == 4:
            return cls(parts[0], parts[1], parts[2], parts[3])
        else:
            raise ValueError(f"Invalid proxy format: {line!r}")

    def to_playwright_dict(self) -> dict:
        """Return the dict expected by Playwright's proxy option."""
        d: dict = {"server": f"socks5://{self.host}:{self.port}"}
        if self.username:
            d["username"] = self.username
        if self.password:
            d["password"] = self.password
        return d

    def __str__(self) -> str:
        return f"{self.host}:{self.port}"


def load_proxies(filepath: str = config.PROXIES_FILE) -> list[Proxy]:
    """Load and parse all proxies from the text file. Returns list (may be empty)."""
    path = Path(filepath)
    if not path.exists():
        logger.warning(f"Proxy file not found: {filepath!r}. Running without proxies.")
        return []

    proxies: list[Proxy] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                proxies.append(Proxy.from_line(line))
            except ValueError as exc:
                logger.warning(f"Skipping bad proxy line — {exc}")

    logger.info(f"Loaded {len(proxies)} proxies from {filepath!r}")
    return proxies


async def validate_proxy(proxy: Proxy, timeout: int = 10) -> bool:
    """
    Test if a proxy can connect to TikTok by attempting a simple HTTP request.
    Returns True if proxy works, False otherwise.
    """
    import aiohttp
    
    try:
        proxy_url = f"http://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}" if proxy.username else f"http://{proxy.host}:{proxy.port}"
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(
                "https://www.tiktok.com",
                proxy=proxy_url,
                ssl=False,
                allow_redirects=True
            ) as response:
                if response.status < 500:
                    logger.info(f"Proxy validation passed: {proxy}")
                    return True
                else:
                    logger.warning(f"Proxy returned status {response.status}: {proxy}")
                    return False
    except Exception as e:
        logger.warning(f"Proxy validation failed for {proxy}: {e}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Data Generators
# ──────────────────────────────────────────────────────────────────────────────

_fake = Faker("en_US")


def random_dob_over_18() -> dict[str, str]:
    """
    Return a random date-of-birth for someone aged 18-45.
    Returns dict with keys: 'year', 'month', 'day' (all strings).
    """
    current_year = time.localtime().tm_year
    year  = random.randint(current_year - 45, current_year - 18)
    month = random.randint(1, 12)
    # Simple day range — avoids 31-day / leap-year edge cases
    day   = random.randint(1, 28)
    return {"year": str(year), "month": str(month).zfill(2), "day": str(day).zfill(2)}


def random_password() -> str:
    """
    Generate a secure random password that satisfies most platform policies:
      - At least one uppercase, lowercase, digit, special char
      - Length between PASSWORD_MIN_LENGTH and PASSWORD_MAX_LENGTH
    """
    length = random.randint(config.PASSWORD_MIN_LENGTH, config.PASSWORD_MAX_LENGTH)
    chars = (
        random.choice(string.ascii_uppercase)
        + random.choice(string.ascii_lowercase)
        + random.choice(string.digits)
        + random.choice("!@#$%^&*()-_=+")
        + "".join(
            random.choices(
                string.ascii_letters + string.digits + "!@#$%^&*()-_=+",
                k=length - 4,
            )
        )
    )
    return "".join(random.sample(chars, len(chars)))  # shuffle


def random_username() -> str:
    """Generate a plausible TikTok username (letters, digits, underscores, max 24 chars)."""
    base = _fake.user_name().replace("-", "_").replace(".", "_")
    suffix = random.randint(100, 9999)
    username = f"{base}{suffix}"[:24]
    # Ensure it's alphanumeric + underscore only
    username = re.sub(r"[^a-zA-Z0-9_]", "", username)
    return username or f"user_{suffix}"


def random_bio() -> str:
    """Return a short, plausible TikTok bio sentence."""
    templates = [
        "Living my best life ✨",
        "Just here for the vibes 🎵",
        "Creator | Dreamer | Explorer 🌍",
        f"Based in {_fake.city()} 📍",
        "Coffee addict & content lover ☕",
        "Making memories one video at a time 🎬",
        f"Lover of {_fake.word()} and {_fake.word()} 🔥",
    ]
    return random.choice(templates)


def random_viewport() -> dict[str, int]:
    """Return a slightly randomised viewport dict."""
    w = 1280 + random.randint(-config.VIEWPORT_JITTER_W, config.VIEWPORT_JITTER_W)
    h = 800  + random.randint(-config.VIEWPORT_JITTER_H, config.VIEWPORT_JITTER_H)
    # Clamp to sensible bounds
    return {"width": max(1024, w), "height": max(600, h)}


# ──────────────────────────────────────────────────────────────────────────────
# Human-like Interaction Helpers (Playwright async)
# ──────────────────────────────────────────────────────────────────────────────

async def human_delay(low: float = 0.5, high: float = 1.5) -> None:
    """Await a random sleep to simulate human reaction time."""
    await asyncio.sleep(random.uniform(low, high))


async def human_type(page: Page, selector: str, text: str) -> None:
    """
    Type text into a field character-by-character with randomised
    inter-keystroke delays to mimic real human typing speed.
    """
    await page.click(selector)
    await human_delay(*config.DELAY_AFTER_CLICK)
    for char in text:
        await page.type(selector, char, delay=random.uniform(
            *config.DELAY_BETWEEN_KEYSTROKES
        ) * 1000)  # Playwright expects ms
    await human_delay(0.2, 0.6)


async def human_click(page: Page, selector: str) -> None:
    """Click an element with a brief pre/post delay."""
    await human_delay(*config.DELAY_AFTER_CLICK)
    await page.click(selector)
    await human_delay(0.3, 0.8)


# ──────────────────────────────────────────────────────────────────────────────
# Bezier-Curve Mouse Movement (anti-bot slider simulation)
# ──────────────────────────────────────────────────────────────────────────────

def _bezier_point(
    t: float,
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
) -> tuple[float, float]:
    """Calculate a point on a cubic Bezier curve at parameter t ∈ [0, 1]."""
    x = (
        (1 - t) ** 3 * p0[0]
        + 3 * (1 - t) ** 2 * t * p1[0]
        + 3 * (1 - t) * t ** 2 * p2[0]
        + t ** 3 * p3[0]
    )
    y = (
        (1 - t) ** 3 * p0[1]
        + 3 * (1 - t) ** 2 * t * p1[1]
        + 3 * (1 - t) * t ** 2 * p2[1]
        + t ** 3 * p3[1]
    )
    return x, y


async def bezier_mouse_drag(
    page: Page,
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    steps: int = 60,
) -> None:
    """
    Perform a realistic Bezier-curve mouse drag from (start_x, start_y)
    to (end_x, end_y).  Control points are randomly jittered to make each
    drag path unique and unpredictable to ML-based bot detectors.
    """
    # Random control points with slight jitter around the straight path
    cp1 = (
        start_x + (end_x - start_x) * 0.3 + random.uniform(-15, 15),
        start_y + random.uniform(-20, 20),
    )
    cp2 = (
        start_x + (end_x - start_x) * 0.7 + random.uniform(-15, 15),
        end_y + random.uniform(-20, 20),
    )

    # Press at start
    await page.mouse.move(start_x, start_y)
    await asyncio.sleep(random.uniform(0.1, 0.3))
    await page.mouse.down()
    await asyncio.sleep(random.uniform(0.05, 0.15))

    # Traverse the curve
    for i in range(1, steps + 1):
        t = i / steps
        x, y = _bezier_point(t, (start_x, start_y), cp1, cp2, (end_x, end_y))
        # Add tiny random jitter per step
        x += random.uniform(-1.5, 1.5)
        y += random.uniform(-0.8, 0.8)
        await page.mouse.move(x, y)
        # Slightly slower near the end (deceleration)
        delay_ms = random.uniform(8, 18) * (1 + 0.5 * math.sin(math.pi * t))
        await asyncio.sleep(delay_ms / 1000)

    await asyncio.sleep(random.uniform(0.05, 0.2))
    await page.mouse.up()
    await asyncio.sleep(random.uniform(0.3, 0.7))


# ──────────────────────────────────────────────────────────────────────────────
# Session Export Helper
# ──────────────────────────────────────────────────────────────────────────────

async def export_session(
    page: Page,
    email: str,
    password: str,
    username: str,
    user_agent: str,
    proxy: Optional[Proxy],
) -> Path:
    """
    Export Playwright cookies + metadata to a JSON file under ACCOUNTS_DIR.
    Returns the path of the written file.
    """
    accounts_dir = Path(config.ACCOUNTS_DIR)
    accounts_dir.mkdir(exist_ok=True)

    cookies = await page.context.cookies()
    safe_username = re.sub(r"[^\w]", "_", username)
    filepath = accounts_dir / f"account_{safe_username}.json"

    session_data = {
        "email":      email,
        "password":   password,
        "username":   username,
        "user_agent": user_agent,
        "proxy":      str(proxy) if proxy else None,
        "cookies":    cookies,
        "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

    logger.info(f"Session exported → {filepath}")
    return filepath
