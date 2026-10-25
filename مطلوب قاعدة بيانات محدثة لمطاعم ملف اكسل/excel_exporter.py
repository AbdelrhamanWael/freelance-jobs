import sys
import re
import urllib.parse
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Common dummy, software libraries or spam emails to filter out
INVALID_EMAIL_PATTERNS = [
    r'wixpress\.com', r'sentry\.io', r'example\.com', r'domain\.com',
    r'noreply', r'no-reply', r'placeholder', r'user@', r'test@',
    r'bootstrap@', r'core@', r'@\d+\.\d+', r'webpack@', r'npm@', r'github\.com'
]

def clean_phone_number(raw_phone):
    """
    Standardize Saudi phone numbers to international format +966...
    Returns (standardized_phone, is_mobile)
    """
    if not raw_phone:
        return "", False

    # Remove all non-digits except leading +
    raw_str = str(raw_phone).strip()
    digits = re.sub(r'[^\d]', '', raw_str)

    if not digits:
        return "", False

    # Normalize Saudi numbers
    if digits.startswith("00966"):
        digits = digits[5:]
    elif digits.startswith("966"):
        digits = digits[3:]
    elif digits.startswith("0"):
        digits = digits[1:]

    # Check mobile (5xxxxxxxx) -> 9 digits
    if digits.startswith("5") and len(digits) == 9:
        return f"+966{digits}", True
    
    # Check Riyadh landline (11xxxxxxx) -> 9 digits
    if digits.startswith("11") and len(digits) == 9:
        return f"+966{digits}", False
    
    # Check other Saudi landlines (12, 13, 14, 16, 17) -> 9 digits
    if len(digits) == 9 and digits[0] == "1":
        return f"+966{digits}", False

    # Check Unified numbers 9200xxxxx (9 digits) or 800xxxxxxx
    if digits.startswith("9200") or digits.startswith("800"):
        return f"+966{digits}", False

    # Fallback to general representation if valid length
    if 7 <= len(digits) <= 12:
        return f"+966{digits}", digits.startswith("5")

    return raw_str, False


def generate_whatsapp_url(phone_number, is_mobile):
    """
    Generate direct WhatsApp click-to-chat URL for mobile numbers
    """
    if not phone_number or not is_mobile:
        return ""
    
    # Extract digits without plus
    digits = re.sub(r'[^\d]', '', phone_number)
    if digits.startswith("9665") and len(digits) == 12:
        return f"https://wa.me/{digits}"
    return ""


def validate_email(email):
    """
    Validate email address format and filter out placeholders/dummies.
    """
    if not email or not isinstance(email, str):
        return ""
    
    email = email.strip().lower()
    
    # Exclude image/asset false positives
    if email.endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif', '.js', '.css', '.woff', '.ttf')):
        return ""

    # Basic email regex
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(regex, email):
        return ""
    
    for pattern in INVALID_EMAIL_PATTERNS:
        if re.search(pattern, email):
            return ""
            
    return email


def scrape_email_from_website(website_url):
    """
    Quickly scrape public contact email from a restaurant website homepage
    """
    if not website_url or not isinstance(website_url, str):
        return ""
    
    url = website_url.strip()
    if not url.startswith("http"):
        url = "http://" + url

    # Skip social link aggregators that require login or don't host raw HTML
    skip_domains = ["instagram.com", "linktr.ee", "twitter.com", "x.com", "facebook.com", "tiktok.com", "snapchat.com", "yallaqrcodes.com", "tickets.bujairi.sa"]
    if any(d in url.lower() for d in skip_domains):
        return ""

    try:
        import requests
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        resp = requests.get(url, headers=headers, timeout=3)
        if resp.status_code == 200:
            text = resp.text
            # 1. Search for mailto: links first (highest confidence)
            mailto_matches = re.findall(r'mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', text, re.IGNORECASE)
            for m in mailto_matches:
                valid = validate_email(m)
                if valid:
                    return valid

            # 2. Search for general email regex in page text
            email_matches = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
            for m in email_matches:
                valid = validate_email(m)
                if valid:
                    return valid
    except Exception:
        pass

    return ""


def enrich_emails_from_websites(records, max_workers=25):
    """
    Concurrently enrich records with emails from their official websites
    """
    from concurrent.futures import ThreadPoolExecutor

    to_scrape = [r for r in records if not r.get("email") and r.get("website")]
    if not to_scrape:
        return records

    print(f"🔎 Scanning websites for emails across {len(to_scrape)} restaurants (concurrently with {max_workers} workers)...")

    def worker(r):
        email = scrape_email_from_website(r.get("website"))
        if email:
            r["email"] = email

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        list(executor.map(worker, to_scrape))

    enriched_count = len([r for r in records if r.get("email")])
    print(f"✨ Email enrichment finished! Total with verified email: {enriched_count}")
    return records



def extract_city_and_district(item, target_city=None):
    """
    Extract city and district from address or Google Maps details
    """
    address = item.get("address", "") or item.get("formatted_address", "") or ""
    neighborhood = item.get("neighborhood", "") or ""
    city = item.get("city", "") or target_city or "الرياض"

    # Known cities mapping
    address_lower = address.lower()
    if "الدرعية" in address or "diriyah" in address_lower:
        city = "الدرعية"
    elif "الخرج" in address or "al-kharj" in address_lower or "kharj" in address_lower:
        city = "الخرج"
    elif not city:
        city = "الرياض"

    # Known popular districts in Riyadh if neighborhood is empty
    if not neighborhood:
        riyadh_districts = [
            "العليا", "الملقا", "النخيل", "حطين", "الياسمين", "الصحافة", "المروج",
            "الملز", "الورود", "السليمانية", "الغدير", "الربيع", "الواحة", "الندى",
            "قرطبة", "اليرموك", "الروضة", "القدس", "الحمراء", "الريان", "النزهة",
            "المعذر", "الدرعية", "البجيري", "السيح"
        ]
        for dist in riyadh_districts:
            if dist in address:
                neighborhood = f"حي {dist}"
                break

    if not neighborhood:
        neighborhood = "غير محدد"

    return city, neighborhood


def deduplicate_records(records):
    """
    Remove duplicate restaurants based on placeId, phone, or name + city
    """
    seen_ids = set()
    seen_phones = set()
    seen_names = set()
    unique_records = []

    for r in records:
        place_id = r.get("placeId") or r.get("cid") or ""
        phone = r.get("phone", "")
        name = (r.get("title") or r.get("name") or "").strip().lower()
        city = r.get("city", "")

        # Key for name + city
        name_key = f"{name}_{city}"

        if place_id and place_id in seen_ids:
            continue
        if phone and phone in seen_phones:
            continue
        if name and name_key in seen_names:
            continue

        if place_id:
            seen_ids.add(place_id)
        if phone:
            seen_phones.add(phone)
        if name:
            seen_names.add(name_key)

        unique_records.append(r)

    return unique_records


def build_excel_database(cleaned_data, output_file_path):
    """
    Build a multi-sheet, beautifully styled Arabic Excel file (.xlsx)
    using openpyxl with full RTL support and executive styling.
    """
    wb = Workbook()
    
    # Styles Definition
    navy_header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    
    regular_font = Font(name="Calibri", size=10)
    bold_font = Font(name="Calibri", size=10, bold=True)
    link_font = Font(name="Calibri", size=10, color="0000FF", underline="single")
    
    zebra_even_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    zebra_odd_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    
    thin_border = Border(
        left=Side(style='thin', color='E5E7EB'),
        right=Side(style='thin', color='E5E7EB'),
        top=Side(style='thin', color='E5E7EB'),
        bottom=Side(style='thin', color='E5E7EB')
    )
    
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=False)
    right_align = Alignment(horizontal="right", vertical="center", wrap_text=False)
    
    headers = [
        "اسم المطعم",
        "التصنيف / المطبخ",
        "المدينة",
        "الحي",
        "رقم التواصل",
        "رابط واتساب المباشر",
        "البريد الإلكتروني",
        "رابط خرائط جوجل",
        "العنوان المباشر",
        "التقييم",
        "عدد التقييمات",
        "الموقع الإلكتروني"
    ]

    # Data sheets configuration
    sheets_config = [
        ("جميع المطاعم", cleaned_data),
        ("الرياض", [r for r in cleaned_data if "الرياض" in r["city"]]),
        ("الدرعية", [r for r in cleaned_data if "الدرعية" in r["city"]]),
        ("الخرج", [r for r in cleaned_data if "الخرج" in r["city"]])
    ]

    # Remove default sheet
    default_sheet = wb.active

    for sheet_title, records in sheets_config:
        ws = wb.create_sheet(title=sheet_title)
        
        # Enable Right-to-Left (RTL)
        ws.views.sheetView[0].rightToLeft = True
        
        # Write Headers
        ws.append(headers)
        header_row = ws[1]
        for cell in header_row:
            cell.fill = navy_header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = thin_border
        ws.row_dimensions[1].height = 28

        # Write Data
        for row_idx, r in enumerate(records, start=2):
            row_data = [
                r.get("name", ""),
                r.get("category", ""),
                r.get("city", ""),
                r.get("district", ""),
                r.get("phone", ""),
                r.get("whatsapp_url", ""),
                r.get("email", ""),
                r.get("google_maps_url", ""),
                r.get("address", ""),
                r.get("rating", ""),
                r.get("reviews_count", ""),
                r.get("website", "")
            ]
            ws.append(row_data)
            
            fill = zebra_odd_fill if row_idx % 2 == 1 else zebra_even_fill
            ws.row_dimensions[row_idx].height = 22

            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.fill = fill
                cell.border = thin_border
                cell.font = regular_font
                
                # Alignments and links
                # Name & Category & Address -> Right Align
                if col_idx in (1, 2, 9):
                    cell.alignment = right_align
                else:
                    cell.alignment = center_align

                # Clickable WhatsApp Link
                if col_idx == 6 and cell.value and cell.value.startswith("http"):
                    val = cell.value
                    cell.value = "مراسلة واتساب"
                    cell.hyperlink = val
                    cell.font = link_font

                # Clickable Google Maps Link
                if col_idx == 8 and cell.value and cell.value.startswith("http"):
                    val = cell.value
                    cell.value = "عرض على الخريطة"
                    cell.hyperlink = val
                    cell.font = link_font

                # Clickable Website
                if col_idx == 12 and cell.value and cell.value.startswith("http"):
                    val = cell.value
                    cell.value = "زيارة الموقع"
                    cell.hyperlink = val
                    cell.font = link_font

        # Auto-fit column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if cell.hyperlink:
                    val_str = "مراسلة واتساب"
                max_len = max(max_len, len(val_str))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

        # Freeze top header row
        ws.freeze_panes = "A2"
        # Auto-filter
        if records:
            last_col_letter = get_column_letter(len(headers))
            ws.auto_filter.ref = f"A1:{last_col_letter}{len(records) + 1}"

    # Create Summary Sheet
    ws_summary = wb.create_sheet(title="الملخص والإحصائيات", index=0)
    ws_summary.views.sheetView[0].rightToLeft = True
    
    # Title Banner
    ws_summary.merge_cells("A1:D2")
    title_cell = ws_summary["A1"]
    title_cell.value = "📊 ملخص قاعدة بيانات مطاعم الرياض والدرعية والخرج"
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    title_cell.fill = navy_header_fill
    title_cell.alignment = center_align
    
    total_count = len(cleaned_data)
    riyadh_count = len([r for r in cleaned_data if "الرياض" in r["city"]])
    diriyah_count = len([r for r in cleaned_data if "الدرعية" in r["city"]])
    kharj_count = len([r for r in cleaned_data if "الخرج" in r["city"]])
    with_phone = len([r for r in cleaned_data if r.get("phone")])
    with_whatsapp = len([r for r in cleaned_data if r.get("whatsapp_url")])
    with_email = len([r for r in cleaned_data if r.get("email")])

    summary_rows = [
        ("إجمالي عدد المطاعم المعتمدة", total_count),
        ("مطاعم مدينة الرياض", riyadh_count),
        ("مطاعم محافظة الدرعية", diriyah_count),
        ("مطاعم محافظة الخرج", kharj_count),
        ("المطاعم المزودة بأرقام تواصل معتمدة", f"{with_phone} ({round(with_phone/max(total_count,1)*100, 1)}%)"),
        ("المطاعم الداعمة للواتساب المباشر", f"{with_whatsapp} ({round(with_whatsapp/max(total_count,1)*100, 1)}%)"),
        ("المطاعم المزودة ببريد إلكتروني رسمي", f"{with_email} ({round(with_email/max(total_count,1)*100, 1)}%)"),
    ]

    ws_summary["A4"] = "المؤشر"
    ws_summary["B4"] = "القيمة"
    for cell in (ws_summary["A4"], ws_summary["B4"]):
        cell.font = header_font
        cell.fill = navy_header_fill
        cell.alignment = center_align
        cell.border = thin_border
    ws_summary.row_dimensions[4].height = 25

    for idx, (metric, val) in enumerate(summary_rows, start=5):
        c1 = ws_summary[f"A{idx}"]
        c2 = ws_summary[f"B{idx}"]
        c1.value = metric
        c2.value = val
        c1.font = bold_font
        c2.font = regular_font
        c1.alignment = right_align
        c2.alignment = center_align
        c1.border = thin_border
        c2.border = thin_border
        c1.fill = zebra_odd_fill if idx % 2 == 1 else zebra_even_fill
        c2.fill = zebra_odd_fill if idx % 2 == 1 else zebra_even_fill
        ws_summary.row_dimensions[idx].height = 22

    ws_summary.column_dimensions["A"].width = 38
    ws_summary.column_dimensions["B"].width = 25

    # Remove the initial default empty sheet
    wb.remove(default_sheet)

    wb.save(output_file_path)
    print(f"✅ Excel database created successfully at: {output_file_path}")
