"""
captcha_solver.py
─────────────────
Handles all captcha interactions with the SadCaptcha API.

Supports:
  - Rotate captcha  (image-rotation puzzles)
  - Puzzle captcha  (jigsaw/slider puzzles — most common on TikTok)

The solver:
  1. Screenshots the captcha elements from the live page.
  2. Sends base64-encoded images to SadCaptcha.
  3. Receives solution coordinates / slide distance.
  4. Performs a realistic Bezier-curve drag on the page.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
from typing import Optional

import aiohttp
from playwright.async_api import Page, ElementHandle

import config
from utils import bezier_mouse_drag, human_delay

logger = logging.getLogger("TikTokBot.CaptchaSolver")


# ──────────────────────────────────────────────────────────────────────────────
# Helper: encode an image file/bytes to base64 string
# ──────────────────────────────────────────────────────────────────────────────

def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


# ──────────────────────────────────────────────────────────────────────────────
# SadCaptcha API Client
# ──────────────────────────────────────────────────────────────────────────────

class CaptchaSolver:
    """
    Interfaces with the SadCaptcha API to solve TikTok captchas.

    Usage:
        solver = CaptchaSolver()
        solved = await solver.solve(page)
    """

    # CSS selectors for common TikTok captcha elements
    # These may need updating as TikTok's UI changes.
    CAPTCHA_CONTAINER_SEL  = "[class*='captcha_verify_container']"
    PUZZLE_PIECE_SEL       = "[class*='captcha_verify_img_slide']"
    PUZZLE_BG_SEL          = "[class*='captcha_verify_img_slide'] img"
    PUZZLE_SLIDER_SEL      = "[class*='secsdk-captcha-drag-icon']"
    PUZZLE_TRACK_SEL       = "[class*='captcha_verify_slide--slidebar']"
    ROTATE_INNER_SEL       = "[class*='captcha-verify-image--r-image']"
    ROTATE_OUTER_SEL       = "[class*='captcha-verify-image--c-image']"

    def __init__(self) -> None:
        self.api_key  = config.SADCAPTCHA_API_KEY
        self.base_url = config.SADCAPTCHA_BASE_URL
        self._session: Optional[aiohttp.ClientSession] = None

    # ── Session lifecycle ────────────────────────────────────────────────────

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # ── Screenshot helpers ───────────────────────────────────────────────────

    async def _screenshot_element(self, element: ElementHandle) -> bytes:
        """Return a PNG screenshot of a single page element."""
        return await element.screenshot(type="png")

    async def _screenshot_region(self, page: Page, clip: dict) -> bytes:
        """
        Screenshot a specific x/y/width/height region of the page.
        clip = {'x': int, 'y': int, 'width': int, 'height': int}
        """
        return await page.screenshot(clip=clip, type="png")

    # ── SadCaptcha API calls ─────────────────────────────────────────────────

    async def _post(self, endpoint: str, payload: dict) -> dict:
        """POST JSON to a SadCaptcha endpoint and return the parsed response."""
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}"
        params = {"licenseKey": self.api_key}

        async with session.post(url, params=params, json=payload, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"SadCaptcha API error {resp.status}: {text}")
            return await resp.json()

    async def _solve_puzzle(self, puzzle_b64: str, piece_b64: str) -> dict:
        """
        Send puzzle (background) + piece (sliding piece) images to SadCaptcha.
        Returns: {"slideXProportion": float}  — fraction of track width to slide.
        """
        return await self._post(
            "puzzle",
            {"puzzleImageB64": puzzle_b64, "pieceImageB64": piece_b64},
        )

    async def _solve_rotate(self, outer_b64: str, inner_b64: str) -> dict:
        """
        Send outer ring + inner image to SadCaptcha for rotation solution.
        Returns: {"angle": float}
        """
        return await self._post(
            "rotate",
            {"outerImageB64": outer_b64, "innerImageB64": inner_b64},
        )

    # ── Detection ────────────────────────────────────────────────────────────

    async def _detect_captcha_type(self, page: Page) -> Optional[str]:
        """
        Return 'puzzle', 'rotate', or None if no captcha is visible.
        Tries up to 5 seconds before giving up.
        """
        for _ in range(10):
            container = await page.query_selector(self.CAPTCHA_CONTAINER_SEL)
            if container:
                # Determine type by looking for type-specific sub-elements
                if await page.query_selector(self.PUZZLE_SLIDER_SEL):
                    return "puzzle"
                if await page.query_selector(self.ROTATE_INNER_SEL):
                    return "rotate"
                return "unknown"
            await asyncio.sleep(0.5)
        return None

    # ── Puzzle Solver ────────────────────────────────────────────────────────

    async def _handle_puzzle(self, page: Page) -> bool:
        """
        Solve a TikTok jigsaw / slider captcha.
        Returns True on likely success, False on failure.
        """
        logger.info("Solving PUZZLE captcha...")

        # Get puzzle elements
        bg_el    = await page.wait_for_selector(self.PUZZLE_BG_SEL,    timeout=10_000)
        piece_el = await page.wait_for_selector(self.PUZZLE_PIECE_SEL, timeout=10_000)

        if not bg_el or not piece_el:
            logger.error("Could not locate puzzle captcha elements.")
            return False

        # Screenshot both images
        puzzle_bytes = await self._screenshot_element(bg_el)
        piece_bytes  = await self._screenshot_element(piece_el)

        # Call SadCaptcha
        result = await self._solve_puzzle(_b64(puzzle_bytes), _b64(piece_bytes))
        slide_proportion: float = result.get("slideXProportion", 0.5)
        logger.debug(f"Puzzle slide proportion: {slide_proportion:.4f}")

        # Locate the slider button and the track bar
        slider_el = await page.wait_for_selector(self.PUZZLE_SLIDER_SEL, timeout=5_000)
        track_el  = await page.wait_for_selector(self.PUZZLE_TRACK_SEL,  timeout=5_000)

        if not slider_el or not track_el:
            logger.error("Could not locate slider or track element.")
            return False

        slider_box = await slider_el.bounding_box()
        track_box  = await track_el.bounding_box()

        if not slider_box or not track_box:
            logger.error("Bounding box retrieval failed.")
            return False

        # Compute drag coordinates
        start_x = slider_box["x"] + slider_box["width"] / 2
        start_y = slider_box["y"] + slider_box["height"] / 2
        end_x   = track_box["x"] + track_box["width"] * slide_proportion
        end_y   = start_y + random.uniform(-2, 2)  # tiny vertical jitter

        # Execute the Bezier drag
        await bezier_mouse_drag(page, start_x, start_y, end_x, end_y)
        await human_delay(1.0, 2.5)

        logger.info("Puzzle captcha drag completed.")
        return True

    # ── Rotate Solver ────────────────────────────────────────────────────────

    async def _handle_rotate(self, page: Page) -> bool:
        """
        Solve a TikTok rotation captcha.
        Returns True on likely success, False on failure.
        """
        logger.info("Solving ROTATE captcha...")

        outer_el = await page.wait_for_selector(self.ROTATE_OUTER_SEL, timeout=10_000)
        inner_el = await page.wait_for_selector(self.ROTATE_INNER_SEL, timeout=10_000)

        if not outer_el or not inner_el:
            logger.error("Could not locate rotate captcha elements.")
            return False

        outer_bytes = await self._screenshot_element(outer_el)
        inner_bytes = await self._screenshot_element(inner_el)

        result = await self._solve_rotate(_b64(outer_bytes), _b64(inner_bytes))
        angle: float = result.get("angle", 0.0)
        logger.debug(f"Rotate captcha angle: {angle:.2f}")

        # The rotation slider goes 0-360 degrees mapped across the slider track
        slider_el = await page.wait_for_selector(self.PUZZLE_SLIDER_SEL, timeout=5_000)
        track_el  = await page.wait_for_selector(self.PUZZLE_TRACK_SEL,  timeout=5_000)

        if not slider_el or not track_el:
            logger.error("Could not locate rotation slider/track.")
            return False

        slider_box = await slider_el.bounding_box()
        track_box  = await track_el.bounding_box()

        if not slider_box or not track_box:
            return False

        proportion = angle / 360.0
        start_x = slider_box["x"] + slider_box["width"] / 2
        start_y = slider_box["y"] + slider_box["height"] / 2
        end_x   = track_box["x"] + track_box["width"] * proportion
        end_y   = start_y

        await bezier_mouse_drag(page, start_x, start_y, end_x, end_y)
        await human_delay(1.0, 2.5)

        logger.info("Rotate captcha drag completed.")
        return True

    # ── Public entry point ───────────────────────────────────────────────────

    async def solve(self, page: Page, max_retries: int = 3) -> bool:
        """
        Detect and solve a TikTok captcha on the given page.

        Args:
            page:        The active Playwright page.
            max_retries: How many times to retry if the solution fails.

        Returns:
            True if captcha was solved (or was not present).
            False if all retries are exhausted.
        """
        captcha_type = await self._detect_captcha_type(page)

        if captcha_type is None:
            logger.debug("No captcha detected on page.")
            return True  # Nothing to solve

        if captcha_type == "unknown":
            logger.warning("Unknown captcha type — skipping solve attempt.")
            return False

        for attempt in range(1, max_retries + 1):
            logger.info(f"Captcha solve attempt {attempt}/{max_retries} — type: {captcha_type}")
            try:
                if captcha_type == "puzzle":
                    success = await self._handle_puzzle(page)
                elif captcha_type == "rotate":
                    success = await self._handle_rotate(page)
                else:
                    return False

                if success:
                    # Wait briefly and check if captcha container disappeared
                    await asyncio.sleep(2)
                    still_present = await page.query_selector(self.CAPTCHA_CONTAINER_SEL)
                    if not still_present:
                        logger.info("Captcha solved successfully!")
                        return True
                    logger.warning(f"Captcha still present after attempt {attempt}.")

            except Exception as exc:
                logger.error(f"Captcha solve attempt {attempt} raised: {exc}")

            await human_delay(2.0, 4.0)

        logger.error("All captcha solve attempts exhausted.")
        return False


# Fix missing import inside class method
import random
