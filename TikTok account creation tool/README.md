# TikTok Account Creator 🎭

A professional, stealth-grade automated TikTok account registration tool built with Python and Playwright.

---

## 📋 Features

| Feature | Details |
|---|---|
| **Anti-Detect Browser** | Off-screen Chromium (not headless), removes all automation flags |
| **playwright-stealth** | Patches Navigator, WebGL, Canvas, AudioContext & Hairline |
| **Canvas Noise** | Per-session pixel-level noise defeats fingerprinting |
| **Bezier Mouse Drags** | Human-like curved drag paths for captcha sliders |
| **Captcha Solver** | SadCaptcha API integration (puzzle + rotate types) |
| **Temp Email** | Mail.tm (free) or Kopeechka (paid) — switchable |
| **Proxy Rotation** | Fresh proxy per account; auto-discards banned proxies |
| **OTP Handling** | Polls inbox, extracts 6-digit code, enters with human timing |
| **Session Export** | Saves cookies + UA + proxy + credentials to JSON |
| **Rich Dashboard** | Live CLI stats table + activity log |

---

## 🗂 Project Structure

```
├── main.py              # Entry point + orchestration + Rich dashboard
├── config.py            # All configuration (API keys, delays, paths)
├── tiktok_bot.py        # Core registration workflow
├── browser_manager.py   # Stealth Playwright browser factory
├── captcha_solver.py    # SadCaptcha integration (puzzle + rotate)
├── email_manager.py     # Mail.tm / Kopeechka OTP managers
├── utils.py             # Shared helpers (Bezier drag, data gen, export)
├── requirements.txt     # Python dependencies
├── proxies.txt          # Your proxy list (IP:Port:User:Pass)
└── accounts/            # Exported session JSON files (auto-created)
```

---

## ⚙️ Setup & Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright browsers

```bash
playwright install chromium
```

### 3. Configure `config.py`

Open `config.py` and set:

```python
SADCAPTCHA_API_KEY = "your_sadcaptcha_key"
EMAIL_PROVIDER     = "mailtm"       # or "kopeechka"
KOPEECHKA_API_KEY  = "..."          # only if using kopeechka
TOTAL_ACCOUNTS     = 10             # how many accounts to create
```

Or set environment variables:

```bash
set SADCAPTCHA_API_KEY=your_key_here
set EMAIL_PROVIDER=mailtm
set TOTAL_ACCOUNTS=5
```

### 4. Add proxies to `proxies.txt`

```
185.220.101.45:1080:user:pass
192.168.1.100:8080
```

---

## 🚀 Running

```bash
python main.py
```

---

## 📁 Session Output

Each successful account is saved to `accounts/account_<username>.json`:

```json
{
  "email": "xyz@mail.tm",
  "password": "SecurePass!42",
  "username": "cooluser7890",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0...",
  "proxy": "185.220.101.45:1080",
  "cookies": [ ... ],
  "exported_at": "2024-01-01T12:00:00Z"
}
```

---

## 🔧 Proxy Format

`proxies.txt` supports:
- `IP:Port` — unauthenticated
- `IP:Port:Username:Password` — authenticated

---

## ⚠️ Disclaimer

This tool is provided for **educational and research purposes only**.
The author assumes no responsibility for misuse. Always comply with
TikTok's Terms of Service and applicable laws in your jurisdiction.

---

## 🔑 API Services Used

| Service | Purpose | Link |
|---|---|---|
| **SadCaptcha** | Captcha solving (puzzle + rotate) | https://www.sadcaptcha.com |
| **Mail.tm** | Free disposable email + OTP | https://mail.tm |
| **Kopeechka** | Paid disposable email (alternative) | https://kopeechka.store |
