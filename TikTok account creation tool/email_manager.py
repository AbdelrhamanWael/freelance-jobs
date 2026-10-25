"""
email_manager.py
────────────────
Manages temporary email addresses and OTP retrieval.

Supports two providers selectable via config.EMAIL_PROVIDER:
  1. "mailtm"    — https://mail.tm  (free, no API key required)
  2. "kopeechka" — https://kopeechka.store (paid, requires API key)

Each manager exposes the same async interface:
    email, token = await manager.create_inbox()
    code         = await manager.wait_for_otp(email, token)
"""

from __future__ import annotations

import asyncio
import logging
import re
import ssl
import time
import uuid
from abc import ABC, abstractmethod
from typing import Optional

import aiohttp

import config

logger = logging.getLogger("TikTokBot.EmailManager")

# Regex to extract 6-digit OTP codes from email bodies
OTP_PATTERN = re.compile(r"\b(\d{6})\b")


# ──────────────────────────────────────────────────────────────────────────────
# Base class
# ──────────────────────────────────────────────────────────────────────────────

class BaseEmailManager(ABC):
    """Abstract interface for temp-email providers."""

    @abstractmethod
    async def create_inbox(self) -> tuple[str, str]:
        """
        Create a new disposable inbox.
        Returns: (email_address, auth_token_or_id)
        """

    @abstractmethod
    async def wait_for_otp(self, email: str, token: str) -> Optional[str]:
        """
        Poll the inbox until a 6-digit OTP from TikTok arrives.
        Returns the code, or None on timeout.
        """

    @abstractmethod
    async def close(self) -> None:
        """Release any open network sessions."""


# ──────────────────────────────────────────────────────────────────────────────
# Mail.tm Provider
# ──────────────────────────────────────────────────────────────────────────────

class MailTmManager(BaseEmailManager):
    """
    Uses the public Mail.tm REST API (free, no key required).
    Docs: https://docs.mail.tm/
    """

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # ── Domain discovery ─────────────────────────────────────────────────────

    async def _get_domain(self) -> str:
        """Fetch the first available Mail.tm domain."""
        session = await self._get_session()
        async with session.get(
            f"{config.MAILTM_BASE_URL}/domains",
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            data = await resp.json()
            domains = data.get("hydra:member", [])
            if not domains:
                raise RuntimeError("Mail.tm returned no available domains.")
            return domains[0]["domain"]

    # ── Inbox creation ───────────────────────────────────────────────────────

    async def create_inbox(self) -> tuple[str, str]:
        """
        Register a new random mailbox on Mail.tm.
        Returns (email, jwt_token).
        """
        import random, string
        session  = await self._get_session()
        domain   = await self._get_domain()
        # Retry loop for rate limits (429) or Timeouts
        for attempt in range(5):
            username = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
            password = "".join(random.choices(string.ascii_letters + string.digits, k=16))
            email    = f"{username}@{domain}"

            try:
                # Create account
                async with session.post(
                    f"{config.MAILTM_BASE_URL}/accounts",
                    json={"address": email, "password": password},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 429:
                        logger.warning(f"Mail.tm Rate Limit (429). Waiting 15s before retry ({attempt+1}/5)...")
                        await asyncio.sleep(15)
                        continue
                    if resp.status not in (200, 201):
                        text = await resp.text()
                        logger.warning(f"Mail.tm account creation failed: {resp.status} {text}")
                        await asyncio.sleep(10)
                        continue

                # Authenticate to get JWT
                async with session.post(
                    f"{config.MAILTM_BASE_URL}/token",
                    json={"address": email, "password": password},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    data = await resp.json()
                    token = data.get("token")
                    if not token:
                        logger.warning(f"Mail.tm token not received: {data}")
                        await asyncio.sleep(5)
                        continue

                logger.info(f"Mail.tm inbox created: {email}")
                return email, token
                
            except Exception as e:
                logger.warning(f"Mail.tm connection error: {type(e).__name__}. Retrying in 10s ({attempt+1}/5)...")
                await asyncio.sleep(10)

        raise RuntimeError("Mail.tm account creation failed after 5 retries.")

    # ── OTP polling ──────────────────────────────────────────────────────────

    async def wait_for_otp(self, email: str, token: str) -> Optional[str]:
        """
        Poll the Mail.tm inbox until a TikTok verification email arrives.
        Returns the 6-digit code or None on timeout.
        """
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {token}"}

        for attempt in range(config.OTP_POLL_MAX_ATTEMPTS):
            logger.debug(f"Polling inbox ({attempt + 1}/{config.OTP_POLL_MAX_ATTEMPTS})…")
            try:
                async with session.get(
                    f"{config.MAILTM_BASE_URL}/messages",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    data = await resp.json()
                    messages = data.get("hydra:member", [])

                    for msg in messages:
                        subject = msg.get("subject", "").lower()
                        # TikTok usually puts "verification" or "code" in the subject
                        if any(kw in subject for kw in ("verify", "code", "tiktok", "confirm")):
                            # Fetch full message body
                            msg_id = msg["id"]
                            async with session.get(
                                f"{config.MAILTM_BASE_URL}/messages/{msg_id}",
                                headers=headers,
                                timeout=aiohttp.ClientTimeout(total=15),
                            ) as detail_resp:
                                detail = await detail_resp.json()
                                body = detail.get("text", "") or detail.get("html", "")
                                match = OTP_PATTERN.search(body)
                                if match:
                                    code = match.group(1)
                                    logger.info(f"OTP found: {code}")
                                    return code

            except Exception as exc:
                logger.warning(f"Inbox poll error: {exc}")

            await asyncio.sleep(config.DELAY_OTP_POLL_INTERVAL)

        logger.error("OTP not received within timeout.")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Kopeechka Provider
# ──────────────────────────────────────────────────────────────────────────────

class KopeechkaManager(BaseEmailManager):
    """
    Uses the official Kopechka.com REST API (v1) for temporary email addresses.
    Base URL: https://api.kopechka.com/api/v1
    """

    def __init__(self) -> None:
        self.api_key = config.KOPEECHKA_API_KEY
        self.base_url = config.KOPEECHKA_BASE_URL.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None
        self._ssl_ctx = ssl.create_default_context()
        self._ssl_ctx.check_hostname = False
        self._ssl_ctx.verify_mode = ssl.CERT_NONE

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            conn = aiohttp.TCPConnector(ssl=self._ssl_ctx)
            self._session = aiohttp.ClientSession(connector=conn)
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    # Domains confirmed degraded for TikTok (0% delivery rate)
    BLACKLISTED_DOMAINS = {"mail.com"}

    # Preferred domains ordered by deliverability + stock
    # rambler.ru has 4,600 slots and is NOT in degraded list
    PREFERRED_DOMAINS = [
        "rambler.ru",
        "gmx.us",
        "email.com",
        "gmx.ca",
        "usa.com",
        "gmx.com",
        "t-online.de",
    ]

    async def _get_best_domain(self) -> str:
        """Return the best available domain for tiktok.com, avoiding all degraded domains.
        
        NOTE: Kopechka's site-domain-yield API returns bestDomain=null for tiktok.com
        because no domain has a statistically significant delivery history yet.
        We therefore use our own preferred list and avoid mail.com (0% delivery).
        """
        session = await self._get_session()
        headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        }

        # Collect degraded domains from Kopechka
        degraded: set[str] = set(self.BLACKLISTED_DOMAINS)
        try:
            async with session.get(
                f"{self.base_url}/site-domain-yield",
                params={"site": "tiktok.com"},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    extra_degraded = data.get("data", {}).get("degraded", [])
                    degraded.update(extra_degraded)
                    logger.debug(f"Kopechka degraded domains for tiktok.com: {degraded}")
        except Exception as e:
            logger.warning(f"Could not fetch site-domain-yield: {e}")

        # Query available domain stock
        try:
            async with session.get(
                f"{self.base_url}/domains",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    dom_list = data.get("data", [])
                    # Build lookup: name -> availableCount
                    stock = {
                        d["name"]: d.get("availableCount", 0)
                        for d in dom_list
                        if d.get("name") not in degraded
                        and d.get("availableCount", 0) > 0
                    }
                    logger.debug(f"Kopechka non-degraded domains in stock: {len(stock)}")
                    # Pick first preferred domain that has stock
                    for pref in self.PREFERRED_DOMAINS:
                        if pref in stock:
                            logger.info(f"Selected email domain: {pref} ({stock[pref]} available)")
                            return pref
                    # Last resort: highest-stock non-degraded domain
                    if stock:
                        best = max(stock, key=lambda k: stock[k])
                        logger.info(f"Fallback email domain: {best} ({stock[best]} available)")
                        return best
        except Exception as e:
            logger.warning(f"Could not fetch domains list: {e}")

        logger.warning("Falling back to hardcoded rambler.ru domain")
        return "rambler.ru"

    async def create_inbox(self) -> tuple[str, str]:
        """
        Create a new email order on Kopechka.com targeting tiktok.com.
        Returns: (email, order_id)
        """
        session = await self._get_session()
        domain = await self._get_best_domain()

        headers = {
            "x-api-key": self.api_key,
            "idempotency-key": str(uuid.uuid4()),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        }
        body = {
            "site": "tiktok.com",
            "domain": domain,
        }

        async with session.post(
            f"{self.base_url}/orders",
            json=body,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=20),
        ) as resp:
            data = await resp.json()
            if resp.status not in (200, 201) or not data.get("success"):
                raise RuntimeError(f"Kopechka create order failed ({resp.status}): {data}")

            order_data = data.get("data", {})
            email = order_data["email"]
            order_id = order_data["orderId"]
            logger.info(f"Kopechka inbox created: {email} (orderId: {order_id})")
            return email, order_id

    async def wait_for_otp(self, email: str, token: str) -> Optional[str]:
        """
        Poll Kopechka.com for messages for the given orderId.
        Returns the 6-digit OTP code, and completes the order to release slot.
        """
        session = await self._get_session()
        order_id = token
        headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0",
        }

        for attempt in range(config.OTP_POLL_MAX_ATTEMPTS):
            logger.debug(f"Kopechka poll ({attempt + 1}/{config.OTP_POLL_MAX_ATTEMPTS}) — order: {order_id}…")
            try:
                async with session.get(
                    f"{self.base_url}/orders/{order_id}/messages",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    data = await resp.json()
                    if resp.status != 200:
                        logger.warning(f"Kopechka messages HTTP {resp.status}: {data}")
                    else:
                        messages = data.get("messages", [])
                        order_status = data.get("order", {}).get("status", "unknown")
                        if not messages:
                            logger.debug(f"No messages yet (order status: {order_status})")
                        else:
                            logger.info(f"Kopechka received {len(messages)} message(s)!")
                            for msg in messages:
                                # Try all possible body/content fields
                                body = (
                                    msg.get("body")
                                    or msg.get("content")
                                    or msg.get("text")
                                    or msg.get("html")
                                    or ""
                                )
                                logger.debug(f"Message body snippet: {body[:200]!r}")
                                match = OTP_PATTERN.search(body)
                                if match:
                                    code = match.group(1)
                                    logger.info(f"Kopechka OTP found: {code}")
                                    # Complete order to free the slot
                                    try:
                                        await session.post(
                                            f"{self.base_url}/orders/{order_id}/complete",
                                            headers=headers,
                                            timeout=aiohttp.ClientTimeout(total=10),
                                        )
                                        logger.debug("Kopechka order marked complete.")
                                    except Exception as ce:
                                        logger.debug(f"Kopechka complete call failed (non-critical): {ce}")
                                    return code
                            # Messages arrived but no OTP found — log raw content
                            logger.warning(f"Messages arrived but no 6-digit OTP found: {messages}")
            except Exception as exc:
                logger.warning(f"Kopechka poll error: {exc}")

            await asyncio.sleep(config.DELAY_OTP_POLL_INTERVAL)

        logger.error(f"Kopechka: OTP not received within {config.OTP_POLL_MAX_ATTEMPTS * config.DELAY_OTP_POLL_INTERVAL:.0f}s timeout for order {order_id}.")
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Factory
# ──────────────────────────────────────────────────────────────────────────────

def get_email_manager() -> BaseEmailManager:
    """
    Return the configured email manager instance based on config.EMAIL_PROVIDER.
    Raises ValueError if the provider is unrecognised.
    """
    provider = config.EMAIL_PROVIDER.lower().strip()
    if provider == "mailtm":
        return MailTmManager()
    elif provider == "kopeechka":
        return KopeechkaManager()
    else:
        raise ValueError(
            f"Unknown EMAIL_PROVIDER {provider!r}. "
            "Choose 'mailtm' or 'kopeechka' in config.py."
        )
