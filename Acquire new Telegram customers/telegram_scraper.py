"""
telegram_scraper.py
───────────────────
Production-ready Telegram Group Member Scraper using Telethon.

SETUP:
  1. Install dependencies:
       pip install -r requirements.txt

  2. Get your Telegram API credentials:
       → Visit https://my.telegram.org/apps
       → Log in with your phone number
       → Create a new application (any name/platform is fine)
       → Copy the "App api_id" and "App api_hash"

  3. Configure credentials:
       → Copy .env.example to .env
       → Fill in your API_ID, API_HASH, PHONE, and TARGET_GROUPS

  4. Run:
       python telegram_scraper.py

NOTES:
  - On first run you will be prompted for your phone's verification code.
  - The session is saved locally so subsequent runs skip authentication.
  - Only groups where YOU are a member and have permission to view members
    can be scraped. Channels or restricted supergroups may return partial data.
  - Respect Telegram's ToS: do not spam, do not abuse this tool.
"""

import asyncio
import csv
import json
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from telethon import TelegramClient, errors
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import (
    Channel,
    ChannelParticipantsSearch,
    Chat,
    InputPeerChannel,
    User,
    UserStatusEmpty,
    UserStatusLastMonth,
    UserStatusLastWeek,
    UserStatusOffline,
    UserStatusOnline,
    UserStatusRecently,
)

# ─── Bootstrap ────────────────────────────────────────────────────────────────

load_dotenv()

# Force UTF-8 output so Rich spinner characters don't crash on Windows cp1252
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# force_jupyter=False + no_color fallback prevents Win32 console Unicode errors
console = Console(force_jupyter=False, highlight=False)

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(console=console, rich_tracebacks=True, markup=False),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("tg_scraper")


# ─── Data Model ───────────────────────────────────────────────────────────────


@dataclass
class MemberRecord:
    """Structured representation of a single Telegram group member."""

    group_title: str = ""
    group_username: str = ""
    user_id: int = 0
    username: str = ""
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    phone: str = ""
    is_bot: bool = False
    is_verified: bool = False
    is_premium: bool = False
    is_restricted: bool = False
    is_scam: bool = False
    is_fake: bool = False
    last_seen_status: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @classmethod
    def from_user(cls, user: User, group_title: str, group_username: str) -> "MemberRecord":
        """Build a MemberRecord from a Telethon User object."""
        return cls(
            group_title=group_title,
            group_username=group_username,
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            full_name=((user.first_name or "") + " " + (user.last_name or "")).strip(),
            phone=user.phone or "",
            is_bot=user.bot or False,
            is_verified=user.verified or False,
            is_premium=getattr(user, "premium", False) or False,
            is_restricted=user.restricted or False,
            is_scam=user.scam or False,
            is_fake=user.fake or False,
            last_seen_status=_status_label(user.status),
        )


def _status_label(status) -> str:
    """Convert a Telegram status object to a human-readable string."""
    if isinstance(status, UserStatusOnline):
        return "online"
    if isinstance(status, UserStatusOffline):
        return f"offline_since_{status.was_online.isoformat()}"
    if isinstance(status, UserStatusRecently):
        return "recently"
    if isinstance(status, UserStatusLastWeek):
        return "last_week"
    if isinstance(status, UserStatusLastMonth):
        return "last_month"
    if isinstance(status, UserStatusEmpty):
        return "unknown"
    return "hidden"


# ─── Exporter ─────────────────────────────────────────────────────────────────


class Exporter:
    """Handles writing collected member records to CSV and/or JSON."""

    def __init__(self, output_dir: Path, fmt: str):
        self.output_dir = output_dir
        self.fmt = fmt.lower()  # "csv", "json", or "both"
        output_dir.mkdir(parents=True, exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    def save(self, records: List[MemberRecord], group_slug: str) -> List[Path]:
        """Persist records and return the list of created file paths."""
        saved: List[Path] = []
        ts = self._timestamp()
        safe_slug = "".join(c if c.isalnum() or c in "_-" else "_" for c in group_slug)

        if self.fmt in ("csv", "both"):
            path = self.output_dir / f"{safe_slug}_{ts}.csv"
            self._write_csv(records, path)
            saved.append(path)

        if self.fmt in ("json", "both"):
            path = self.output_dir / f"{safe_slug}_{ts}.json"
            self._write_json(records, path)
            saved.append(path)

        return saved

    @staticmethod
    def _write_csv(records: List[MemberRecord], path: Path) -> None:
        fieldnames = [f.name for f in fields(MemberRecord)]
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(asdict(r) for r in records)
        log.info(f"CSV saved -> {path}")

    @staticmethod
    def _write_json(records: List[MemberRecord], path: Path) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([asdict(r) for r in records], fh, ensure_ascii=False, indent=2)
        log.info(f"JSON saved -> {path}")


# ─── Scraper Core ─────────────────────────────────────────────────────────────


class TelegramScraper:
    """
    Asynchronous Telegram group member scraper.

    Uses GetParticipantsRequest (for supergroups/channels) or
    iter_participants (for regular groups) depending on entity type,
    with automatic back-off on rate limit errors.
    """

    # Telethon returns at most 200 participants per page
    _CHUNK_SIZE = 200

    def __init__(
        self,
        client: TelegramClient,
        request_delay: float = 0.5,
        max_members: int = 0,
    ):
        self.client = client
        self.request_delay = request_delay
        self.max_members = max_members  # 0 means unlimited

    # ── Public API ────────────────────────────────────────────────────────────

    async def scrape_group(self, group_identifier: str) -> List[MemberRecord]:
        """
        Scrape all accessible members from a group/channel.

        :param group_identifier: Username (@group), t.me link, or numeric ID.
        :returns: List of MemberRecord objects.
        """
        log.info(f"Resolving entity: {group_identifier}")
        try:
            entity = await self.client.get_entity(group_identifier)
        except ValueError as exc:
            log.error(f"Cannot resolve '{group_identifier}': {exc}")
            return []
        except errors.FloodWaitError as exc:
            log.warning(f"FloodWait {exc.seconds}s while resolving entity - waiting...")
            await asyncio.sleep(exc.seconds + 5)
            return await self.scrape_group(group_identifier)
        except Exception as exc:
            log.error(f"Unexpected error resolving '{group_identifier}': {exc}")
            return []

        group_title = getattr(entity, "title", str(entity.id))
        group_username = getattr(entity, "username", "") or str(entity.id)
        log.info(f"Scraping: {group_title} (@{group_username})")

        # Use iter_participants — works for supergroups, basic chats, and
        # channels where the account has visibility of members.
        records = await self._iter_members(entity, group_title, group_username)

        log.info(f"Collected {len(records)} members from {group_title}")
        return records

    # ── Private helpers ───────────────────────────────────────────────────────

    async def _iter_members(
        self, entity, group_title: str, group_username: str
    ) -> List[MemberRecord]:
        """
        Universal member fetcher using Telethon's iter_participants.

        Works for:
          - Basic chats  (all members visible)
          - Supergroups  (all visible members, no admin rights needed)
          - Broadcast channels  (only admins are typically visible;
            regular subscribers cannot be listed without admin rights)

        On FloodWaitError the function waits the required time and retries
        from where it left off.
        """
        records: List[MemberRecord] = []
        log.info(f"Starting member iteration for: {group_title}")

        while True:
            try:
                async for user in self.client.iter_participants(
                    entity,
                    aggressive=True,   # tries multiple search queries to get more members
                ):
                    if not isinstance(user, User):
                        continue

                    records.append(
                        MemberRecord.from_user(user, group_title, group_username)
                    )

                    n = len(records)
                    if n % 100 == 0:
                        log.info(f"  ... {n} members collected so far")

                    if self.max_members and n >= self.max_members:
                        log.info(f"Reached MAX_MEMBERS limit ({self.max_members}), stopping.")
                        break

                    await asyncio.sleep(self.request_delay)

                # Iteration finished normally
                break

            except errors.FloodWaitError as exc:
                wait = exc.seconds + 5
                log.warning(f"Rate limited by Telegram — sleeping {wait}s then resuming...")
                await asyncio.sleep(wait)
                # iter_participants restarts; duplicate records are deduplicated below

            except errors.ChatAdminRequiredError:
                log.error(
                    f"'{group_title}' is a broadcast channel — member list is only "
                    "accessible to channel admins. If you are an admin, verify the "
                    "account has the 'Manage Members' permission."
                )
                break

            except errors.UserNotParticipantError:
                log.error(f"You are not a member of '{group_title}'. Join first, then re-run.")
                break

            except Exception as exc:
                log.error(f"Unexpected error while iterating members: {exc}")
                break

        # Deduplicate in case a FloodWait retry caused re-iteration from start
        seen: set = set()
        unique: List[MemberRecord] = []
        for r in records:
            if r.user_id not in seen:
                seen.add(r.user_id)
                unique.append(r)

        return unique


# ─── Summary Printer ──────────────────────────────────────────────────────────


def _print_summary(all_records: List[MemberRecord]) -> None:
    """Print a Rich table summarising the completed scraping run."""
    table = Table(title="Scraping Summary", show_lines=True)
    table.add_column("Group", style="cyan")
    table.add_column("Total Members", justify="right", style="green")
    table.add_column("With Username", justify="right", style="yellow")
    table.add_column("Bots", justify="right", style="red")

    # Aggregate by group_title
    groups: dict = {}
    for rec in all_records:
        groups.setdefault(rec.group_title, []).append(rec)

    for title, recs in groups.items():
        with_username = sum(1 for r in recs if r.username)
        bots = sum(1 for r in recs if r.is_bot)
        table.add_row(title, str(len(recs)), str(with_username), str(bots))

    console.print(table)


# ─── Entry Point ──────────────────────────────────────────────────────────────


async def main() -> None:
    # ── Read configuration from .env ──────────────────────────────────────────
    api_id_raw = os.getenv("TELEGRAM_API_ID", "")
    api_hash = os.getenv("TELEGRAM_API_HASH", "")
    phone = os.getenv("TELEGRAM_PHONE", "")
    password = os.getenv("TELEGRAM_PASSWORD", "") or None
    session_name = os.getenv("SESSION_NAME", "telegram_scraper")
    groups_raw = os.getenv("TARGET_GROUPS", "")
    output_fmt = os.getenv("OUTPUT_FORMAT", "both")
    output_dir = Path(os.getenv("OUTPUT_DIR", "./output"))
    delay = float(os.getenv("REQUEST_DELAY", "0.5"))
    max_members = int(os.getenv("MAX_MEMBERS", "0"))

    # Validate required settings before connecting
    missing = []
    if not api_id_raw:
        missing.append("TELEGRAM_API_ID")
    if not api_hash:
        missing.append("TELEGRAM_API_HASH")
    if not phone:
        missing.append("TELEGRAM_PHONE")
    if not groups_raw:
        missing.append("TARGET_GROUPS")

    if missing:
        console.print(
            f"[bold red]Missing required environment variables:[/] {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in the values."
        )
        sys.exit(1)

    try:
        api_id = int(api_id_raw)
    except ValueError:
        console.print("[bold red]TELEGRAM_API_ID must be an integer.[/]")
        sys.exit(1)

    target_groups = [g.strip() for g in groups_raw.split(",") if g.strip()]

    # ── Connect & authenticate ────────────────────────────────────────────────
    log.info("Connecting to Telegram...")
    client = TelegramClient(session_name, api_id, api_hash)

    # client.start() handles the interactive OTP flow automatically
    await client.start(phone=phone, password=password)

    me = await client.get_me()
    log.info(
        f"Authenticated as {me.first_name} (@{me.username}) - ID {me.id}"
    )

    # ── Scrape all target groups ──────────────────────────────────────────────
    scraper = TelegramScraper(client, request_delay=delay, max_members=max_members)
    exporter = Exporter(output_dir, output_fmt)
    all_records: List[MemberRecord] = []

    for group_id in target_groups:
        records = await scraper.scrape_group(group_id)
        if records:
            all_records.extend(records)
            # Derive a filesystem-safe slug from the group identifier
            slug = group_id.lstrip("@").replace("https://t.me/", "")
            saved_paths = exporter.save(records, slug)
            for p in saved_paths:
                console.print(f"  Saved: {p}")

    # ── Final summary table ───────────────────────────────────────────────────
    console.print()
    _print_summary(all_records)
    console.print(f"\nDone! Total members collected: {len(all_records)}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
