"""
main.py
───────
CLI entry point and orchestration layer for the TikTok Account Creator.

Features:
  • Live Rich dashboard showing real-time stats
  • Sequential account creation with fresh proxy per attempt
  • Automatic proxy rotation on failure / ban detection
  • Graceful shutdown on Ctrl-C with partial results summary
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal
import sys
import time
from contextlib import suppress
from pathlib import Path
from typing import Optional

# ── Force UTF-8 output on Windows to handle emoji in Rich panels ──────────────
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text
from rich.prompt import IntPrompt

import config
from captcha_solver import CaptchaSolver
from email_manager import get_email_manager
from tiktok_bot import TikTokBot, RegistrationResult
from utils import load_proxies, Proxy, validate_proxy

logger = logging.getLogger("TikTokBot.Main")


# ──────────────────────────────────────────────────────────────────────────────
# Rich Dashboard
# ──────────────────────────────────────────────────────────────────────────────

class Dashboard:
    """
    Manages the live Rich CLI dashboard.
    Renders a stats table + progress bar + activity log.
    """

    MAX_LOG_LINES = 12  # Max lines shown in the activity log panel

    def __init__(self, total: int) -> None:
        self.total      = total
        self.success    = 0
        self.failed     = 0
        self.remaining  = 0      # Updated from proxy list
        self.status     = "Initialising…"
        self.start_time = time.time()
        self._log_lines: list[str] = []

        self.console  = Console()
        self.progress = Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=40, style="cyan", complete_style="green"),
            MofNCompleteColumn(),
            TextColumn("[green]{task.percentage:>5.1f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=False,
        )
        self._task_id: Optional[TaskID] = None

    def _build_stats_table(self) -> Table:
        """Build the top-level statistics table."""
        elapsed = int(time.time() - self.start_time)
        h, rem  = divmod(elapsed, 3600)
        m, s    = divmod(rem, 60)
        elapsed_str = f"{h:02d}:{m:02d}:{s:02d}"

        success_rate = (
            f"{self.success / (self.success + self.failed) * 100:.1f}%"
            if (self.success + self.failed) > 0
            else "N/A"
        )

        table = Table(
            title="[bold magenta]🎭 TikTok Account Creator[/bold magenta]",
            box=box.ROUNDED,
            border_style="bright_blue",
            show_header=True,
            header_style="bold bright_white on dark_blue",
            min_width=70,
        )
        table.add_column("Metric",          style="bright_cyan",  justify="left",   min_width=20)
        table.add_column("Value",           style="bright_white", justify="center",  min_width=20)
        table.add_column("Status",          style="bright_white", justify="center",  min_width=20)

        table.add_row("🎯 Target Accounts",  str(self.total),       "")
        table.add_row(
            "✅ Successful",
            f"[bold green]{self.success}[/bold green]",
            f"[green]{'▓' * min(self.success, 20)}[/green]",
        )
        table.add_row(
            "❌ Failed",
            f"[bold red]{self.failed}[/bold red]",
            f"[red]{'▓' * min(self.failed, 20)}[/red]",
        )
        table.add_row(
            "📡 Proxies Left",
            f"[bold yellow]{self.remaining}[/bold yellow]",
            "",
        )
        table.add_row("📈 Success Rate",    success_rate,          "")
        table.add_row("⏱  Elapsed",        elapsed_str,           "")
        table.add_row(
            "⚡ Current Status",
            f"[bold bright_yellow]{self.status}[/bold bright_yellow]",
            "",
        )
        return table

    def _build_log_panel(self) -> Panel:
        """Build the scrolling activity log panel."""
        lines = self._log_lines[-self.MAX_LOG_LINES:]
        content = "\n".join(lines) if lines else "[dim]Waiting for activity…[/dim]"
        return Panel(
            content,
            title="[bold]📋 Activity Log[/bold]",
            border_style="dim blue",
            padding=(0, 1),
        )

    def build_layout(self) -> Columns:
        """Compose the full dashboard layout."""
        return Columns(
            [self._build_stats_table(), self._build_log_panel()],
            equal=False,
            expand=True,
        )

    def log(self, message: str, level: str = "info") -> None:
        """Append a message to the activity log and the Python logger."""
        icons   = {"info": "ℹ️ ", "success": "✅", "error": "❌", "warn": "⚠️ "}
        colours = {"info": "white", "success": "green", "error": "red", "warn": "yellow"}
        icon    = icons.get(level, "•")
        colour  = colours.get(level, "white")
        ts      = time.strftime("%H:%M:%S")
        line    = f"[dim]{ts}[/dim] {icon} [{colour}]{message}[/{colour}]"
        self._log_lines.append(line)

        # Also log to file logger
        if level == "error":
            logger.error(message)
        elif level == "warn":
            logger.warning(message)
        else:
            logger.info(message)

    def update(
        self,
        status: Optional[str] = None,
        success_delta: int = 0,
        failed_delta: int = 0,
        remaining: Optional[int] = None,
    ) -> None:
        """Update dashboard counters and status string."""
        if status:
            self.status = status
        self.success += success_delta
        self.failed  += failed_delta
        if remaining is not None:
            self.remaining = remaining


# ──────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ──────────────────────────────────────────────────────────────────────────────

class Orchestrator:
    """
    Main controller.  Iterates through proxies and creates accounts one-by-one.
    """

    def __init__(self) -> None:
        self.proxies        = load_proxies(config.PROXIES_FILE) if config.USE_PROXIES else []
        self.proxy_index    = 0
        self.dashboard      = Dashboard(total=config.TOTAL_ACCOUNTS)
        self._shutdown      = False
        self._consecutive_failures = 0   # Track back-to-back failures
        self._rate_limited  = False      # True when TikTok returns error_code 7

        # Shared captcha solver (stateless — can be reused across sessions)
        self.captcha_solver = CaptchaSolver()

    def _next_proxy(self) -> Optional[Proxy]:
        """Return the next proxy from the list, or None if exhausted."""
        # Skip proxies that have been marked as failed
        while self.proxy_index < len(self.proxies):
            proxy = self.proxies[self.proxy_index]
            self.proxy_index += 1
            return proxy
        return None

    async def _create_one_account(self, attempt_num: int, live: Live) -> bool:
        """
        Run a single account creation attempt.
        Returns True on success, False on failure.
        """
        proxy = self._next_proxy()
        proxy_str = str(proxy) if proxy else "No Proxy"
        remaining_proxies = len(self.proxies) - self.proxy_index

        self.dashboard.update(
            status=f"[{attempt_num}/{config.TOTAL_ACCOUNTS}] Connecting via {proxy_str}",
            remaining=remaining_proxies,
        )
        self.dashboard.log(f"Attempt #{attempt_num} — Proxy: {proxy_str}")
        live.update(self.dashboard.build_layout())

        # Validate proxy before attempting registration
        if proxy:
            self.dashboard.update(status=f"[{attempt_num}] Validating proxy...")
            live.update(self.dashboard.build_layout())
            proxy_valid = await validate_proxy(proxy)
            if not proxy_valid:
                self.dashboard.update(
                    status=f"❌ Proxy validation failed: {proxy_str}",
                    failed_delta=1,
                )
                self.dashboard.log(f"Proxy validation failed #{attempt_num}: {proxy_str}", "error")
                live.update(self.dashboard.build_layout())
                # If this was the last proxy, try without proxy
                if remaining_proxies == 0:
                    self.dashboard.log("All proxies failed, attempting without proxy...", "warn")
                    proxy = None
                else:
                    return False

        # Create a fresh email manager per session
        email_mgr = get_email_manager()

        try:
            bot = TikTokBot(
                proxy=proxy,
                email_manager=email_mgr,
                captcha_solver=self.captcha_solver,
            )

            self.dashboard.update(status=f"[{attempt_num}] Running registration…")
            live.update(self.dashboard.build_layout())

            result: RegistrationResult = await bot.run()

            if result.success:
                self._consecutive_failures = 0
                self._rate_limited = False
                self.dashboard.update(
                    status=f"✅ Account created: {result.email}",
                    success_delta=1,
                )
                self.dashboard.log(
                    f"Created: {result.email} → {result.session_file}", "success"
                )
                live.update(self.dashboard.build_layout())
                return True
            else:
                self._consecutive_failures += 1
                error = result.error.lower()

                # Detect IP rate-limit (error_code 7)
                is_rate_limited = "maximum" in error or "attempts" in error or "try again" in error
                if is_rate_limited:
                    self._rate_limited = True

                # Detect common ban signals
                ban_signals = ("maximum attempts", "blocked", "banned", "flagged", "risk")
                is_proxy_ban = proxy and any(sig in error for sig in ban_signals)

                self.dashboard.update(
                    status=f"❌ Failed: {result.error[:60]}",
                    failed_delta=1,
                )
                msg = f"Failed #{attempt_num}: {result.error}"
                if is_proxy_ban:
                    msg += f" [Proxy {proxy_str} discarded]"
                self.dashboard.log(msg, "error")
                live.update(self.dashboard.build_layout())
                return False

        except Exception as exc:
            self.dashboard.update(
                status=f"❌ Critical error: {str(exc)[:60]}",
                failed_delta=1,
            )
            self.dashboard.log(f"Critical error #{attempt_num}: {exc}", "error")
            live.update(self.dashboard.build_layout())
            return False

        finally:
            await email_mgr.close()

    async def run(self) -> None:
        """Main execution loop with live Rich dashboard."""
        console = self.dashboard.console

        console.print(
            Panel.fit(
                "[bold magenta]🎭 TikTok Account Creator[/bold magenta]\n"
                "[dim]Stealth Mode • Playwright • SadCaptcha[/dim]",
                border_style="bright_magenta",
                padding=(1, 4),
            )
        )

        Path(config.ACCOUNTS_DIR).mkdir(exist_ok=True)

        with Live(
            self.dashboard.build_layout(),
            console=console,
            refresh_per_second=4,
            screen=False,
        ) as live:

            attempt = 0
            while self.dashboard.success < config.TOTAL_ACCOUNTS and not self._shutdown:
                # Only check for proxy exhaustion if we're using proxies
                if config.USE_PROXIES and not self.proxies:
                    self.dashboard.log("Out of proxies! Stopping.", "error")
                    break

                attempt += 1
                await self._create_one_account(attempt, live)

                if self._shutdown or self.dashboard.success >= config.TOTAL_ACCOUNTS:
                    break

                # ── Rate-limit backoff ────────────────────────────────────────
                if self._rate_limited:
                    # TikTok has temporarily blocked this IP from sending OTPs.
                    # Backing off for 5 minutes gives the block time to expire.
                    backoff = 300  # 5 minutes
                    self.dashboard.log(
                        f"⚠️ IP rate-limited by TikTok (error_code 7). "
                        f"Waiting {backoff // 60} min before next attempt…", "warn"
                    )
                    for remaining in range(backoff, 0, -5):
                        if self._shutdown:
                            break
                        self.dashboard.update(
                            status=f"⏸ Rate-limit cooldown — {remaining}s remaining…"
                        )
                        live.update(self.dashboard.build_layout())
                        await asyncio.sleep(5)
                    self._rate_limited = False
                    self._consecutive_failures = 0
                    continue

                # ── Abort if too many consecutive failures with no proxy ───────
                if self._consecutive_failures >= 5 and not config.USE_PROXIES:
                    self.dashboard.log(
                        "🛑 5 consecutive failures with no proxy. "
                        "Your IP is likely blocked. Please add proxies or wait ~30 min.",
                        "error",
                    )
                    break

                # ── Normal inter-attempt pause (always, not just when proxies) ─
                pause = 5 + (attempt % 5)  # 5–9 seconds, slightly varied
                self.dashboard.update(status=f"Cooling down ({pause}s)…")
                live.update(self.dashboard.build_layout())
                await asyncio.sleep(pause)

        await self.captcha_solver.close()

        # ── Final Summary ─────────────────────────────────────────────────
        console.print()
        console.print(
            Panel(
                f"[bold green]✅ Successful:[/bold green] {self.dashboard.success}\n"
                f"[bold red]❌ Failed:    [/bold red] {self.dashboard.failed}\n"
                f"[bold cyan]📁 Sessions:  [/bold cyan] ./{config.ACCOUNTS_DIR}/",
                title="[bold white]Run Complete[/bold white]",
                border_style="green",
                padding=(1, 4),
            )
        )

    def signal_shutdown(self) -> None:
        """Gracefully signal the loop to stop after the current attempt."""
        self._shutdown = True
        logger.info("Shutdown signal received — stopping after current attempt.")


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

async def _async_main() -> None:
    orchestrator = Orchestrator()

    # Graceful Ctrl-C handling
    loop = asyncio.get_running_loop()

    def _handle_signal():
        orchestrator.dashboard.log("Ctrl-C received — finishing current account…", "warn")
        orchestrator.signal_shutdown()

    with suppress(NotImplementedError):
        # Unix / Windows compatibility
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _handle_signal)

    await orchestrator.run()


def main() -> None:
    """Synchronous entry point — boots the asyncio event loop."""
    try:
        print("\n")
        target = IntPrompt.ask("[cyan]🎯 How many SUCCESSFUL accounts do you want to create?[/cyan]", default=config.TOTAL_ACCOUNTS)
        config.TOTAL_ACCOUNTS = target
        print("\n")
        asyncio.run(_async_main())
    except KeyboardInterrupt:
        print("\n[yellow]Interrupted by user.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
