"""
الحل الجذري: بدل ما نكتب tags بـ python-docx (اللي بيكسرها على runs متعددة),
هنعمل find-and-replace مباشرة في الـ XML داخل ملف الـ docx
عشان نضمن إن كل tag تبقى run واحد متكامل يقدر docxtpl يتعرف عليه.
"""
import zipfile
import shutil
import os
import re

def fix_tags_in_xml(input_path, output_path):
    """
    يفتح ملف الـ docx كـ zip، ويعمل find-and-replace في document.xml
    لتوحيد كل tag مكسورة على runs متعددة في run واحد.
    """
    # نسخ الملف المصدر للملف الهدف أولاً
    shutil.copy2(input_path, output_path)
    
    # قراءة document.xml من الـ zip
    with zipfile.ZipFile(output_path, 'r') as z:
        xml_content = z.read('word/document.xml').decode('utf-8')
    
    # دالة تنظف tags المكسورة: بتدور على النمط {{...}} المقسمة على runs XML
    # وتوحدها في run واحد
    def merge_broken_tags(xml):
        """
        الـ XML بيخزن {{Hashtags}} على شكل:
        <w:r><w:t>{{</w:t></w:r><w:r><w:t>Hashtags</w:t></w:r><w:r><w:t>}}</w:t></w:r>
        الدالة دي بتشيل tags المكسورة وتعمل منها tag صحيحة.
        """
        # أولاً: نشيل كل tags الـ Word الزيادة (spelling errors etc) من الـ XML
        # بيعمل strip للـ proofErr و rPrChange اللي بيكسروا الـ runs
        xml = re.sub(r'<w:proofErr[^/]*/>', '', xml)
        xml = re.sub(r'<w:rPrChange>.*?</w:rPrChange>', '', xml, flags=re.DOTALL)
        
        # الخطوة الرئيسية: دور على كل run يحتوي على {{ وادمج معه الـ runs اللي بعده لحد ما يلاقي }}
        # Pattern: نص مقسم على runs
        # نستبدل الـ opening و closing براkets المنفصلة
        
        # Strategy: extract all text within runs, check if combined they form a tag
        # Then rebuild the XML with merged runs
        
        # بنفس المبدأ: نعوض عن الـ runs المتعددة بـ run واحد
        # نستخدم pattern يدور على run elements متتالية
        def merge_run_texts(match_xml):
            # استخراج كل النصوص من الـ runs
            texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', match_xml)
            combined = ''.join(texts)
            return combined
        
        # دور على مجموعات الـ runs المتتالية اللي بتشكل tags
        # Pattern يمسك سلسلة من runs متتالية
        run_pattern = re.compile(r'(<w:r>(?:<w:rPr>.*?</w:rPr>)?<w:t[^>]*>[^<]*</w:t></w:r>)+', re.DOTALL)
        
        def check_and_merge(m):
            block = m.group(0)
            # استخراج كل النصوص
            texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', block)
            combined = ''.join(texts)
            
            # لو فيه tag مكتملة في المجموعة دي
            if '{{' in combined and '}}' in combined:
                # أعد بناء الـ block كـ run واحد مع النص الكامل
                return f'<w:r><w:t xml:space="preserve">{combined}</w:t></w:r>'
            return block
        
        xml = run_pattern.sub(check_and_merge, xml)
        return xml
    
    fixed_xml = fix_tags_in_xml_content(xml_content)
    
    # كتابة الـ XML المصلح في الـ zip
    # نقرأ كل الملفات الأخرى ونعمل zip جديد
    tmp_path = output_path + ".tmp"
    with zipfile.ZipFile(output_path, 'r') as zin:
        with zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == 'word/document.xml':
                    zout.writestr(item, fixed_xml.encode('utf-8'))
                else:
                    zout.writestr(item, zin.read(item.filename))
    
    os.replace(tmp_path, output_path)
    print(f"✅ Fixed XML tags in {output_path}")


def fix_tags_in_xml_content(xml):
    """
    الحل الأبسط: نبحث عن أي text يحتوي على {{ أو }} ونعمل merge للـ runs المتتالية.
    """
    # شيل الـ proofErr elements اللي بتكسر الـ runs
    xml = re.sub(r'<w:proofErr[^/]*/>', '', xml)
    
    # Pattern لمجموعات runs متتالية (بدون أي elements تانية بينهم)
    # كل run: <w:r>...</w:t></w:r>  
    run_pat = re.compile(
        r'((?:<w:r>(?:<w:rPr>.*?</w:rPr>)?<w:t(?:\s[^>]*)?>.*?</w:t></w:r>\s*)+)',
        re.DOTALL
    )
    
    def merge_if_tag(m):
        block = m.group(0)
        # استخراج كل النصوص
        texts = re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', block)
        combined = ''.join(texts)
        
        # لو في tag واحدة على الأقل
        if '{{' in combined and '}}' in combined:
            return f'<w:r><w:t xml:space="preserve">{combined}</w:t></w:r>'
        return block
    
    xml = run_pat.sub(merge_if_tag, xml)
    return xml


# تطبيق على القالب الموجود
fix_tags_in_xml("template.docx", "template.docx")

# تحقق من النتيجة
from docxtpl import DocxTemplate
doc = DocxTemplate("template.docx")
undeclared = doc.get_undeclared_template_variables()
print(f"\nعدد المتغيرات المعترف بها: {len(undeclared)}")
if undeclared:
    print("المتغيرات:", sorted(undeclared))
else:
    print("✅ لا يوجد متغيرات! كل شيء تمام.")
