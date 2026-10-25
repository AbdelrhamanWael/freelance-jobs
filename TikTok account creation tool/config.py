"""
config.py
─────────
Central configuration for the TikTok Account Creator.
Edit values here or override them via environment variables.
"""

import os

# ──────────────────────────────────────────────
# API Keys
# ──────────────────────────────────────────────
SADCAPTCHA_API_KEY: str = os.getenv("SADCAPTCHA_API_KEY", "f3da6df4c7f8f871c95ca36d56545712")

# Temp-email provider: "mailtm" | "kopeechka"
EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "kopeechka")

# Mail.tm credentials (account is auto-created if left empty)
MAILTM_BASE_URL: str = "https://api.mail.tm"

# Kopeechka (Kopechka.com v1 REST API)
KOPEECHKA_API_KEY: str = os.getenv("KOPEECHKA_API_KEY", "kop_v1_KNNT0y5ol5ERZKGyO7jPt0Bg7MvMu-Fxr2lzIT7sg7M")
KOPEECHKA_BASE_URL: str = "https://api.kopechka.com/api/v1"

# SadCaptcha API base URL
SADCAPTCHA_BASE_URL: str = "https://www.sadcaptcha.com/api/v1"

# ──────────────────────────────────────────────
# Account Generation Settings
# ──────────────────────────────────────────────
TOTAL_ACCOUNTS: int = int(os.getenv("TOTAL_ACCOUNTS", "10"))   # How many to create
USE_PROXIES: bool = os.getenv("USE_PROXIES", "false").lower() == "true"  # Enable/disable proxies

# Passwoxrd policy
PASSWORD_MIN_LENGTH: int = 12
PASSWORD_MAX_LENGTH: int = 20

# ──────────────────────────────────────────────
# Browser / Stealth Settings
# ──────────────────────────────────────────────
BROWSER_HEADLESS: bool = False          # Always False — use off-screen trick instead
WINDOW_POSITION: str = "-2000,-2000"   # Moves window completely off-screen
WINDOW_SIZE: str = "1280,800"

# Randomise viewport slightly per session
VIEWPORT_JITTER_W: int = 200   # +/- pixels
VIEWPORT_JITTER_H: int = 100

# ──────────────────────────────────────────────
# Timing / Human-like Delays (seconds)
# ──────────────────────────────────────────────
DELAY_BETWEEN_KEYSTROKES: tuple = (0.05, 0.18)
DELAY_AFTER_CLICK:        tuple = (0.4, 1.2)
DELAY_PAGE_LOAD:          tuple = (2.0, 4.5)
DELAY_OTP_POLL_INTERVAL:  float = 5.0   # seconds between inbox polls
OTP_POLL_MAX_ATTEMPTS:    int   = 36    # 36 x 5 s = 3 min timeout

# ──────────────────────────────────────────────
# TikTok URLs
# ──────────────────────────────────────────────
TIKTOK_SIGNUP_URL: str = "https://www.tiktok.com/signup/phone-or-email/email"
TIKTOK_BASE_URL:   str = "https://www.tiktok.com"

# ──────────────────────────────────────────────
# File paths
# ──────────────────────────────────────────────
PROXIES_FILE:   str = "proxies.txt"
ACCOUNTS_DIR:   str = "accounts"       # Exported session JSONs go here
LOG_FILE:       str = "tiktok_bot.log"
