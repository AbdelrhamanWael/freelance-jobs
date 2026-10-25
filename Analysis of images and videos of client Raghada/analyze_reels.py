import os
import re
import time
import json
import threading
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.genai.errors import APIError

# ============================================================
# 1. API KEYS — each thread gets its own dedicated key
# ============================================================
API_KEYS = [
    "AQ.Ab8RN6Knc0bMri3sVs_vIUJ3cVb-wjrL_vlK-bpsnUrfGwLeNQ",
    "AQ.Ab8RN6KKzfZsy7aVFMBI58NOTN8cUFd-1Aqetg_0uTxK2B97Nw",
    "AQ.Ab8RN6LLFbKVCRVfwtM8C0HWjL4h8TrKU1vP__5wxW8lT0Qoyw",
    "AQ.Ab8RN6JSbwjBU2Nft5I95iyVvYcZnwDJMnSX-PL3OwYEmpaWrA"
]
MODEL_NAME = 'gemini-3.8-flash'
MAX_WORKERS           = 4   # one worker per API key
MAX_RETRIES           = 12  # max retries per video (handles long 503 storms)
RPM_WAIT              = 35  # seconds to wait when rate-limited
MAX_429_BEFORE_SWITCH = 2   # switch key after this many consecutive 429s

# ============================================================
# 2. Pydantic schema
# ============================================================
class AcademicMediaAnalysis(BaseModel):
    spoken_transcript:           str       = Field(description="تفريغ النص المسموع بالكامل داخل الفيديو، أو أي نص مكتوب يظهر على الشاشة")
    main_topics:                 list[str] = Field(description="الموضوعات الرئيسية المتناولة في المقطع (مثل السياسة، التكنولوجيا، الاقتصاد)")
    mentioned_countries:         list[str] = Field(description="الدول أو النطاقات الجغرافية المذكورة صراحة")
    characters_present:          list[str] = Field(description="الشخصيات الظاهرة أو المذكورة (مثل: مسئولين، مواطنين، رياضيين)")
    communication_strategy:      str       = Field(description="تصنيف استراتيجية الاتصال: إعلام، إقناع، بناء إجماع، أو حوار")
    cultural_interpreter_tactics:str       = Field(description="تكتيكات المترجم الثقافي: استخدام رموز مألوفة، أبطال، فكاهة، أو طقوس وعادات")
    ideological_discourse:       str       = Field(description="استراتيجيات الخطاب: التأكيد على إيجابيات الذات، التركيز على سلبيات الآخر، التبرير، إلخ")
    body_language:               str       = Field(description="تحليل لغة الجسد والانفعالات البصرية للمتحدثين")

# ============================================================
# 3. Helpers
# ============================================================
print_lock   = threading.Lock()
results_lock = threading.Lock()

def log(msg: str, prefix: str = ""):
    with print_lock:
        print(f"{prefix}{msg}", flush=True)

def format_for_excel(item: dict) -> dict:
    """Convert Python lists → Arabic comma-separated strings for clean Excel output."""
    out = {}
    for k, v in item.items():
        if isinstance(v, list):
            out[k] = "، ".join(str(x) for x in v if x)
        else:
            out[k] = v
    return out

def save_excel(results: list, output_folder: str, folder_name: str, df_original: pd.DataFrame):
    """Save/overwrite the Excel file with all results collected so far."""
    if not results:
        return
    formatted = [format_for_excel(r) for r in results]
    df = pd.DataFrame(formatted)

    original_cols = list(df_original.columns)
    ai_cols = [
        'File_Name', 'spoken_transcript', 'main_topics', 'mentioned_countries',
        'characters_present', 'communication_strategy', 'cultural_interpreter_tactics',
        'ideological_discourse', 'body_language'
    ]
    final_cols = [c for c in original_cols if c in df.columns]
    for c in ai_cols:
        if c not in final_cols and c in df.columns:
            final_cols.append(c)
    for c in df.columns:
        if c not in final_cols:
            final_cols.append(c)

    df = df[final_cols]
    path = os.path.join(output_folder, f"{folder_name}_Analysis.xlsx")
    df.to_excel(path, index=False)

# ============================================================
# 4. Per-video worker  (runs in its own thread with its own key)
# ============================================================
def analyse_file(task: dict) -> dict | None:
    """
    task keys:
        file_name, file_path, json_output_path, row_data,
        key_idx, folder_name, idx, total
    Returns the merged analysis dict on success, None on failure.
    """
    file_name        = task["file_name"]
    file_path        = task["file_path"]
    json_output_path = task["json_output_path"]
    row_data         = task["row_data"]
    key_idx          = task["key_idx"]
    idx              = task["idx"]
    total            = task["total"]
    folder_name      = task["folder_name"]
    prefix           = f"  [KEY-{key_idx+1}][{idx}/{total}] "

    # ---------- already done? ----------
    if os.path.exists(json_output_path):
        log(f"✔ {file_name} — skipped (already analysed)", prefix)
        with open(json_output_path, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        saved.update(row_data)
        return saved

    log(f"▶ Starting {file_name}", prefix)
    t0     = time.time()
    client = genai.Client(api_key=API_KEYS[key_idx])

    uploaded_file = None
    consecutive_429 = 0

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # --- upload (only once per video, re-upload if key switched) ---
            if uploaded_file is None:
                log(f"↑ Uploading {file_name} (using KEY-{key_idx+1})…", prefix)
                client = genai.Client(api_key=API_KEYS[key_idx])
                uploaded_file = client.files.upload(file=file_path)
                while uploaded_file.state.name == "PROCESSING":
                    time.sleep(2)
                    uploaded_file = client.files.get(name=uploaded_file.name)
                if uploaded_file.state.name == "FAILED":
                    log(f"❌ Upload FAILED for {file_name}", prefix)
                    return None
                log(f"✓ Upload ready for {file_name}", prefix)

            # --- build prompt ---
            post_text = row_data.get('Post Text', '')
            prompt = (
                "شاهد هذا المقطع (أو الصورة) بدقة واستمع إلى الحوار المنطوق إن وجد. "
                "قم بتفريغ الصوت وتحليل العناصر البصرية استناداً إلى الهيكل الأكاديمي المحدد.\n\n"
                f"هذا هو النص المرفق مع المنشور (Caption) لمساعدتك في فهم السياق:\n{post_text}"
            )

            # --- generate ---
            log(f"⚙ Generating analysis for {file_name} (attempt {attempt}, KEY-{key_idx+1})…", prefix)
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AcademicMediaAnalysis,
                ),
            )

            data = json.loads(resp.text)
            data['File_Name'] = file_name
            data.update(row_data)

            # --- save JSON checkpoint immediately ---
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            elapsed = time.time() - t0
            log(f"✅ Done {file_name} in {elapsed:.1f}s", prefix)
            # clean up uploaded file
            try:
                client.files.delete(name=uploaded_file.name)
            except:
                pass
            return data

        except APIError as e:
            if e.code == 429:
                consecutive_429 += 1
                if consecutive_429 >= MAX_429_BEFORE_SWITCH:
                    # Switch to next key
                    key_idx = (key_idx + 1) % len(API_KEYS)
                    log(f"⚠ 429 x{consecutive_429} — switching to KEY-{key_idx+1}", prefix)
                    consecutive_429 = 0
                    uploaded_file = None  # must re-upload with new key
                    time.sleep(5)
                else:
                    log(f"⚠ 429 rate-limit on KEY-{key_idx+1} — waiting {RPM_WAIT}s…", prefix)
                    time.sleep(RPM_WAIT)
            elif e.code == 503:
                consecutive_429 = 0
                wait = min(attempt * 10, 60)
                log(f"⚠ 503 server busy — waiting {wait}s (file still uploaded)…", prefix)
                time.sleep(wait)
            else:
                log(f"❌ API error {e.code} on {file_name}: {e}", prefix)
                break
        except Exception as e:
            es = str(e).lower()
            if "429" in es or "quota" in es or "exhausted" in es:
                consecutive_429 += 1
                if consecutive_429 >= MAX_429_BEFORE_SWITCH:
                    key_idx = (key_idx + 1) % len(API_KEYS)
                    log(f"⚠ 429 x{consecutive_429} — switching to KEY-{key_idx+1}", prefix)
                    consecutive_429 = 0
                    uploaded_file = None
                    time.sleep(5)
                else:
                    log(f"⚠ Quota/rate-limit — waiting {RPM_WAIT}s…", prefix)
                    time.sleep(RPM_WAIT)
            elif "503" in es or "high demand" in es:
                consecutive_429 = 0
                wait = min(attempt * 10, 60)
                log(f"⚠ 503 busy — waiting {wait}s…", prefix)
                time.sleep(wait)
            else:
                log(f"❌ Unexpected error on {file_name}: {e}", prefix)
                break

    log(f"💀 Giving up on {file_name} after {MAX_RETRIES} attempts", prefix)
    return None

# ============================================================
# 5. Folders to process
# ============================================================
folders_to_process = [
    {'folder': 'Chinese_Embassy_Reels',  'excel': 'Reels_Chinese_Embassy.xlsx',  'prefix': 'Reel_'},
    {'folder': 'US_Embassy_Reels',       'excel': 'Reels_US_Embassy.xlsx',        'prefix': 'Reel_'},
    {'folder': 'Excluded_Posts_Media',   'excel': 'Excluded_Posts_31.xlsx',       'prefix': 'Media_'},
]

# ============================================================
# 6. Main loop — one folder at a time, but files in parallel
# ============================================================
for item in folders_to_process:
    folder_name = item['folder']
    excel_file  = item['excel']
    file_prefix = item['prefix']

    if not os.path.exists(folder_name):
        print(f"\n⚠ Folder '{folder_name}' not found — skipping.")
        continue

    output_folder = folder_name.replace('_Reels', '_Analysis').replace('_Media', '_Analysis')
    os.makedirs(output_folder, exist_ok=True)

    # --- read Excel ---
    print(f"\n📂 Reading {excel_file}…")
    try:
        df_original = pd.read_excel(excel_file)
    except Exception as e:
        print(f"❌ Cannot read {excel_file}: {e}")
        continue

    valid_ext   = ('.mp4', '.jpg', '.jpeg', '.png')
    media_files = sorted([f for f in os.listdir(folder_name) if f.lower().endswith(valid_ext)])
    total       = len(media_files)

    print(f"📋 {folder_name}: {total} files to process with {MAX_WORKERS} parallel workers")
    print("=" * 60)

    # --- pre-load SAMPLE.xlsx if present (skip already analysed reels) ---
    sample_path = os.path.join(output_folder, f"{folder_name.replace('_Reels','_Reels')}_SAMPLE.xlsx")
    # Also check generic naming
    sample_candidates = [
        os.path.join(output_folder, f"{folder_name}_SAMPLE.xlsx"),
        os.path.join(output_folder, f"{folder_name.replace('_Reels','_Reels')}_SAMPLE.xlsx"),
        os.path.join(output_folder, "Chinese_Embassy_Reels_SAMPLE.xlsx"),
    ]
    preloaded_filenames = set()
    for sc in sample_candidates:
        if os.path.exists(sc):
            try:
                df_sample = pd.read_excel(sc)
                if 'File_Name' in df_sample.columns:
                    for _, row in df_sample.iterrows():
                        fn = str(row['File_Name']).strip()
                        fname_no_ext = os.path.splitext(fn)[0]
                        # Write a JSON checkpoint so the main loop skips it
                        jpath = os.path.join(output_folder, f"{fname_no_ext}.json")
                        if not os.path.exists(jpath):
                            row_dict = row.to_dict()
                            row_dict = {k: ("" if pd.isna(v) else v) for k, v in row_dict.items()}
                            with open(jpath, 'w', encoding='utf-8') as jf:
                                json.dump(row_dict, jf, ensure_ascii=False, indent=4)
                            preloaded_filenames.add(fn)
                print(f"ℹ Pre-loaded {len(preloaded_filenames)} reels from SAMPLE → no API calls for them!")
            except Exception as e:
                print(f"⚠ Could not read SAMPLE file {sc}: {e}")
            break  # only load the first match

    # --- build task list ---
    tasks = []
    for idx, file_name in enumerate(media_files, start=1):
        # map file number → Excel row (Reel_001 → row 0, Reel_002 → row 1, etc.)
        row_data = {}
        try:
            m = re.search(r'\d+', file_name)
            if m:
                row_idx = int(m.group()) - 1
                if 0 <= row_idx < len(df_original):
                    rd = df_original.iloc[row_idx].to_dict()
                    row_data = {k: ("" if pd.isna(v) else v) for k, v in rd.items()}
        except Exception as e:
            print(f"⚠ Could not map {file_name} to Excel row: {e}")

        tasks.append({
            "file_name":        file_name,
            "file_path":        os.path.join(folder_name, file_name),
            "json_output_path": os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}.json"),
            "row_data":         row_data,
            "key_idx":          (idx - 1) % MAX_WORKERS,   # round-robin key assignment
            "folder_name":      folder_name,
            "idx":              idx,
            "total":            total,
        })

    # --- parallel execution ---
    all_results = []
    completed   = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_task = {executor.submit(analyse_file, t): t for t in tasks}
        for future in as_completed(future_to_task):
            result = future.result()
            with results_lock:
                if result is not None:
                    all_results.append(result)
                completed += 1
                pct = (completed / total) * 100
                # Save Excel after every completed file
                save_excel(all_results, output_folder, folder_name, df_original)
                with print_lock:
                    print(f"\n📊 Progress: {completed}/{total} ({pct:.1f}%) — Excel updated.", flush=True)

    # --- final save ---
    save_excel(all_results, output_folder, folder_name, df_original)
    xlsx_path = os.path.join(output_folder, f"{folder_name}_Analysis.xlsx")
    print(f"\n✨ Folder '{folder_name}' complete! {len(all_results)} rows saved to:\n   {xlsx_path}")

print("\n🎉 ALL FOLDERS DONE!")