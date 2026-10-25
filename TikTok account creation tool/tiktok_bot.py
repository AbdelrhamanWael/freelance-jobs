"""
tiktok_bot.py
─────────────
The core TikTok registration orchestrator.

Encapsulates the full end-to-end workflow:
  1. Launch a stealth browser via BrowserManager
  2. Navigate to TikTok email signup
  3. Fill DOB, email, and password with human-like timing
  4. Solve any captcha via CaptchaSolver
  5. Retrieve OTP from the temp inbox via EmailManager
  6. Enter OTP and complete registration
  7. Export session (cookies + metadata) to a JSON file

Designed to be called once per account.  The main.py orchestrator
runs multiple instances sequentially with different proxies.
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

import config
from browser_manager import BrowserManager
from captcha_solver import CaptchaSolver
from email_manager import BaseEmailManager
from utils import (
    Proxy,
    export_session,
    human_click,
    human_delay,
    human_type,
    random_bio,
    random_dob_over_18,
    random_password,
    random_username,
)

logger = logging.getLogger("TikTokBot.Core")


# ──────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class RegistrationResult:
    success:    bool
    email:      str = ""
    username:   str = ""
    password:   str = ""
    session_file: Optional[str] = None
    error:      str = ""


# ──────────────────────────────────────────────────────────────────────────────
# CSS Selectors — update if TikTok changes their DOM
# ──────────────────────────────────────────────────────────────────────────────

class Selectors:
    # ── DOB — TikTok uses custom div comboboxes (NOT native <select>) ──────────
    # All 3 appear in DOM order: Month, Day, Year
    DOB_COMBOBOX = "[data-e2e='select-container']"
    # Listbox panels that open on click (keyed by their id pattern)
    DOB_MONTH_LIST = "[id*='Month-options-list']"
    DOB_DAY_LIST   = "[id*='Day-options-list']"
    DOB_YEAR_LIST  = "[id*='Year-options-list']"
    # Options inside a listbox
    DOB_OPTION     = "[role='option'], li"

    # ── Email + Password ────────────────────────────────────────────────────────
    EMAIL_INPUT    = "input[name='email'], input[placeholder='Email address']"
    PASSWORD_INPUT = "input[type='password'], input[placeholder='Password']"
    SEND_CODE_BTN  = "[data-e2e='send-code-button'], button:has-text('Send code')"

    # ── OTP / verification code ─────────────────────────────────────────────────
    OTP_INPUTS = "input[maxlength='1'], [class*='verify-code'] input"
    OTP_SINGLE = "input[placeholder='Enter 6-digit code'], input[placeholder*='code'], input[name='code']"

    # ── Submit ──────────────────────────────────────────────────────────────────
    # TikTok currently uses a single submit button labelled "Next"
    SUBMIT_BTN = "button[type='submit'], button:has-text('Sign Up'), button:has-text('Next'), button:has-text('Create')"
    NEXT_BTN   = "button:has-text('Next'), [data-e2e='next-button']"

    # ── Logged-in detection ─────────────────────────────────────────────────────
    LOGGED_IN_INDICATOR = "[data-e2e='nav-upload'], [class*='DivHeaderIconWrapper']"

    # ── Username (profile setup step — may appear post-registration) ────────────
    USERNAME_INPUT = "input[placeholder*='Username'], input[name='nickname']"
    USERNAME_NEXT  = "button:has-text('Next'), button:has-text('Continue')"

    # ── Error messages ──────────────────────────────────────────────────────────
    ERROR_MSG = "[class*='error'], [class*='Error'], [data-e2e='register-error']"


# ──────────────────────────────────────────────────────────────────────────────
# TikTokBot
# ──────────────────────────────────────────────────────────────────────────────

class TikTokBot:
    """
    Orchestrates a single TikTok account registration attempt.

    Args:
        proxy:         Optional Proxy instance for this session.
        email_manager: Initialised BaseEmailManager instance.
        captcha_solver: Initialised CaptchaSolver instance.
    """

    def __init__(
        self,
        proxy: Optional[Proxy],
        email_manager: BaseEmailManager,
        captcha_solver: CaptchaSolver,
    ) -> None:
        self.proxy          = proxy
        self.email_mgr      = email_manager
        self.captcha_solver = captcha_solver

    # ── Public entry ─────────────────────────────────────────────────────────

    async def run(self) -> RegistrationResult:
        """
        Execute the full registration flow.
        Returns a RegistrationResult with all session details.
        """
        email, token   = await self.email_mgr.create_inbox()
        async with BrowserManager(proxy=self.proxy) as bm:
            page = await bm.new_page()
            password       = random_password()
            username       = random_username()
            dob            = random_dob_over_18()

            result = RegistrationResult(
                success=False,
                email=email,
                username=username,
                password=password,
            )

            api_errors = []
            async def _track_response(resp):
                if any(x in resp.url for x in ("send_code", "passport/web", "registration")):
                    try:
                        ct = resp.headers.get("content-type", "")
                        if "json" in ct:
                            data = await resp.json()
                            logger.info(f"TikTok API [{resp.status}] {resp.url.split('?')[0]}: {data}")
                            msg = data.get("message")
                            if msg and msg != "success":
                                desc = data.get("data", {}).get("description") or msg
                                api_errors.append(desc)
                    except Exception:
                        pass
            page.on("response", _track_response)

            try:
                # ── Step 1: Navigate to signup page ──────────────────────
                # Use wait_until="commit" (fires on first HTTP byte) because
                # rotating residential proxies can be slow to fully load the
                # page, causing "domcontentloaded" to time out.
                # We then wait manually for the DOB combobox to confirm load.
                logger.info(f"Navigating to TikTok signup → {config.TIKTOK_SIGNUP_URL}")
                await page.goto(
                    config.TIKTOK_SIGNUP_URL,
                    wait_until="domcontentloaded",
                    timeout=60_000,
                )
                # Wait for the page to actually render (DOB combobox appears)
                try:
                    await page.wait_for_selector(
                        Selectors.DOB_COMBOBOX, timeout=30_000
                    )
                except PlaywrightTimeout:
                    logger.warning("DOB combobox did not appear after navigation — continuing anyway.")
                await human_delay(*config.DELAY_PAGE_LOAD)

                # ── Step 2: Fill date of birth ────────────────────────────
                await self._fill_dob(page, dob)

                # ── Step 3: Fill email ────────────────────────────────────
                await self._fill_email(page, email)

                # ── Step 4: Fill password ─────────────────────────────────
                await self._fill_password(page, password)

                # ── Step 5: Request OTP code ──────────────────────────────
                await self._click_send_code(page)
                await asyncio.sleep(2)

                # Check if TikTok returned an immediate API error
                if api_errors:
                    result.error = f"TikTok API rejected: {api_errors[-1]}"
                    logger.error(result.error)
                    return result

                # Check if an on-screen error banner appeared
                form_err = await self._get_error_text(page)
                if form_err:
                    result.error = f"TikTok form error: {form_err}"
                    logger.error(result.error)
                    return result

                # ── Step 6: Solve captcha (may appear at any point) ───────
                solved = await self.captcha_solver.solve(page)
                if not solved:
                    result.error = "Captcha solve failed"
                    logger.error(result.error)
                    return result

                # ── Step 7: Retrieve and enter OTP ────────────────────────
                logger.info("Taking debug screenshot before waiting for OTP...")
                await page.screenshot(path="debug_otp.png")
                otp = await self.email_mgr.wait_for_otp(email, token)
                if not otp:
                    result.error = "OTP retrieval timed out"
                    logger.error(result.error)
                    return result

                await self._enter_otp(page, otp)

                # ── Step 8: Complete signup ───────────────────────────────
                await self._submit_form(page)
                await human_delay(*config.DELAY_PAGE_LOAD)

                # ── Step 9: Handle optional username setup screen ─────────
                await self._maybe_set_username(page, username)

                # ── Step 10: Verify we are actually logged in ─────────────
                logged_in = await self._verify_logged_in(page)
                if not logged_in:
                    # Check for error messages
                    error_text = await self._get_error_text(page)
                    result.error = error_text or "Login verification failed after signup"
                    logger.error(result.error)
                    return result

                # ── Step 11: Export session ───────────────────────────────
                session_path = await export_session(
                    page=page,
                    email=email,
                    password=password,
                    username=username,
                    user_agent=bm.user_agent,
                    proxy=self.proxy,
                )
                result.success      = True
                result.session_file = str(session_path)
                logger.info(f"Account created successfully: {email}")

            except PlaywrightTimeout as exc:
                result.error = f"Playwright timeout: {exc}"
                logger.error(result.error)
            except Exception as exc:
                result.error = f"Unexpected error: {exc}"
                logger.exception(result.error)

            return result

    # ── Private step methods ─────────────────────────────────────────────────

    async def _fill_dob(self, page: Page, dob: dict) -> None:
        """
        Fill Date of Birth using TikTok's custom div comboboxes.
        TikTok no longer uses native <select> — it uses clickable div dropdowns
        with separate listbox panels (Month / Day / Year).
        All three DOB fields and the main form are on the same page — no extra
        'Next' click is needed after filling DOB.
        """
        logger.debug(f"Filling DOB: {dob}")
        try:
            await page.wait_for_selector(Selectors.DOB_COMBOBOX, timeout=10_000)
            comboboxes = await page.query_selector_all(Selectors.DOB_COMBOBOX)
            if len(comboboxes) < 3:
                logger.warning(f"Expected 3 DOB comboboxes, found {len(comboboxes)} — skipping.")
                return

            month_idx = int(dob["month"]) - 1   # 0-based index into Month list
            day_idx   = int(dob["day"])   - 1   # 0-based index into Day list

            # Month
            await self._click_dob_combobox(page, comboboxes[0], Selectors.DOB_MONTH_LIST, index=month_idx)
            # Day
            await self._click_dob_combobox(page, comboboxes[1], Selectors.DOB_DAY_LIST,   index=day_idx)
            # Year (match by text since ordering may vary)
            await self._click_dob_year(page, comboboxes[2], Selectors.DOB_YEAR_LIST, year=dob["year"])

            await human_delay(0.4, 0.9)

        except PlaywrightTimeout:
            logger.warning("DOB comboboxes not found — skipping.")

    async def _click_dob_combobox(self, page: Page, combobox, listbox_sel: str, index: int) -> None:
        """Click a DOB combobox then pick the option at position `index`."""
        await combobox.click()
        await asyncio.sleep(0.5)
        listbox = await page.wait_for_selector(listbox_sel, timeout=5_000)
        options = await listbox.query_selector_all(Selectors.DOB_OPTION)
        target  = min(index, len(options) - 1)
        await options[target].click()
        await human_delay(0.2, 0.5)

    async def _click_dob_year(self, page: Page, combobox, listbox_sel: str, year: str) -> None:
        """Click the year combobox and pick the option whose text matches `year`."""
        await combobox.click()
        await asyncio.sleep(0.5)
        listbox = await page.wait_for_selector(listbox_sel, timeout=5_000)
        options = await listbox.query_selector_all(Selectors.DOB_OPTION)
        for option in options:
            text = (await option.text_content() or "").strip()
            if text == year:
                await option.click()
                await human_delay(0.2, 0.5)
                return
        # Fallback: click last option (oldest year in list)
        if options:
            await options[-1].click()
        await human_delay(0.2, 0.5)

    async def _react_fill(self, page: Page, selector: str, value: str) -> None:
        """
        Fill an input in a way that properly triggers React's synthetic event system.

        TikTok uses React which tracks input state internally. A plain Playwright
        page.type() or page.fill() writes the DOM value but does NOT fire the
        React onChange handler, so React's internal state stays empty and the form
        validation logic thinks the field is blank — keeping "Send code" disabled.

        Fix: Use the native input value setter (bypasses React's value override),
        then dispatch both 'input' and 'change' events which React listens to.
        """
        await page.wait_for_selector(selector, timeout=15_000)
        # Click first to focus the element
        await page.click(selector)
        await human_delay(0.3, 0.7)

        # Use JS to set value via native setter and fire React events
        await page.evaluate(
            """
            ([sel, val]) => {
                const el = document.querySelector(sel);
                if (!el) return;
                // Clear existing value
                el.focus();
                // Use native setter to bypass React's value tracking
                const nativeSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                nativeSetter.call(el, val);
                // Dispatch events React listens to
                el.dispatchEvent(new Event('input',  { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
            """,
            [selector, value],
        )
        await human_delay(0.2, 0.5)
        # Tab away to trigger onBlur validation
        await page.keyboard.press("Tab")
        await human_delay(0.3, 0.6)

    async def _fill_email(self, page: Page, email: str) -> None:
        """Fill the email field and trigger React onChange + onBlur validation."""
        logger.debug(f"Entering email: {email}")
        await self._react_fill(page, Selectors.EMAIL_INPUT, email)

    async def _fill_password(self, page: Page, password: str) -> None:
        """Fill the password field and trigger React onChange + onBlur validation."""
        logger.debug("Entering password…")
        await self._react_fill(page, Selectors.PASSWORD_INPUT, password)

    async def _click_send_code(self, page: Page) -> None:
        """
        Click the 'Send code' button to trigger OTP email dispatch.

        We wait for the button to become enabled (not disabled) before clicking.
        TikTok enables the button only after React validates both email + password.
        """
        logger.debug("Waiting for 'Send code' button to become enabled…")
        try:
            # Wait for button to exist
            btn = await page.wait_for_selector(Selectors.SEND_CODE_BTN, timeout=10_000)
            if not btn:
                logger.warning("'Send code' button not found — may have auto-progressed.")
                return

            # Wait up to 8s for the button to become enabled (not disabled)
            for _ in range(16):  # 16 x 0.5s = 8s max
                is_disabled = await btn.get_attribute("disabled")
                aria_disabled = await btn.get_attribute("aria-disabled")
                if is_disabled is None and aria_disabled != "true":
                    break
                logger.debug("'Send code' button still disabled — waiting for form validation…")
                await asyncio.sleep(0.5)

            await btn.scroll_into_view_if_needed()
            await human_delay(0.5, 1.0)

            # Try standard click first
            await btn.click()
            await asyncio.sleep(1.0)

            # Verify OTP countdown started (button text changes to "Resend in Xs")
            btn_text = (await btn.text_content() or "").strip().lower()
            logger.debug(f"'Send code' button text after click: {btn_text!r}")

            if "send code" in btn_text:
                # Click did not trigger — try JS dispatch
                logger.warning("Button click had no effect — retrying with JS dispatch_event…")
                await page.evaluate(
                    "(sel) => { const el = document.querySelector(sel); if (el) el.click(); }",
                    Selectors.SEND_CODE_BTN.split(",")[0].strip(),
                )
                await asyncio.sleep(1.5)

            await human_delay(0.5, 1.2)
        except PlaywrightTimeout:
            logger.warning("'Send code' button not found — may have auto-progressed.")

    async def _enter_otp(self, page: Page, otp: str) -> None:
        """
        Enter the 6-digit OTP.  Handles two common TikTok OTP UI patterns:
          A) Six individual single-character inputs
          B) A single 6-character input field
        """
        logger.debug(f"Entering OTP: {otp}")
        await human_delay(1.0, 2.0)

        # Pattern A: individual character boxes
        individual_inputs = await page.query_selector_all(Selectors.OTP_INPUTS)
        if len(individual_inputs) == 6:
            for i, char in enumerate(otp):
                await individual_inputs[i].click()
                await asyncio.sleep(0.1)
                await individual_inputs[i].type(char, delay=120)
                await human_delay(0.1, 0.3)
            return

        # Pattern B: single code input
        try:
            await page.wait_for_selector(Selectors.OTP_SINGLE, timeout=5_000)
            await human_type(page, Selectors.OTP_SINGLE, otp)
        except PlaywrightTimeout:
            logger.error("Could not locate OTP input field.")
            raise

    async def _submit_form(self, page: Page) -> None:
        """Click the final Sign Up / submit button."""
        logger.debug("Submitting registration form…")
        try:
            # Prefer explicit submit button
            await page.wait_for_selector(Selectors.SUBMIT_BTN, timeout=8_000)
            await human_click(page, Selectors.SUBMIT_BTN)
        except PlaywrightTimeout:
            # Fallback: press Enter
            await page.keyboard.press("Enter")
        await human_delay(*config.DELAY_PAGE_LOAD)

    async def _maybe_set_username(self, page: Page, username: str) -> None:
        """
        Some TikTok registration flows show a username-setup screen.
        If it appears, fill it; otherwise, skip gracefully.
        """
        try:
            username_input = await page.wait_for_selector(
                Selectors.USERNAME_INPUT, timeout=5_000
            )
            if username_input:
                logger.debug(f"Username setup screen detected — entering: {username}")
                await page.fill(Selectors.USERNAME_INPUT, "")   # clear default
                await human_type(page, Selectors.USERNAME_INPUT, username)
                await human_delay(0.5, 1.0)
                try:
                    await human_click(page, Selectors.USERNAME_NEXT)
                except Exception:
                    await page.keyboard.press("Enter")
                await human_delay(*config.DELAY_PAGE_LOAD)
        except PlaywrightTimeout:
            logger.debug("No username setup screen — continuing.")

    async def _verify_logged_in(self, page: Page, timeout: int = 15_000) -> bool:
        """
        Check whether registration succeeded by looking for a logged-in indicator.
        Returns True if the indicator appears within the timeout.
        """
        try:
            await page.wait_for_selector(Selectors.LOGGED_IN_INDICATOR, timeout=timeout)
            return True
        except PlaywrightTimeout:
            # Fallback: check the URL for an indication of success
            current_url = page.url
            if "foryou" in current_url or "following" in current_url:
                return True
            logger.debug(f"Logged-in indicator not found. Current URL: {current_url}")
            return False

    async def _get_error_text(self, page: Page) -> str:
        """Scrape any visible error message from the page."""
        try:
            el = await page.query_selector(Selectors.ERROR_MSG)
            if el:
                return (await el.text_content() or "").strip()
        except Exception:
            pass
        return ""
