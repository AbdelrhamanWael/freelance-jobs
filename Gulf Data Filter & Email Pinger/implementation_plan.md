# Gulf Data Filter & Email Pinger — Implementation Plan

This is a full-stack demo desktop app for filtering and validating Gulf-region contact data (emails + phone numbers) from uploaded Excel/CSV files. The backend uses Flask + Pandas with threaded DNS MX lookups, and the frontend is a premium dark-mode dashboard with drag-and-drop, live progress, and interactive results.

## Proposed Changes

### Project Structure

```
Gulf Data Filter & Email Pinger/
├── app.py                  # [NEW] Flask backend
├── requirements.txt        # [NEW] Python dependencies
├── templates/
│   └── index.html          # [NEW] Tailwind dark dashboard
└── static/
    └── (Tailwind CDN used inline; no build step)
```

---

### Backend

#### [NEW] app.py

- **Flask Routes:**
  - `GET /` → serve `index.html`
  - `POST /process` → accept Excel/CSV upload, trigger async processing via `threading.Thread`; returns `{"status": "processing", "job_id": ...}`
  - `GET /progress/<job_id>` → returns `{"percent": 0-100, "done": bool}`
  - `GET /download/<job_id>` → streams the `Cleaned_Data.xlsx` output file

- **Email Validation (`validate_email_entry`):**
  1. Regex check: `^[\w.+-]+@[\w-]+\.[\w.]+$`
  2. DNS MX lookup via `dns.resolver.resolve(domain, 'MX')` using `dnspython`
  3. Returns `"Valid"` / `"Invalid Format"` / `"No MX Record"`

- **Phone Formatter (`clean_phone`):**
  - Strip all non-numeric characters (spaces, dashes, brackets, `+`)
  - Gulf country code map:
    ```
    Saudi Arabia → +966 (local prefix: 05x → 966 5x)
    UAE          → +971 (local prefix: 05x → 971 5x)
    Kuwait       → +965 (local prefix: 0x  → 965 x)
    Qatar        → +974
    Bahrain      → +973
    Oman         → +968
    Jordan       → +962
    ```
  - Auto-detect by existing country code prefix (966xx, 971xx, etc.)
  - Convert `05XXXXXXXX` → `+966 5XXXXXXXX` (Saudi default if no code)
  - Country is inferred from detected code and stored in result

- **Threading:**
  - Each upload spawns a `threading.Thread`
  - Progress is updated atomically via a shared `job_store` dict (in-memory)
  - Rows processed per-row with progress % increments

- **Export:**
  - Output DataFrame saved to `Cleaned_Data.xlsx` using `openpyxl`

#### [NEW] requirements.txt
```
flask
pandas
openpyxl
dnspython
```

---

### Frontend

#### [NEW] templates/index.html

- **Styling:** Tailwind CSS via CDN (`play.tailwindcss.com` script tag — no build needed)
- **Layout:**
  - Fixed left sidebar (dark, icon + label: Home, Settings, History)
  - Main content area with top header bar
- **Upload Zone:**
  - Dashed drag-and-drop box with animated icon
  - `<input type="file">` hidden, triggered on click/drop
  - Shows selected filename after pick
- **Progress Bar:**
  - Real-time JS polling (`setInterval → fetch /progress/<job_id>`) every 800ms
  - Animated colored bar fills on progress
- **Summary Cards (4):**
  - Total Records, Valid Emails, Invalid Emails, Cleaned Phones
  - Shown after processing completes
- **Results Table:**
  - Columns: #, Email, Email Status, Phone (Cleaned), Country
  - Color-coded status badges (green=Valid, red=Invalid/No MX)
  - Rendered from JSON response
- **Download Button:**
  - Appears after processing, links to `/download/<job_id>`

---

## Verification Plan

### Manual Testing (Browser)
1. Run: `python app.py` from the project directory
2. Open browser at `http://127.0.0.1:5000`
3. Drag & drop (or click to upload) a sample Excel file with columns: `Email`, `Phone`
4. Verify the progress bar animates in real time
5. Verify Summary Cards show correct totals
6. Verify Results Table populates with Email Status and cleaned Phone + Country
7. Click **Download** → confirm `Cleaned_Data.xlsx` downloads with correct data

### Sample Test Data
A small inline test dataset will be used (no real file needed for quick demo):
| Email | Phone |
|-------|-------|
| user@gmail.com | 0501234567 |
| bad-email | 00971501234567 |
| test@nonexistentdomain123.xyz | +965 9876543 |
