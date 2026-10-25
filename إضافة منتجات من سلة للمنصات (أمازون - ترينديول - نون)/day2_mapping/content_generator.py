# =============================================================================
#  content_generator.py — تنظيف وتوليد المحتوى التسويقي للمنصات
# =============================================================================

import re
import sys
from bs4 import BeautifulSoup

# نسبة الزيادة السعرية لتغطية عمولة المنصات (0 = بدون زيادة)
PRICE_MARKUP_PERCENT = 0.0


def strip_html(html_content: str) -> str:
    """تنظيف نصوص الوصف من وسوم HTML والروابط للحصول على نص نقي."""
    if not html_content or str(html_content).strip() in ("", "nan", "None"):
        return ""

    try:
        soup = BeautifulSoup(str(html_content), "html.parser")

        # إزالة وسوم الصور والروابط الزائدة
        for s in soup(["script", "style", "img"]):
            s.decompose()

        text = soup.get_text(separator=" ")
        # إزالة المسافات الزائدة
        text = re.sub(r"\s+", " ", text).strip()
        # إزالة الروابط المتبقية في النص إن وُجدت
        text = re.sub(r"https?://\S+", "", text).strip()
        return text
    except Exception:
        clean = re.sub(r"<[^>]+>", " ", str(html_content))
        return re.sub(r"\s+", " ", clean).strip()


def extract_bullet_points(row: dict) -> list[str]:
    """
    استخراج 5 نقاط بارزة (Bullet Points) منظمة بدقة متناهية
    من الوصف ومواصفات المنتج لاستخدامها في أمازون ونون.
    """
    desc_html = str(row.get("description", ""))
    name = str(row.get("name_ar", "")).strip()
    brand = str(row.get("brand", "")).strip() or "قطاف الطبيعة"
    weight_kg = row.get("weight_kg", 0.0)
    category = str(row.get("category", "")).strip()

    bullets = []

    if desc_html and desc_html != "nan":
        try:
            soup = BeautifulSoup(desc_html, "html.parser")
            items = [li.get_text(strip=True) for li in soup.find_all("li") if len(li.get_text(strip=True)) > 5]
            for item in items:
                # تصفية الروابط أو النصوص الدعائية العامة
                if "http" not in item and "شاهد أيضًا" not in item and "للمزيد" not in item:
                    cleaned_item = re.sub(r"\s+", " ", item).strip()
                    if cleaned_item and cleaned_item not in bullets:
                        bullets.append(cleaned_item)
                if len(bullets) >= 5:
                    break
        except Exception:
            pass

    # إذا كانت النقاط المستخرجة أقل من 5، نُكمل بنقاط قياسية ذكية مبنية على بيانات المنتج:
    fallbacks = [
        f"منتج أصلي عالي الجودة من علامة {brand} الموثوقة.",
        f"مواصفات قياسية ووزن صافي {weight_kg} كجم في عبوة محكمة الإغلاق لحفظ النقاء والجودة.",
        f"طبيعي 100% ومثالي للاستخدام اليومي ضمن تصنيف {category.replace(',', ' و ')}.",
        "تمت التعبئة والتغليف بأعلى معايير السلامة والجودة الغذائية لضمان الطزاجة.",
        "يحفظ في مكان بارد وجاف وبعيداً عن أشعة الشمس المباشرة لضمان أفضل جودة واستدامة.",
    ]

    for fb in fallbacks:
        if len(bullets) < 5:
            bullets.append(fb)

    # ضمان أن كل نقطة لا تتجاوز 450 حرفاً (حدود أمازون)
    return [b[:450].strip() for b in bullets[:5]]


def generate_standard_title(brand: str, name_ar: str, weight_kg: float) -> str:
    """
    توليد عنوان إدراج قياسي واحترافي:
    [اسم الماركة] - [اسم المنتج] - [الوزن]
    """
    brand_clean = (brand or "قطاف الطبيعة").strip()
    name_clean = (name_ar or "").strip()

    # إذا كان الاسم يتضمن بالفعل اسم الماركة، نتجنب التكرار
    if brand_clean in name_clean:
        title = name_clean
    else:
        title = f"{brand_clean} - {name_clean}"

    # إذا كان الاسم لا يحتوي على وزن مذكور، نضيف الوزن بالكيلو أو الجرام
    if not re.search(r"\d+\s*(جرام|كجم|كيلو|مل|g|kg|ml)", name_clean, re.IGNORECASE):
        if weight_kg > 0:
            if weight_kg < 1.0:
                title += f" - {int(weight_kg * 1000)} جرام"
            else:
                title += f" - {weight_kg} كجم"

    # أمازون تسمح بحد أقصى 200 حرف للعنوان
    return title[:200].strip()


def calculate_platform_price(base_price: float) -> float:
    """حساب سعر البيع على المنصة مع تطبيق نسبة الزيادة إن وُجدت."""
    try:
        p = float(base_price)
        if p <= 0:
            return 0.0
        if PRICE_MARKUP_PERCENT > 0:
            return round(p * (1.0 + (PRICE_MARKUP_PERCENT / 100.0)), 2)
        return round(p, 2)
    except Exception:
        return 0.0


def generate_search_terms(name_ar: str, category: str, brand: str) -> str:
    """توليد كلمات بحث دلالية مخفية (Search Terms) للمنصات."""
    terms = [brand, name_ar, category.replace(",", " ")]
    combined = " ".join(terms)
    # إزالة التشكيل والرموز الخاصة
    words = re.findall(r"[\w\u0621-\u064A]+", combined)
    unique_words = []
    for w in words:
        if len(w) > 2 and w not in unique_words:
            unique_words.append(w)
    return " ".join(unique_words[:20])


def generate_amazon_highlight(name_ar: str, category: str) -> str:
    """
    توليد نقطة بارزة (Item Highlight) آمنة ومتوافقة 100% مع فلاتر وسياسات أمازون:
    - نصوص إنجليزية قياسية خالية من الأرقام والرموز والادعاءات الطبية أو الترويجية المحظورة.
    """
    text = f"{name_ar} {category}".lower()

    if any(w in text for w in ["حناء", "سدر", "شعر", "مشاط", "زيت", "بشرة", "تجميل", "عناية"]):
        return "Natural Herbal Care Formula for Daily Hair and Body Routine"
    elif any(w in text for w in ["شاي", "قهوة", "بن", "هيل", "مشروب", "كركديه"]):
        return "Premium Traditional Herbal Tea and Beverage Specialty"
    elif any(w in text for w in ["بهار", "توابل", "فلفل", "كمون", "كزبرة", "قرفة", "كركم"]):
        return "Authentic Aromatic Spices and Culinary Seasoning"
    elif any(w in text for w in ["عسل", "سمن", "زبدة", "تمر", "دبس"]):
        return "Pure Traditional Specialty Food and Pantry Staple"
    elif any(w in text for w in ["بذور", "حبوب", "سمسم", "كتان", "رشاد"]):
        return "Wholesome Natural Seeds and Grain Pantry Essentials"
    else:
        return "High Quality Natural Specialty Pantry Product"

