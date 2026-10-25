import os
import re
import uuid
import threading
import time
import io
import sqlite3
import datetime

import pandas as pd
import dns.resolver
from flask import Flask, request, jsonify, render_template, send_file, g

app = Flask(__name__)
app.secret_key = "gulf_data_filter_secret_2024"

# ─── SQLite Integration ────────────────────────────────────────────────────────
DATABASE = 'data.db'
EXPORTS_DIR = 'Exports'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                filename TEXT,
                status TEXT,
                percent INTEGER DEFAULT 0,
                total INTEGER DEFAULT 0,
                valid INTEGER DEFAULT 0,
                invalid INTEGER DEFAULT 0,
                cleaned_phones INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        db.commit()

# Initialize DB on startup
if not os.path.exists(DATABASE):
    init_db()
elif os.path.getsize(DATABASE) == 0:
    init_db()
# Ensure table exists just in case
init_db()

def init_trial():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT value FROM settings WHERE key="expiry_date"')
        row = cursor.fetchone()
        if not row:
            # Set expiry to 24 hours from now
            expiry = (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat()
            cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?)', ('expiry_date', expiry))
            db.commit()

init_trial()

def check_validity():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT value FROM settings WHERE key="expiry_date"')
        row = cursor.fetchone()
        if row:
            expiry_date = datetime.datetime.fromisoformat(row['value'])
            if datetime.datetime.now() > expiry_date:
                return False
    except Exception:
        pass
    return True

@app.before_request
def limit_trial():
    if not check_validity():
        return "انتهت صلاحية النسخة التجريبية. يرجى شراء الخدمة للحصول على النسخة الكاملة.", 403

# ─── Gulf Country Code Map ─────────────────────────────────────────────────────
GULF_CODES = {
    "966": "Saudi Arabia",
    "971": "UAE",
    "965": "Kuwait",
    "974": "Qatar",
    "973": "Bahrain",
    "968": "Oman",
    "962": "Jordan",
}

# Local mobile prefixes that hint at Saudi (default fallback) for 05x numbers
GULF_LOCAL_PREFIXES = {
    "966": ("05", "5"),   # Saudi
    "971": ("05", "5"),   # UAE
    "965": ("0", ""),     # Kuwait 8-digit local
    "974": ("0", ""),     # Qatar
    "973": ("0", ""),     # Bahrain
    "968": ("0", ""),     # Oman
    "962": ("0", ""),     # Jordan
}


# ─────────────────────────────────────────────────────────────────────────────
#  EMAIL VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
_EMAIL_RE = re.compile(r"^[\w.+\-]+@[\w\-]+\.[\w.]+$")

def validate_email_entry(email: str, timeout: int = 5) -> str:
    """Returns 'Valid', 'Invalid Format', or 'No MX Record'."""
    email = str(email).strip()
    if not _EMAIL_RE.match(email):
        return "Invalid Format"
    domain = email.split("@", 1)[1]
    try:
        dns.resolver.resolve(domain, "MX", lifetime=timeout)
        return "Valid"
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return "No MX Record"
    except Exception:
        return "No MX Record"


# ─────────────────────────────────────────────────────────────────────────────
#  PHONE FORMATTING
# ─────────────────────────────────────────────────────────────────────────────
def clean_phone(raw: str, default_country_code: str = "966") -> tuple[str, str]:
    """
    Returns (formatted_phone, country_name).
    Strips non-numeric chars, detects Gulf country code, formats to +XXX XXXXXXXXX.
    """
    raw = str(raw).strip()
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", raw)

    if not digits:
        return ("—", "Unknown")

    # Remove leading double-zero (international prefix alternative: 00966...)
    if digits.startswith("00"):
        digits = digits[2:]

    # --- detect by existing country code prefix ---
    for code in sorted(GULF_CODES.keys(), key=len, reverse=True):
        if digits.startswith(code):
            country = GULF_CODES[code]
            number = digits[len(code):]
            return (f"+{code} {number}", country)

    # --- convert local format ---
    code = default_country_code
    country = GULF_CODES.get(code, "Unknown")

    if code in ("966", "971"):
        # Expect 05XXXXXXXX  (10 digits local) → strip leading 0 → 5XXXXXXXX
        if digits.startswith("05") and len(digits) >= 10:
            number = digits[1:]  # drop leading 0
            return (f"+{code} {number}", country)
        if digits.startswith("5") and len(digits) >= 9:
            return (f"+{code} {digits}", country)
    else:
        # Kuwait, Qatar, Bahrain, Oman, Jordan: strip leading 0
        if digits.startswith("0"):
            digits = digits[1:]
        return (f"+{code} {digits}", country)

    # Fallback: just prefix with country code
    return (f"+{code} {digits}", country)


# ─────────────────────────────────────────────────────────────────────────────
#  PROCESSING WORKER (runs in background thread)
# ─────────────────────────────────────────────────────────────────────────────
def update_job_status(job_id, status, percent=0, total=0, valid=0, invalid=0, cleaned_phones=0, error_message=None):
    try:
        # Each thread gets its own db connection
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE jobs 
            SET status=?, percent=?, total=?, valid=?, invalid=?, cleaned_phones=?, error_message=?
            WHERE id=?
        ''', (status, percent, total, valid, invalid, cleaned_phones, error_message, job_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating job {job_id}: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def process_file(job_id: str, files_list: list, default_cc: str, dns_timeout: int = 5):
    """Read the uploaded files, detect columns dynamically, process data."""
    try:
        all_dfs = []
        for file_bytes, filename in files_list:
            ext = os.path.splitext(filename)[1].lower()
            buf = io.BytesIO(file_bytes)

            try:
                # Read without headers to avoid skipping row 1 if headers are absent
                if ext in (".xlsx", ".xls"):
                    df = pd.read_excel(buf, header=None)
                elif ext == ".csv":
                    df = pd.read_csv(buf, header=None)
                else:
                    continue
            except Exception as e:
                print(f"Failed parsing file: {e}")
                continue
            
            if df.empty:
                continue

            email_col = None
            phone_col = None
            
            # Smart column detection (up to 20 rows of inspection)
            for col_idx in df.columns:
                sample_values = df[col_idx].head(20).astype(str).tolist()
                col_header = sample_values[0].lower().strip() if len(sample_values) > 0 else ""
                
                # Check Header 
                is_email = any(word in col_header for word in ["email", "e-mail", "بريد", "ايميل", "إيميل"])
                is_phone = any(word in col_header for word in ["phone", "mobile", "رقم", "هاتف", "جوال"])

                # Value inspection fallback
                if not is_email and not email_col:
                    matches = sum(1 for v in sample_values if "@" in v and "." in v and len(v) > 5)
                    if matches >= min(3, len([v for v in sample_values if v.strip() != "nan"])):
                        is_email = True
                
                if not is_phone and not phone_col:
                    matches = sum(1 for v in sample_values if len(re.sub(r"\D", "", v)) >= 7)
                    if matches >= min(3, len([v for v in sample_values if v.strip() != "nan"])):
                        is_phone = True

                if is_email and email_col is None:
                    email_col = col_idx
                if is_phone and phone_col is None:
                    phone_col = col_idx

            temp_df = pd.DataFrame()
            temp_df["mapped_email"] = df[email_col] if email_col is not None else ""
            temp_df["mapped_phone"] = df[phone_col] if phone_col is not None else ""

            # If headers were detected in row 0, we can drop row 0.
            # But just leaving it is safer unless it exactly matches 'email' or 'phone' etc.
            # We'll just let the validation handle invalid headers.
            
            all_dfs.append(temp_df)

        if not all_dfs:
            update_job_status(job_id, 'Error', error_message="No valid data or columns (Email/Phone) found in files.")
            return

        combined_df = pd.concat(all_dfs, ignore_index=True)
        total = len(combined_df)
        rows = []
        valid_count = 0
        invalid_count = 0
        cleaned_phone_count = 0
        processed_records = 0

        # We will bulk update UI every 50 records to not spam sqlite
        for i, (_, row) in enumerate(combined_df.iterrows()):
            if processed_records >= 100:
                break

            email_val = str(row["mapped_email"]).strip() if pd.notna(row.get("mapped_email")) else ""
            phone_val = str(row["mapped_phone"]).strip() if pd.notna(row.get("mapped_phone")) else ""
            
            if email_val == "nan": email_val = ""
            if phone_val == "nan": phone_val = ""

            # Skip fully empty rows
            if not email_val and not phone_val:
                continue

            # Skip header rows from being processed as data
            if email_val.lower() in ("email", "e-mail", "بريد", "ايميل", "إيميل") or \
               phone_val.lower() in ("phone", "mobile", "رقم", "هاتف", "جوال"):
                continue

            processed_records += 1

            # Email
            email_status = validate_email_entry(email_val, dns_timeout) if email_val else "—"
            if email_status == "Valid":
                valid_count += 1
            elif email_status in ("Invalid Format", "No MX Record"):
                invalid_count += 1

            # Phone
            cleaned_ph, country = ("—", "—")
            if phone_val:
                cleaned_ph, country = clean_phone(phone_val, default_cc)
                if cleaned_ph != "—":
                    cleaned_phone_count += 1

            rows.append({
                "Email": email_val or "—",
                "Email Status": email_status,
                "Phone (Cleaned)": cleaned_ph,
                "Country": country,
            })

            if i % 50 == 0:
                percent = int(((i + 1) / total) * 100)
                update_job_status(job_id, 'Processing', percent=percent, total=len(rows))

        # Build output DataFrame
        if not rows:
            out_df = pd.DataFrame(columns=["Email", "Email Status", "Phone (Cleaned)", "Country"])
        else:
            out_df = pd.DataFrame(rows)
            
            # Dynamic Column Removal (Remove columns if they only contain '—')
            has_emails = not all(out_df["Email"] == "—")
            has_phones = not all(out_df["Phone (Cleaned)"] == "—")

            columns_to_keep = []
            if has_emails:
                columns_to_keep.extend(["Email", "Email Status"])
            if has_phones:
                columns_to_keep.extend(["Phone (Cleaned)", "Country"])
                
            # Fallback if both somehow missing but rows exist (shouldn't happen)
            if not columns_to_keep:
                columns_to_keep = ["Email", "Email Status", "Phone (Cleaned)", "Country"]
                
            out_df = out_df[columns_to_keep]

        # Output to directory
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        export_path = os.path.join(EXPORTS_DIR, f"Cleaned_Data_{job_id}.xlsx")
        
        with pd.ExcelWriter(export_path, engine="openpyxl") as writer:
            out_df.to_excel(writer, index=False, sheet_name="Cleaned Data")

        # Job Finished
        update_job_status(
            job_id, 
            status='Completed', 
            percent=100, 
            total=len(rows), 
            valid=valid_count, 
            invalid=invalid_count, 
            cleaned_phones=cleaned_phone_count
        )

    except Exception as e:
        update_job_status(job_id, 'Error', error_message=str(e))


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    if "file" not in request.files:
        return jsonify({"error": "No files uploaded."}), 400

    uploaded_files = request.files.getlist("file")
    if not uploaded_files or all(f.filename == "" for f in uploaded_files):
        return jsonify({"error": "Empty files."}), 400

    default_cc = request.form.get("country_code", "966")
    try:
        dns_timeout = int(request.form.get("dns_timeout", 5))
    except ValueError:
        dns_timeout = 5

    files_list = []
    compound_filename = ""
    for f in uploaded_files:
        if f.filename:
            files_list.append((f.read(), f.filename))
            compound_filename += f.filename + ", "
    
    if compound_filename.endswith(", "):
        compound_filename = compound_filename[:-2]

    job_id = str(uuid.uuid4())
    
    # Insert new job to SQLite
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO jobs (id, filename, status, percent)
        VALUES (?, ?, ?, ?)
    ''', (job_id, compound_filename, 'Processing', 0))
    db.commit()

    t = threading.Thread(
        target=process_file,
        args=(job_id, files_list, default_cc, dns_timeout),
        daemon=True,
    )
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/progress/<job_id>")
def progress(job_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM jobs WHERE id=?', (job_id,))
    row = cursor.fetchone()
    
    if not row:
        return jsonify({"error": "Job not found."}), 404
        
    job = dict(row)
    is_done = job['status'] in ('Completed', 'Error')
    
    # Send limited rows if it's done for the UI preview
    rows_preview = []
    if is_done and job['status'] == 'Completed':
        export_path = os.path.join(EXPORTS_DIR, f"Cleaned_Data_{job_id}.xlsx")
        if os.path.exists(export_path):
            try:
                # read top 100 rows for ui
                df = pd.read_excel(export_path, nrows=100)
                # handle nan safely
                df = df.fillna(value="—")
                # format dictionary for UI matching old format
                for _, df_row in df.iterrows():
                    rows_preview.append({
                        "email": str(df_row.get("Email", "—")),
                        "email_status": str(df_row.get("Email Status", "—")),
                        "phone": str(df_row.get("Phone (Cleaned)", "—")),
                        "country": str(df_row.get("Country", "—")),
                    })
            except Exception:
                pass

    return jsonify({
        "percent": job["percent"],
        "done": is_done,
        "rows": rows_preview,
        "summary": {
            "total": job["total"],
            "valid": job["valid"],
            "invalid": job["invalid"],
            "cleaned_phones": job["cleaned_phones"],
        } if is_done else {},
        "error": job.get("error_message"),
    })

@app.route("/history")
def history():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM jobs ORDER BY created_at DESC LIMIT 50')
    rows = cursor.fetchall()
    
    jobs = []
    for r in rows:
        jobs.append(dict(r))
        
    return jsonify({"jobs": jobs})

@app.route("/download/<job_id>")
def download(job_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT status FROM jobs WHERE id=?', (job_id,))
    row = cursor.fetchone()
    
    if not row or row['status'] != 'Completed':
        return jsonify({"error": "File not ready."}), 404

    export_path = os.path.join(EXPORTS_DIR, f"Cleaned_Data_{job_id}.xlsx")
    if not os.path.exists(export_path):
         return jsonify({"error": "File was deleted or not found."}), 404

    export_filter = request.args.get("filter", "all")

    if export_filter == "valid":
        try:
            df = pd.read_excel(export_path)
            # Filter rows where Email Status is 'Valid'
            if "Email Status" in df.columns:
                df_valid = df[df["Email Status"] == "Valid"]
            else:
                # If there is no 'Email Status' column, returning an empty DataFrame with the same columns
                df_valid = df.iloc[0:0]
            
            output_buf = io.BytesIO()
            with pd.ExcelWriter(output_buf, engine="openpyxl") as writer:
                df_valid.to_excel(writer, index=False, sheet_name="Cleaned Data")
            output_buf.seek(0)
            
            return send_file(
                output_buf,
                as_attachment=True,
                download_name=f"Filtered_Valid_Only.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            return jsonify({"error": f"Error filtering file: {str(e)}"}), 500
    
    # Default: Export All
    return send_file(
        export_path,
        as_attachment=True,
        download_name=f"Filtered_Data.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

import webbrowser
from threading import Timer

if __name__ == "__main__":
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000/")
    
    # Wait 1.5 seconds for the server to start before opening the browser
    Timer(1.5, open_browser).start()
    
    app.run(debug=False, port=5000)
