import os
import sys
import hashlib
import re
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as OpenpyxlImage

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

def get_file_hash(path):
    """حساب البصمة الرقمية للصورة (MD5) لاكتشاف وتطابق الصور المتماثلة بدقة 100%"""
    if not path or not os.path.exists(path):
        return None
    h = hashlib.md5()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None

def find_latest_report(folder_path):
    """البحث عن أحدث ملف تقرير Report_*.xlsx داخل مجلد القناة"""
    if not os.path.exists(folder_path):
        return None
    files = [
        f for f in os.listdir(folder_path) 
        if f.startswith('Report_') and f.endswith('.xlsx') and not f.startswith('~$')
    ]
    if not files:
        return None
    files.sort()
    return os.path.join(folder_path, files[-1])

def merge_and_deduplicate():
    print("=" * 65)
    print("🚀 بدء تشغيل أداة دمج وتصفية بنك الأسئلة الشامل (بدون تكرار)")
    print("=" * 65)

    channels = {
        'المفكر': 'Almufakir',
        'المنصف': 'Elmonsefqudrat'
    }

    raw_items = []
    
    # 1. قراءة أحدث تقارير من كل قناة
    for channel_label, folder in channels.items():
        latest_file = find_latest_report(folder)
        if not latest_file:
            print(f"⚠️ لم يتم العثور على تقارير في مجلد: {folder}")
            continue
            
        print(f"\n📂 قراءة تقرير قناة [{channel_label}]:\n   {latest_file}")
        wb = openpyxl.load_workbook(latest_file)
        ws = wb.active
        
        headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
        img_col = headers.index('سكرين شوت') + 1
        link_col = headers.index('رابط الرسالة') + 1
        cat_col = headers.index('التصنيف') + 1
        sender_col = headers.index('اسم المرسل') + 1
        date_col = headers.index('تاريخ ووقت الرسالة') + 1
        text_col = headers.index('نص الرسالة (للمراجعة)') + 1
        ctx_col = headers.index('سياق النقاش') + 1
        
        count_in_file = 0
        for r in range(2, ws.max_row + 1):
            cell_img = ws.cell(row=r, column=img_col)
            val = str(cell_img.value or '').strip()
            link = cell_img.hyperlink.target if cell_img.hyperlink else None
            
            # تحديد مسار الصورة الفعلي على الجهاز
            img_path = None
            if link and os.path.exists(link):
                img_path = os.path.abspath(link)
            elif link and os.path.exists(os.path.join(folder, link)):
                img_path = os.path.abspath(os.path.join(folder, link))
                
            # تجاهل أي صف لا يحتوي على صورة
            if not img_path or not os.path.exists(img_path):
                continue
                
            img_hash = get_file_hash(img_path)
            if not img_hash:
                continue
                
            msg_link = ws.cell(row=r, column=link_col).hyperlink
            msg_url = msg_link.target if msg_link else str(ws.cell(row=r, column=link_col).value or '')
            
            raw_items.append({
                'channel': channel_label,
                'img_hash': img_hash,
                'img_path': img_path,
                'category': str(ws.cell(row=r, column=cat_col).value or 'حديث غير محدد'),
                'sender': str(ws.cell(row=r, column=sender_col).value or 'طالب'),
                'date': str(ws.cell(row=r, column=date_col).value or ''),
                'msg_link': msg_url,
                'text': str(ws.cell(row=r, column=text_col).value or '').strip(),
                'context': str(ws.cell(row=r, column=ctx_col).value or '').strip()
            })
            count_in_file += 1
            
        print(f"   📥 تم استخراج {count_in_file} رسالة مصورة.")

    if not raw_items:
        print("❌ لم يتم العثور على أي أسئلة مصورة للدمج.")
        return

    print(f"\n📊 إجمالي السجلات المستخرجة قبل التصفية: {len(raw_items)} سجل.")

    # 2. الدمج الذكي بناءً على بصمة الصورة (Image Hash)
    # كل سؤال يظهر في صف واحد فقط، مع دمج كافة ردود وتأكيدات الطلاب داخله
    grouped_questions = {}
    for item in raw_items:
        h = item['img_hash']
        if h not in grouped_questions:
            grouped_questions[h] = {
                'channels': {item['channel']},
                'img_path': item['img_path'],
                'category': item['category'],
                'senders': [item['sender']],
                'dates': [item['date']],
                'links': [item['msg_link']],
                'texts': [item['text']],
                'contexts': [item['context']]
            }
        else:
            g = grouped_questions[h]
            g['channels'].add(item['channel'])
            if item['category'] == 'أولوية عالية':
                g['category'] = 'أولوية عالية'
            g['senders'].append(item['sender'])
            g['dates'].append(item['date'])
            if item['msg_link'] not in g['links']:
                g['links'].append(item['msg_link'])
            if item['text'] and item['text'] not in g['texts']:
                g['texts'].append(item['text'])
            if item['context'] and item['context'] not in g['contexts']:
                g['contexts'].append(item['context'])

    print(f"✨ عدد الأسئلة الفريدة تماماً بعد الدمج ومنع التكرار: {len(grouped_questions)} سؤالاً فريداً!")

    # 3. بناء جدول البيانات النهائي المصفى
    merged_rows = []
    for h, g in grouped_questions.items():
        # اسم المصدر / القنوات التي ورد فيها السؤال
        channel_source = " + ".join(sorted(list(g['channels'])))
        
        # إذا ورد السؤال في القناتين أو ورد عليه أكثر من تأكيد، يرفع تلقائياً لأولوية عالية
        cat = g['category']
        if len(g['channels']) > 1 or len(g['links']) > 1:
            cat = "أولوية عالية"
            
        # أفضل نص يعبر عن السؤال (أطول نص ذو معنى)
        valid_texts = [t for t in g['texts'] if t and t != "[سؤال مصور من بنك الأسئلة / التجميعات]"]
        best_text = valid_texts[0] if valid_texts else "[سؤال مصور من بنك الأسئلة والتجميعات]"
        
        # دمج سياق النقاش والحلول وتأكيدات الطلاب بدون تكرار
        cleaned_contexts = []
        for ctx in g['contexts']:
            if ctx and ctx != "📷 [سؤال مصور معروض للمناقشة في القناة]" and ctx not in cleaned_contexts:
                cleaned_contexts.append(ctx)
                
        # إذا كان هناك أكثر من طالب أكد على السؤال، نضيف ملخص التأكيدات
        student_confirmations = []
        for s, t in zip(g['senders'], g['texts']):
            if any(w in t for w in ["جاني", "تكرر", "نفس السؤال", "اليوم"]):
                student_confirmations.append(f"💬 {s}: {t}")
                
        context_blocks = []
        if len(g['channels']) > 1:
            context_blocks.append(f"🌟 [سؤال متكرر ورد في قناتي: {channel_source}]")
            
        if student_confirmations:
            context_blocks.append("👥 [تأكيدات ورود السؤال في الاختبار]:\n" + "\n".join(student_confirmations))
            
        if cleaned_contexts:
            context_blocks.append("\n\n".join(cleaned_contexts))
            
        final_context = "\n\n".join(context_blocks) if context_blocks else "📷 [سؤال مصور معروض للمناقشة وبنك الأسئلة]"
        
        # أحدث تاريخ
        sorted_dates = sorted([d for d in g['dates'] if d], reverse=True)
        latest_date = sorted_dates[0] if sorted_dates else ""
        
        # الرابط الأساسي
        primary_link = g['links'][0] if g['links'] else ""
        
        merged_rows.append({
            'source': channel_source,
            'category': cat,
            'img_path': g['img_path'],
            'primary_link': primary_link,
            'sender': g['senders'][0] if g['senders'] else 'طالب',
            'date': latest_date,
            'text': best_text,
            'context': final_context
        })

    # ترتيب الصفوف بحيث تظهر "أولوية عالية" في الأعلى دائماً
    merged_rows.sort(
        key=lambda x: (0 if x['category'] == 'أولوية عالية' else 1, x['date']), 
        reverse=False
    )

    # 4. كتابة وتنسيق ملف الإكسل الاحترافي
    output_files = [
        "بنك_الأسئلة_المجمع_بدون_تكرار.xlsx",
        "الإكسل الأول - الرصد المباشر.xlsx",
        "الرصد_المباشر.xlsx"
    ]
    
    for out_file in output_files:
        wb_out = openpyxl.Workbook()
        ws_out = wb_out.active
        ws_out.title = "بنك الأسئلة الموحد"
        ws_out.sheet_view.rightToLeft = True

        title_font = Font(name="Segoe UI", size=14, bold=True, color="1E3A8A")
        note_font = Font(name="Segoe UI", size=10, italic=True, color="475569")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        data_font = Font(name="Segoe UI", size=10, color="0F172A")
        
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

        # عنوان ورقة العمل والتعليمات
        ws_out.merge_cells("A1:H1")
        ws_out["A1"] = "📊 بنك الأسئلة الموحد والشامل (مدمج من القنوات وبدون أي تكرار)"
        ws_out["A1"].font = title_font
        ws_out["A1"].alignment = Alignment(horizontal="right", vertical="center")
        ws_out.row_dimensions[1].height = 28

        ws_out.merge_cells("A2:H2")
        ws_out["A2"] = "📌 ملاحظة: تم دمج الأسئلة المتطابقة في صف واحد، مع تجميع كافة حلول وتأكيدات الطلاب في سياق النقاش. صفوف 'أولوية عالية' في الأعلى دائماً."
        ws_out["A2"].font = note_font
        ws_out["A2"].alignment = Alignment(horizontal="right", vertical="center")
        ws_out.row_dimensions[2].height = 22

        headers = [
            "المصدر / القناة", "التصنيف", "اسم / يوزر الطالب", "سكرين شوت", 
            "رابط الرسالة", "نص السؤال / المسألة", "سياق النقاش والحلول المجمعة", "تاريخ الرصد"
        ]
        ws_out.row_dimensions[4].height = 30
        for c_idx, h in enumerate(headers, 1):
            c = ws_out.cell(row=4, column=c_idx, value=h)
            c.font = header_font
            c.fill = header_fill
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = thin_border

        for idx, row in enumerate(merged_rows, 5):
            ws_out.row_dimensions[idx].height = 65
            cat = row['category']
            
            # 1. المصدر
            c1 = ws_out.cell(row=idx, column=1, value=row['source'])
            c1.alignment = Alignment(horizontal="center", vertical="center")
            c1.border = thin_border
            c1.font = Font(name="Segoe UI", size=10, bold=True, color="1E3A8A" if "+" in row['source'] else "334155")
            
            # 2. التصنيف
            c2 = ws_out.cell(row=idx, column=2, value=cat)
            c2.alignment = Alignment(horizontal="center", vertical="center")
            c2.border = thin_border
            if cat == "أولوية عالية":
                c2.fill = high_priority_fill
                c2.font = high_priority_font
            else:
                c2.fill = normal_fill
                c2.font = normal_font

            # 3. اسم / يوزر الطالب
            c3 = ws_out.cell(row=idx, column=3, value=row['sender'])
            c3.alignment = Alignment(horizontal="center", vertical="center")
            c3.border = thin_border
            c3.font = Font(name="Segoe UI", size=10, bold=True, color="0F172A")
                
            # 4. سكرين شوت (المصغرة + الرابط)
            c4 = ws_out.cell(row=idx, column=4)
            c4.border = thin_border
            img_p = row['img_path']
            if img_p and os.path.exists(img_p):
                c4.value = "📷 عرض السؤال"
                c4.hyperlink = img_p
                c4.font = Font(name="Segoe UI", size=9, color="2563EB", underline="single", bold=True)
                c4.alignment = Alignment(horizontal="center", vertical="bottom")
                try:
                    xl_img = OpenpyxlImage(img_p)
                    w, h = xl_img.width, xl_img.height
                    if w > 0 and h > 0:
                        scale = min(110 / w, 44 / h, 1.0)
                        xl_img.width = int(w * scale)
                        xl_img.height = int(h * scale)
                        ws_out.add_image(xl_img, f"D{idx}")
                except Exception:
                    pass
            else:
                c4.value = "لا توجد صورة"
                c4.font = Font(name="Segoe UI", size=9, italic=True, color="94A3B8")
                c4.alignment = Alignment(horizontal="center", vertical="center")
                
            # 5. رابط الرسالة
            c5 = ws_out.cell(row=idx, column=5, value=row['primary_link'])
            c5.alignment = Alignment(horizontal="center", vertical="center")
            c5.border = thin_border
            if str(row['primary_link']).startswith("http"):
                c5.hyperlink = row['primary_link']
                c5.font = Font(name="Segoe UI", size=10, color="2563EB", underline="single")
                
            # 6. نص السؤال
            c6 = ws_out.cell(row=idx, column=6, value=row['text'])
            c6.alignment = Alignment(horizontal="right", vertical="center", wrap_text=True)
            c6.border = thin_border
            c6.font = data_font
            
            # 7. سياق النقاش
            c7 = ws_out.cell(row=idx, column=7, value=row['context'])
            c7.alignment = Alignment(horizontal="right", vertical="center", wrap_text=True)
            c7.border = thin_border
            c7.font = data_font
            
            # 8. التاريخ
            c8 = ws_out.cell(row=idx, column=8, value=row['date'])
            c8.alignment = Alignment(horizontal="center", vertical="center")
            c8.border = thin_border
            c8.font = data_font

        col_widths = {
            1: 18,  # المصدر
            2: 16,  # التصنيف
            3: 22,  # اسم / يوزر الطالب
            4: 26,  # سكرين شوت
            5: 32,  # رابط الرسالة
            6: 45,  # نص السؤال
            7: 60,  # سياق النقاش المجمع
            8: 20   # التاريخ
        }
        for col_idx, width in col_widths.items():
            ws_out.column_dimensions[get_column_letter(col_idx)].width = width

        wb_out.save(out_file)
        print(f"   💾 تم الحفظ بنجاح: {out_file}")

    print("\n" + "=" * 65)
    print("🎉 اكتمل الدمج والتصفية بنجاح تام!")
    print(f"📌 إجمالي الأسئلة في الملف الموحد: {len(merged_rows)} سؤالاً فريداً ومصوراً.")
    print("📌 تم إضافة عمود 'اسم / يوزر الطالب' ودمج ردود وتأكيدات الطلاب.")
    print("=" * 65)

if __name__ == '__main__':
    merge_and_deduplicate()
