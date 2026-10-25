import asyncio
import re
import os
import random
import sys
import pandas as pd
from telethon import TelegramClient, errors
from datetime import datetime, timedelta, timezone
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as OpenpyxlImage
from openpyxl.worksheet.datavalidation import DataValidation
from PIL import Image as PILImage

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

# 1. إعدادات تيليجرام
API_ID = "36389169"
API_HASH = '7f6203e401192c3e27067f87223b30ed'
PHONE = '+201016752893'

# القنوات المستهدفة
TARGET_CHATS = ['https://t.me/Almufakir', 'https://t.me/Elmonsefqudrat']

# 2. الكلمات المفتاحية المستهدفة لجمع أسئلة بنك الأسئلة والتسريبات الحقيقية فقط
# تم استبعاد "اختباري" و "اختبرت" المنفردة تماماً لمنع تدفق مئات السوالف الإدارية (متى النتايج، ادعولي...)
targeted_keywords = [
    "جاني",          # يغطي: جاني سؤال، جاني اليوم، جاني كمي، جاني لفظي...
    "جاه",           # يغطي: جاه سؤال، أحد جاه...
    "جاء في الاختبار",
    "نفس السؤال",
    "نفس السوال",
    "صيغة السؤال",
    "صيغة السوال",
    "سؤال المقارنة",
    "سؤال كمي",
    "سؤال لفظي",
    "تسريب",
    "تسريبات",
    "تكرر",
    "تكررت",
    "توي طالع",
    "توني طالع",
    "توي مخلص",
    "توني مخلص"
]

priority_keywords = [
    "اليوم", "توي", "قبل شوي", "توني", "الصباح", "المساء", 
    "الفترة الأولى", "الفترة الثانية", "توي طالع", "توني طالع", 
    "الآن", "الان", "تسريب", "تسريبات", "نفس السؤال", "تكرر"
]
priority_pattern = re.compile("|".join(priority_keywords), re.IGNORECASE)

# قائمة استبعاد السوالف الإدارية والدردشة العشوائية (Negative Filter)
ADMIN_CHATTER = [
    r"متى تطلع النتايج", r"متى تطلع النتيج", r"تطلع الدرجات", r"متى النتايج",
    r"ادعول[يى]", r"ادعو ل[يى]", r"دعواتكم", 
    r"احجز اختباري", r"حجزت اختباري", r"متى احجز", r"حجزت موعد",
    r"الساعه\s+[0-9]+|الساعة\s+[0-9]+",
    r"كيف اذاكر", r"وش اذاكر", r"ايش اذاكر", r"من وين اذاكر",
    r"افضل مدرس", r"مين افضل", r"افضل قناة", r"قروب قدرات",
    r"كم باقي على", r"باقي عليه\s+[0-9]+\s+ايام",
    r"عادي اكلم المشرفين", r"اشتراكي مقفل", r"فلوسي", r"الدفع",
    r"مميزات موقع", r"اضغط المشبك", r"قناتنا على", r"تابعونا", r"للاشتراك", r"كود الخصم"
]
admin_chatter_pattern = re.compile("|".join(ADMIN_CHATTER), re.IGNORECASE)

def normalize_text(text):
    """تنظيف وتوحيد النص لمنع التكرار تماماً"""
    if not text:
        return ""
    t = re.sub(r'[\r\n\t]+', ' ', text)
    t = re.sub(r'[^\w\s]', '', t)
    t = re.sub(r'[إأآا]', 'ا', t)
    t = re.sub(r'ة', 'ه', t)
    t = re.sub(r'ى', 'ي', t)
    return re.sub(r'\s+', ' ', t).strip().lower()

async def get_sender_name(message):
    """استخراج اسم المرسل أو لقبه بأمان"""
    try:
        sender = message.sender or await message.get_sender()
        if sender:
            if hasattr(sender, 'first_name') and sender.first_name:
                name = sender.first_name
                if hasattr(sender, 'last_name') and sender.last_name:
                    name += f" {sender.last_name}"
                return name.strip()
            elif hasattr(sender, 'title'):
                return sender.title.strip()
            elif hasattr(sender, 'username') and sender.username:
                return f"@{sender.username}"
    except Exception:
        pass
    return "طالب / مشارك"

async def get_sender_handle(message, chat_username):
    """استخراج رابط الحساب المباشر للطالب أو رابط رسالته"""
    try:
        sender = message.sender or await message.get_sender()
        if sender and hasattr(sender, 'username') and sender.username:
            return f"https://t.me/{sender.username}"
    except Exception:
        pass
    return f"https://t.me/{chat_username}/{message.id}"

async def extract_discussion_context(client, chat, message, parent_msg=None):
    """استخراج سياق النقاش الحقيقي: السؤال الأصلي + ردود وحلول وتأكيدات الطلاب"""
    context_parts = []
    
    # 1. السؤال الأصلي (لو كانت الرسالة رداً على سؤال سابق)
    if parent_msg:
        parent_sender = await get_sender_name(parent_msg)
        p_text = (parent_msg.text or parent_msg.message or "").strip()
        if not p_text and parent_msg.media:
            p_text = "[مرفق سؤال أصلي مصور]"
        elif not p_text:
            p_text = "[سؤال أصلي بدون نص]"
        context_parts.append(f"📌 [السؤال الأصلي من {parent_sender}]:\n{p_text}")

    # 2. حلول وردود الطلاب تحت هذا السؤال
    student_replies = []
    try:
        async for rep in client.iter_messages(chat, reply_to=message.id, limit=4):
            if rep.id == message.id:
                continue
            r_sender = await get_sender_name(rep)
            r_text = (rep.text or rep.message or "").strip()
            if not r_text and rep.photo:
                r_text = "[أرفق صورة توضيحية / حل]"
            if r_text:
                student_replies.append(f"💬 {r_sender}: {r_text}")
    except Exception:
        pass

    if student_replies:
        context_parts.append("👥 [حلول وتأكيدات الطلاب في النقاش]:\n" + "\n".join(student_replies))

    if context_parts:
        return "\n\n".join(context_parts)
    elif message.photo or (parent_msg and parent_msg.media):
        return "📷 [سؤال مصور معروض للمناقشة في القناة]"
    else:
        return "📝 [سؤال/تجربة اختبار مطروحة مباشرة في القناة]"

async def download_image_safe(client, media_msg, images_dir):
    """تحميل الصورة بأمان والتأكد من أنها صورة صالحة"""
    os.makedirs(images_dir, exist_ok=True)
    target_base = os.path.join(images_dir, f"msg_{media_msg.id}")
    
    # التحقق إن كانت محملة مسبقاً
    existing = [
        os.path.join(images_dir, f) for f in os.listdir(images_dir) 
        if f.startswith(f"msg_{media_msg.id}.")
    ]
    if existing:
        return existing[0]

    # فقط تحميل الصور والـ PDF وتجاهل المقاطع الصوتية
    if not (media_msg.photo or (media_msg.document and getattr(media_msg.document, 'mime_type', '').startswith('image/')) or (media_msg.document and getattr(media_msg.document, 'mime_type', '') == 'application/pdf')):
        return ""

    try:
        downloaded = await asyncio.wait_for(
            client.download_media(media_msg, file=target_base),
            timeout=25
        )
        if downloaded and os.path.exists(downloaded):
            ext = os.path.splitext(downloaded)[1].lower()
            if ext in ['.ogg', '.mp3', '.mp4', '.mov']:
                try:
                    os.remove(downloaded)
                except Exception:
                    pass
                return ""
            return downloaded
    except Exception:
        pass
    return ""

async def main():
    client = TelegramClient(
        'student_scraper_session',
        API_ID,
        API_HASH,
        flood_sleep_threshold=120
    )
    
    await client.start(phone=PHONE)
    print("✅ تم تسجيل الدخول إلى تيليجرام بنجاح.")
    
    # نافذة الرصد الصارمة: آخر 24 ساعة بالثانية
    now_utc = datetime.now(timezone.utc)
    time_threshold = now_utc - timedelta(hours=24)
    current_date_str = datetime.now().strftime('%Y-%m-%d_%H-%M')
    
    all_master_questions = []
    all_master_followup = []
    
    total_chats = len(TARGET_CHATS)
    for idx, chat in enumerate(TARGET_CHATS, 1):
        chat_username = chat.split('/')[-1]
        print(f"\n[{idx}/{total_chats}] 🚀 جاري رصد وتجميع بنك الأسئلة من: {chat_username}...")
        
        images_dir = os.path.join(chat_username, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        extracted_questions = []
        followup_students = []
        
        seen_msg_ids = set()
        seen_text_hashes = set()
        parent_cache = {}
        
        # -------------------------------------------------------------
        # المحرك الأول: صيد جميع الأسئلة المصورة (Photos & Question Cards)
        # -------------------------------------------------------------
        print(f"   📸 [المحرك الأول]: صيد وتجميع الأسئلة المصورة لآخر 24 ساعة...")
        photo_count = 0
        try:
            async for msg in client.iter_messages(chat, limit=800):
                msg_date_utc = msg.date if msg.date.tzinfo else msg.date.replace(tzinfo=timezone.utc)
                if msg_date_utc < time_threshold:
                    break
                
                # التحقق إن كانت الرسالة تحتوي على صورة سؤال
                is_photo_msg = msg.photo or (msg.document and getattr(msg.document, 'mime_type', '').startswith('image/'))
                if not is_photo_msg:
                    continue
                
                # استبعاد الرسائل الصادرة من البوتات والردود الآلية الترويجية
                sender = msg.sender or await msg.get_sender()
                sender_name = await get_sender_name(msg)
                if sender and getattr(sender, 'bot', False):
                    continue
                if any(b in sender_name for b in ["ردود", "بوت", "Bot", "bot", "المفكر", "المنصف"]):
                    if "ردود" in sender_name or "بوت" in sender_name:
                        continue
                
                raw_text = (msg.text or "").strip()
                
                # استبعاد الإعلانات التسويقية والسوالف الإدارية
                if admin_chatter_pattern.search(raw_text):
                    continue
                    
                norm_t = normalize_text(raw_text)
                if norm_t and norm_t in seen_text_hashes:
                    continue
                if norm_t:
                    seen_text_hashes.add(norm_t)
                seen_msg_ids.add(msg.id)
                
                # جلب السؤال الأصلي إن وجد
                parent_msg = None
                if msg.is_reply:
                    r_id = getattr(msg, 'reply_to_msg_id', None)
                    if r_id and r_id in parent_cache:
                        parent_msg = parent_cache[r_id]
                    else:
                        try:
                            parent_msg = await msg.get_reply_message()
                            if r_id:
                                parent_cache[r_id] = parent_msg
                        except Exception:
                            pass
                
                # تحميل صورة السؤال
                img_path = await download_image_safe(client, msg, images_dir)
                
                # استخراج سياق النقاش (السؤال + الحلول)
                ctx = await extract_discussion_context(client, chat, msg, parent_msg)
                
                # تحديد التصنيف بدقة
                is_priority = bool(priority_pattern.search(raw_text) or priority_pattern.search(ctx))
                category = "أولوية عالية" if is_priority else "حديث غير محدد"
                
                msg_link = f"https://t.me/{chat_username}/{msg.id}"
                msg_date = msg_date_utc.strftime("%Y-%m-%d %H:%M:%S")
                
                display_text = raw_text if raw_text else "[سؤال مصور من بنك الأسئلة / التجميعات]"
                
                extracted_questions.append({
                    "الكلمة المفتاحية": "سؤال مصور / تجميعات",
                    "التصنيف": category,
                    "اسم المرسل": sender_name,
                    "تاريخ ووقت الرسالة": msg_date,
                    "سكرين شوت": img_path if img_path else "لا توجد صورة",
                    "رابط الرسالة": msg_link,
                    "نص الرسالة (للمراجعة)": display_text,
                    "سياق النقاش": ctx
                })
                photo_count += 1
                if photo_count % 10 == 0:
                    print(f"      📥 تم اصطياد وتوثيق {photo_count} سؤالاً مصوراً...")
                    
        except Exception as e:
            print(f"   ⚠️ تنبيه أثناء صيد الأسئلة المصورة: {e}")

        print(f"   ✅ تم الانتهاء من صيد الأسئلة المصورة (الإجمالي: {photo_count} سؤال مصور).")
        
        # -------------------------------------------------------------
        # المحرك الثاني: صيد الأسئلة النصية الحقيقية والتسريبات والتأكيدات
        # -------------------------------------------------------------
        print(f"   🔎 [المحرك الثاني]: صيد الأسئلة النصية والتسريبات والتجارب المباشرة...")
        text_q_count = 0
        try:
            for kw_idx, kw in enumerate(targeted_keywords, 1):
                async for msg in client.iter_messages(chat, search=kw):
                    msg_date_utc = msg.date if msg.date.tzinfo else msg.date.replace(tzinfo=timezone.utc)
                    if msg_date_utc < time_threshold:
                        break
                        
                    if msg.id in seen_msg_ids:
                        continue
                    
                    # استبعاد الرسائل الصادرة من البوتات والردود الآلية
                    sender = msg.sender or await msg.get_sender()
                    sender_name = await get_sender_name(msg)
                    if sender and getattr(sender, 'bot', False):
                        continue
                    if any(b in sender_name for b in ["ردود", "بوت", "Bot", "bot", "المفكر", "المنصف"]):
                        if "ردود" in sender_name or "بوت" in sender_name:
                            continue

                    raw_text = (msg.text or "").strip()
                    if not raw_text and not msg.media:
                        continue
                        
                    # فلترة السوالف الإدارية (متى تطلع النتايج، ادعولي، إلخ)
                    if admin_chatter_pattern.search(raw_text):
                        continue
                        
                    norm_t = normalize_text(raw_text)
                    if norm_t and norm_t in seen_text_hashes:
                        continue

                    # جلب السؤال الأصلي في حال الرد
                    parent_msg = None
                    if msg.is_reply:
                        r_id = getattr(msg, 'reply_to_msg_id', None)
                        if r_id and r_id in parent_cache:
                            parent_msg = parent_cache[r_id]
                        else:
                            try:
                                parent_msg = await msg.get_reply_message()
                                if r_id:
                                    parent_cache[r_id] = parent_msg
                            except Exception:
                                pass
                    
                    # صيد صورة السؤال سواء أرفقها الطالب أو كانت في السؤال الأصلي
                    media_target = msg if msg.media else (parent_msg if parent_msg and parent_msg.media else None)
                    img_path = ""
                    if media_target:
                        img_path = await download_image_safe(client, media_target, images_dir)

                    # معيار جودة الأسئلة النصية: استبعاد الرسائل المبتورة المكونة من كلمة واحدة بدون صورة وبدون سياق
                    if not img_path and not (parent_msg and parent_msg.media):
                        if len(raw_text) < 15 or norm_t in [
                            "تسريبات", "شرح", "جاني", "جاه", "طريقة الحل", "بالله", 
                            "كيف الحل", "تسريبات المفكر", "تسريبات يلو", "تسريبات المنصف",
                            "نفس السؤال", "نفس السوال", "تكرر", "تكررت"
                        ]:
                            continue

                    if norm_t:
                        seen_text_hashes.add(norm_t)
                    seen_msg_ids.add(msg.id)
                    
                    ctx = await extract_discussion_context(client, chat, msg, parent_msg)
                    
                    is_priority = bool(priority_pattern.search(raw_text) or priority_pattern.search(ctx))
                    category = "أولوية عالية" if is_priority else "حديث غير محدد"
                    
                    msg_link = f"https://t.me/{chat_username}/{msg.id}"
                    msg_date = msg_date_utc.strftime("%Y-%m-%d %H:%M:%S")
                    
                    extracted_questions.append({
                        "الكلمة المفتاحية": kw,
                        "التصنيف": category,
                        "اسم المرسل": sender_name,
                        "تاريخ ووقت الرسالة": msg_date,
                        "سكرين شوت": img_path if img_path else "لا توجد صورة",
                        "رابط الرسالة": msg_link,
                        "نص الرسالة (للمراجعة)": raw_text if raw_text else "[مرفق بدون نص]",
                        "سياق النقاش": ctx
                    })
                    text_q_count += 1
                    
                    # رصد طلاب التواصل والمتابعة (الإكسل الثاني)
                    # الطلاب الذين ذكروا خروجهم من الاختبار أو أكدوا أسئلة اليوم
                    if any(w in raw_text for w in ["توي طالع", "توني طالع", "توي مخلص", "توني مخلص", "اختبرت اليوم وجاني", "جاني اليوم"]):
                        sender_link = await get_sender_handle(msg, chat_username)
                        followup_students.append({
                            "حالة التواصل (تم الرد / في الانتظار)": "في الانتظار",
                            "اسم الطالب": sender_name,
                            "رابط حساب الطالب أو رسالته": sender_link,
                            "رد الطالب (الأسئلة والتجربة)": raw_text,
                            "سكرين شوت للمحادثة": img_path if img_path else "لا توجد صورة",
                            "تاريخ الرسالة": msg_date
                        })
                        
                await asyncio.sleep(1.2)
                
        except errors.FloodWaitError as fwe:
            print(f"⚠️ طلب تيليجرام انتظاراً لمدة {fwe.seconds} ثانية...")
            await asyncio.sleep(fwe.seconds)
        except Exception as e:
            print(f"   ⚠️ خطأ أثناء البحث النصي: {e}")
            
        print(f"   ✅ تم الانتهاء من صيد الأسئلة النصية (الإجمالي: {text_q_count} سؤال).")
        
        # -------------------------------------------------------------
        # حفظ وتنسيق ملف الرصد: الاقتصار الصارم على الرسائل التي تحتوي على صور فقط
        # -------------------------------------------------------------
        extracted_questions = [
            q for q in extracted_questions 
            if q.get("سكرين شوت") and q.get("سكرين شوت") != "لا توجد صورة" and os.path.exists(q.get("سكرين شوت"))
        ]
        
        if extracted_questions:
            df_main = pd.DataFrame(extracted_questions).copy()
            category_order = ["أولوية عالية", "حديث غير محدد"]
            df_main['التصنيف'] = pd.Categorical(df_main['التصنيف'], categories=category_order, ordered=True)
            df_main = df_main.sort_values(by=['التصنيف', 'تاريخ ووقت الرسالة'], ascending=[True, False])
            
            report_file = os.path.join(chat_username, f"Report_{current_date_str}.xlsx")
            df_main.to_excel(report_file, index=False)
            format_main_excel(report_file)
            print(f"\n📊 تم حفظ تقرير {chat_username} (الرسائل المصورة فقط):")
            print(f"   📂 الملف: {report_file}")
            print(f"   📸 إجمالي الأسئلة المصورة: {len(df_main)} (أولوية عالية في الأعلى دائماً)\n")
        else:
            print(f"ℹ️ لم يتم العثور على رسائل مصورة لـ {chat_username} خلال الـ 24 ساعة الماضية.\n")

        all_master_questions.extend(extracted_questions)

        if idx < total_chats:
            delay = random.randint(8, 12)
            print(f"🕒 استراحة أمان لمدة {delay} ثانية قبل الانتقال إلى القناة التالية...")
            await asyncio.sleep(delay)

    # -------------------------------------------------------------
    # تحديث وتعبئة الملف المجمع الرئيسي للرصد المصور
    # -------------------------------------------------------------
    if all_master_questions:
        print("\n🏆 جاري تحديث ملف الرصد المباشر المجمع بالصور فقط...")
        populate_master_client_sheets(all_master_questions, [])

    await client.disconnect()
    print("✨ اكتملت مهمة بنك الأسئلة بالكامل وبأعلى دقة وجودة.")

def format_main_excel(file_path):
    """تنسيق ملف الرصد المباشر وإدراج مصغرات الصور وروابط المعاينة بجودة كاملة وسياق النقاش"""
    try:
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        ws.sheet_view.rightToLeft = True

        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        data_font = Font(name="Segoe UI", size=10, color="0F172A")
        placeholder_font = Font(name="Segoe UI", size=9, italic=True, color="94A3B8")
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")

        high_priority_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
        high_priority_font = Font(name="Segoe UI", size=10, bold=True, color="991B1B")

        normal_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        normal_font = Font(name="Segoe UI", size=10, color="334155")

        thin_border = Border(
            left=Side(style='thin', color="CBD5E1"),
            right=Side(style='thin', color="CBD5E1"),
            top=Side(style='thin', color="CBD5E1"),
            bottom=Side(style='thin', color="CBD5E1")
        )

        align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)

        ws.row_dimensions[1].height = 32
        headers = [ws.cell(1, col).value for col in range(1, ws.max_column + 1)]

        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(1, col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_center
            cell.border = thin_border

        for r in range(2, ws.max_row + 1):
            ws.row_dimensions[r].height = 60
            for c in range(1, ws.max_column + 1):
                cell = ws.cell(r, c)
                cell.border = thin_border
                cell.font = data_font
                h_name = headers[c - 1] if c - 1 < len(headers) else ""

                if h_name in ["نص الرسالة (للمراجعة)", "سياق النقاش"]:
                    cell.alignment = align_right
                else:
                    cell.alignment = align_center

                if h_name == "التصنيف":
                    if cell.value == "أولوية عالية":
                        cell.fill = high_priority_fill
                        cell.font = high_priority_font
                    else:
                        cell.fill = normal_fill
                        cell.font = normal_font

                # معالجة سكرين شوت وإدراج المصغرة بدقة
                if h_name == "سكرين شوت":
                    val = str(cell.value or "").strip()
                    if val and val != "لا توجد صورة" and os.path.exists(val):
                        abs_path = os.path.abspath(val)
                        ext = os.path.splitext(val)[1].lower()
                        if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                            try:
                                cell.value = "📷 عرض السؤال"
                                cell.hyperlink = abs_path
                                cell.font = Font(name="Segoe UI", size=9, color="2563EB", underline="single", bold=True)
                                cell.alignment = Alignment(horizontal="center", vertical="bottom")
                                
                                xl_img = OpenpyxlImage(abs_path)
                                w, h = xl_img.width, xl_img.height
                                if w > 0 and h > 0:
                                    scale = min(110 / w, 42 / h, 1.0)
                                    xl_img.width = int(w * scale)
                                    xl_img.height = int(h * scale)
                                    cell_coord = get_column_letter(c) + str(r)
                                    ws.add_image(xl_img, cell_coord)
                            except Exception:
                                cell.value = f"📷 {os.path.basename(val)}"
                                cell.hyperlink = abs_path
                                cell.font = Font(name="Segoe UI", size=10, color="2563EB", underline="single")
                        elif ext == '.pdf':
                            cell.value = f"📄 {os.path.basename(val)}"
                            cell.hyperlink = abs_path
                            cell.font = Font(name="Segoe UI", size=10, color="DC2626", underline="single", bold=True)
                    else:
                        cell.value = "لا توجد صورة"
                        cell.font = placeholder_font

                if h_name == "رابط الرسالة" and cell.value and str(cell.value).startswith("http"):
                    cell.hyperlink = cell.value
                    cell.font = Font(name="Segoe UI", size=10, color="2563EB", underline="single")

        col_widths = {
            "الكلمة المفتاحية": 20, "التصنيف": 16, "اسم المرسل": 20,
            "تاريخ ووقت الرسالة": 20, "سكرين شوت": 26, "رابط الرسالة": 32,
            "نص الرسالة (للمراجعة)": 45, "سياق النقاش": 55
        }
        for idx, h in enumerate(headers, 1):
            col_letter = get_column_letter(idx)
            ws.column_dimensions[col_letter].width = col_widths.get(h, 22)

        wb.save(file_path)
    except Exception as err:
        print(f"⚠️ تنبيه أثناء تنسيق الإكسل: {err}")

def format_followup_excel(file_path):
    """تنسيق ملف متابعة وتواصل الطلاب (الإكسل الثاني)"""
    try:
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        ws.sheet_view.rightToLeft = True

        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        data_font = Font(name="Segoe UI", size=10, color="0F172A")
        thin_border = Border(
            left=Side(style='thin', color="CBD5E1"),
            right=Side(style='thin', color="CBD5E1"),
            top=Side(style='thin', color="CBD5E1"),
            bottom=Side(style='thin', color="CBD5E1")
        )

        status_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
        status_font = Font(name="Segoe UI", size=10, bold=True, color="92400E")

        ws.row_dimensions[1].height = 30
        headers = [ws.cell(1, col).value for col in range(1, ws.max_column + 1)]
        for c in range(1, ws.max_column + 1):
            cell = ws.cell(1, c)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        dv = DataValidation(type="list", formula1='"تم الرد,في الانتظار"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"A2:A{ws.max_row + 1}")

        for r in range(2, ws.max_row + 1):
            ws.row_dimensions[r].height = 45
            for c in range(1, ws.max_column + 1):
                cell = ws.cell(r, c)
                cell.font = data_font
                cell.border = thin_border
                h_name = headers[c - 1] if c - 1 < len(headers) else ""

                if c == 1:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    cell.fill = status_fill
                    cell.font = status_font
                elif h_name == "رد الطالب (الأسئلة والتجربة)":
                    cell.alignment = Alignment(horizontal="right", vertical="center", wrap_text=True)
                else:
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

                if "رابط" in h_name and cell.value and str(cell.value).startswith("http"):
                    cell.hyperlink = cell.value
                    cell.font = Font(name="Segoe UI", size=10, color="2563EB", underline="single")

        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 22
        ws.column_dimensions['C'].width = 35
        ws.column_dimensions['D'].width = 50
        ws.column_dimensions['E'].width = 25
        ws.column_dimensions['F'].width = 22

        wb.save(file_path)
    except Exception as err:
        print(f"⚠️ تنبيه أثناء تنسيق ملف المتابعة: {err}")

def populate_master_client_sheets(all_questions, all_followup):
    """تعبئة وتنسيق الملفات الرسمية للعميل في المجلد الرئيسي بأعلى جودة واحترافية"""
    try:
        # 1. تنظيف وفلترة الأسئلة
        df_q = pd.DataFrame(all_questions).copy()
        if not df_q.empty:
            # استبعاد البوتات
            df_q = df_q[~df_q['اسم المرسل'].str.contains('ردود|بوت|Bot', na=False)]
            df_q = df_q[~df_q['نص الرسالة (للمراجعة)'].str.contains('المفكر 💯|متى تطلع|ادعول', na=False)]
            
            # ترتيب الأولوية
            category_order = ["أولوية عالية", "حديث غير محدد"]
            df_q['التصنيف'] = pd.Categorical(df_q['التصنيف'], categories=category_order, ordered=True)
            df_q = df_q.sort_values(by=['التصنيف', 'تاريخ ووقت الرسالة'], ascending=[True, False])
            
            wb1 = openpyxl.Workbook()
            ws1 = wb1.active
            ws1.title = "الرصد المباشر"
            ws1.sheet_view.rightToLeft = True
            
            title_font = Font(name="Segoe UI", size=14, bold=True, color="1E3A8A")
            note_font = Font(name="Segoe UI", size=10, italic=True, color="475569")
            header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            cell_font = Font(name="Segoe UI", size=10, color="0F172A")
            placeholder_font = Font(name="Segoe UI", size=9, italic=True, color="94A3B8")
            
            header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
            high_priority_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
            high_priority_font = Font(name="Segoe UI", size=10, bold=True, color="991B1B")
            normal_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
            normal_font = Font(name="Segoe UI", size=10, color="334155")
            
            thin_border = Border(
                left=Side(style='thin', color="CBD5E1"),
                right=Side(style='thin', color="CBD5E1"),
                top=Side(style='thin', color="CBD5E1"),
                bottom=Side(style='thin', color="CBD5E1")
            )
            align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
            align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)
            
            ws1.merge_cells("A1:E1")
            ws1["A1"] = "📊 ملف الرصد المباشر لتوثيق الرسائل الجاهزة وبنك الأسئلة"
            ws1["A1"].font = title_font
            ws1["A1"].alignment = Alignment(horizontal="right", vertical="center")
            ws1.row_dimensions[1].height = 28
            
            ws1.merge_cells("A2:E2")
            ws1["A2"] = "📌 ملاحظة: يُستخدم لتوثيق الرسائل والأسئلة الجاهزة. صفوف 'أولوية عالية' في أعلى الملف دائماً."
            ws1["A2"].font = note_font
            ws1["A2"].alignment = Alignment(horizontal="right", vertical="center")
            ws1.row_dimensions[2].height = 22
            
            headers1 = ["التصنيف", "سكرين شوت", "رابط الرسالة", "نص السؤال / الرسالة", "سياق النقاش والحلول"]
            ws1.row_dimensions[4].height = 30
            for c_idx, h in enumerate(headers1, 1):
                c = ws1.cell(row=4, column=c_idx, value=h)
                c.font = header_font
                c.fill = header_fill
                c.alignment = align_center
                c.border = thin_border
                
            start_r = 5
            # الاقتصار الحصري على الأسئلة والرسائل المصورة فقط بدون تكرار
            sample_q = df_q[
                (df_q['سكرين شوت'] != 'لا توجد صورة') & 
                (df_q['سكرين شوت'].str.strip() != '')
            ].drop_duplicates(subset=['رابط الرسالة'])
            
            for idx, (_, row) in enumerate(sample_q.iterrows()):
                r = start_r + idx
                ws1.row_dimensions[r].height = 60
                cat = row['التصنيف']
                
                c1 = ws1.cell(row=r, column=1, value=cat)
                c1.alignment = align_center
                c1.border = thin_border
                if cat == "أولوية عالية":
                    c1.fill = high_priority_fill
                    c1.font = high_priority_font
                else:
                    c1.fill = normal_fill
                    c1.font = normal_font
                    
                c2 = ws1.cell(row=r, column=2)
                c2.border = thin_border
                img_val = str(row['سكرين شوت'] or "").strip()
                if img_val and img_val != "لا توجد صورة" and os.path.exists(img_val):
                    abs_p = os.path.abspath(img_val)
                    c2.value = "📷 عرض السؤال"
                    c2.hyperlink = abs_p
                    c2.font = Font(name="Segoe UI", size=9, color="2563EB", underline="single", bold=True)
                    c2.alignment = Alignment(horizontal="center", vertical="bottom")
                    try:
                        xl_img = OpenpyxlImage(abs_p)
                        w, h = xl_img.width, xl_img.height
                        if w > 0 and h > 0:
                            scale = min(110 / w, 42 / h, 1.0)
                            xl_img.width = int(w * scale)
                            xl_img.height = int(h * scale)
                            ws1.add_image(xl_img, f"B{r}")
                    except Exception:
                        pass
                else:
                    c2.value = "لا توجد صورة"
                    c2.font = placeholder_font
                    c2.alignment = align_center
                    
                c3 = ws1.cell(row=r, column=3, value=row['رابط الرسالة'])
                c3.alignment = align_center
                c3.border = thin_border
                if str(row['رابط الرسالة']).startswith("http"):
                    c3.hyperlink = row['رابط الرسالة']
                    c3.font = Font(name="Segoe UI", size=10, color="2563EB", underline="single")
                    
                c4 = ws1.cell(row=r, column=4, value=str(row['نص الرسالة (للمراجعة)']))
                c4.alignment = align_right
                c4.border = thin_border
                c4.font = cell_font
                
                c5 = ws1.cell(row=r, column=5, value=str(row['سياق النقاش']))
                c5.alignment = align_right
                c5.border = thin_border
                c5.font = cell_font

            ws1.column_dimensions['A'].width = 18
            ws1.column_dimensions['B'].width = 25
            ws1.column_dimensions['C'].width = 32
            ws1.column_dimensions['D'].width = 45
            ws1.column_dimensions['E'].width = 55
            
            wb1.save("الإكسل الأول - الرصد المباشر.xlsx")
            wb1.save("الرصد_المباشر.xlsx")
            print("   ✅ تم تحديث وحفظ: 'الإكسل الأول - الرصد المباشر.xlsx'")

        # 2. ملف التواصل وجمع البيانات (الـ 6 طلاب)
        df_f = pd.DataFrame(all_followup).copy()
        if not df_f.empty:
            comb_f = df_f.drop_duplicates(subset=['رابط حساب الطالب أو رسالته'])
            wb2 = openpyxl.Workbook()
            ws2 = wb2.active
            ws2.title = "التواصل وجمع البيانات"
            ws2.sheet_view.rightToLeft = True
            
            ws2.merge_cells("A1:D1")
            ws2["A1"] = "📋 ملف التواصل وجمع البيانات - متابعة الـ 6 طلاب يومياً"
            ws2["A1"].font = title_font
            ws2["A1"].alignment = Alignment(horizontal="right", vertical="center")
            ws2.row_dimensions[1].height = 28
            
            ws2.merge_cells("A2:D2")
            ws2["A2"] = "📌 ملاحظة: يُستخدم لتوثيق محاولات التواصل مع الـ 6 طلاب يومياً ومتابعة ردودهم وتجاربهم."
            ws2["A2"].font = note_font
            ws2["A2"].alignment = Alignment(horizontal="right", vertical="center")
            ws2.row_dimensions[2].height = 22
            
            headers2 = ["حالة التواصل (تم الرد / في الانتظار)", "رابط حساب الطالب أو رسالته", "رد الطالب (الأسئلة والتجربة)", "سكرين شوت للمحادثة"]
            ws2.row_dimensions[4].height = 30
            for c_idx, h in enumerate(headers2, 1):
                c = ws2.cell(row=4, column=c_idx, value=h)
                c.font = header_font
                c.fill = header_fill
                c.alignment = align_center
                c.border = thin_border
                
            dv = DataValidation(type="list", formula1='"تم الرد,في الانتظار"', allow_blank=True)
            ws2.add_data_validation(dv)
            dv.add(f"A5:A35")
            
            status_fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
            status_font = Font(name="Segoe UI", size=10, bold=True, color="92400E")
            
            top_students = comb_f.head(10)
            for idx, (_, row) in enumerate(top_students.iterrows()):
                r = 5 + idx
                ws2.row_dimensions[r].height = 50
                
                c1 = ws2.cell(row=r, column=1, value="في الانتظار")
                c1.alignment = align_center
                c1.border = thin_border
                c1.fill = status_fill
                c1.font = status_font
                
                c2 = ws2.cell(row=r, column=2, value=str(row['رابط حساب الطالب أو رسالته']))
                c2.alignment = align_center
                c2.border = thin_border
                if str(row['رابط حساب الطالب أو رسالته']).startswith("http"):
                    c2.hyperlink = str(row['رابط حساب الطالب أو رسالته'])
                    c2.font = Font(name="Segoe UI", size=10, color="2563EB", underline="single")
                    
                c3 = ws2.cell(row=r, column=3, value=str(row['رد الطالب (الأسئلة والتجربة)']))
                c3.alignment = align_right
                c3.border = thin_border
                c3.font = cell_font
                
                c4 = ws2.cell(row=r, column=4)
                c4.border = thin_border
                img_val = str(row['سكرين شوت للمحادثة'] or "").strip()
                if img_val and img_val != "لا توجد صورة" and os.path.exists(img_val):
                    abs_p = os.path.abspath(img_val)
                    c4.value = "📷 عرض المحادثة"
                    c4.hyperlink = abs_p
                    c4.font = Font(name="Segoe UI", size=9, color="2563EB", underline="single", bold=True)
                    c4.alignment = Alignment(horizontal="center", vertical="bottom")
                    try:
                        xl_img = OpenpyxlImage(abs_p)
                        w, h = xl_img.width, xl_img.height
                        if w > 0 and h > 0:
                            scale = min(110 / w, 40 / h, 1.0)
                            xl_img.width = int(w * scale)
                            xl_img.height = int(h * scale)
                            ws2.add_image(xl_img, f"D{r}")
                    except Exception:
                        pass
                else:
                    c4.value = "لا توجد صورة"
                    c4.font = placeholder_font
                    c4.alignment = align_center
                    
            ws2.column_dimensions['A'].width = 25
            ws2.column_dimensions['B'].width = 35
            ws2.column_dimensions['C'].width = 60
            ws2.column_dimensions['D'].width = 25
            
            wb2.save("الإكسل الثاني - التواصل وجمع البيانات.xlsx")
            wb2.save("التواصل_وجمع_البيانات.xlsx")
            print("   ✅ تم تحديث وحفظ: 'الإكسل الثاني - التواصل وجمع البيانات.xlsx'")
    except Exception as err:
        print(f"⚠️ تنبيه أثناء تعبئة الملفات الرسمية: {err}")

if __name__ == '__main__':
    asyncio.run(main())