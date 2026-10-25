"""
فحص مخزون أمازون المباشر ومطابقته مع سلة
=============================================================================
يفتح صفحة إدارة المنتجات والمخزون في أمازون السعودية (Seller Central):
https://sellercentral.amazon.sa/myinventory/inventory?fulfilledBy=all&page=1&pageSize=50&sort=date_created_desc&status=all

ويقوم بجلب كافة المنتجات المدرجة حالياً على أمازون، ثم يقارنها مع ملف سلة
ويستخرج تقريراً شاملاً بالمنتجات الموجودة (المدرجة) والمنتجات المفقودة (غير الموجودة).
"""

import sys
import os
import re
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import pandas as pd

# ضمان ترميز UTF-8 في شاشة الأوامر على ويندوز
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# استيراد مكونات الحزمة
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from amazon_salla_validator.config import ValidatorConfig, SallaProduct
from amazon_salla_validator.salla_reader import SallaExcelReader
from amazon_salla_validator.amazon_scraper import AmazonScraper
from amazon_salla_validator.reporter import safe_print

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AmazonInventoryChecker")

TARGET_INVENTORY_URL = (
    "https://sellercentral.amazon.sa/myinventory/inventory"
    "?fulfilledBy=all&page={page}&pageSize={page_size}&sort=date_created_desc&status=all"
)


class LiveInventoryAuditor:
    """يقوم بفحص مخزون أمازون المباشر ومطابقته مع سلة."""

    def __init__(
        self,
        excel_path: Path,
        profile_dir: Path,
        output_dir: Path,
        email: Optional[str] = "lawazimplus93@gmail.com",
        password: Optional[str] = "Qitaf@123456",
        headless: bool = False,
        max_pages: int = 15,
        page_size: int = 50
    ):
        self.excel_path = Path(excel_path)
        self.profile_dir = Path(profile_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.email = email
        self.password = password
        self.headless = headless
        self.max_pages = max_pages
        self.page_size = page_size

        self.config = ValidatorConfig(
            marketplace="SA",
            excel_path=self.excel_path,
            output_dir=self.output_dir,
            chrome_profile_dir=self.profile_dir,
            headless=self.headless,
            amazon_email=self.email,
            amazon_password=self.password,
        )
        self.scraper: Optional[AmazonScraper] = None

    def load_salla_catalog(self) -> List[SallaProduct]:
        """تحميل منتجات سلة من ملف الإكسيل."""
        logger.info(f"قراءة ملف سلة: {self.excel_path.name}")
        reader = SallaExcelReader(self.excel_path)
        products = reader.load_products()
        logger.info(f"تم تحميل {len(products)} منتج من سلة.")
        return products

    def scrape_all_amazon_inventory(self) -> Dict[str, Dict[str, Any]]:
        """
        يتصفح صفحات المخزون في أمازون ويستخرج كل المنتجات المسجلة.
        يرجع قاموساً بمفتاح الـ SKU وقيم البيانات (ASIN, Title, Price, Status, Qty).
        """
        self.scraper = AmazonScraper(self.config)
        self.scraper.start_browser()

        # التأكد من تسجيل الدخول
        if not self.scraper.login_seller_central():
            raise RuntimeError("تعذر تسجيل الدخول إلى أمازون Seller Central.")

        driver = self.scraper.driver
        all_amazon_products: Dict[str, Dict[str, Any]] = {}

        logger.info("بدء جلب صفحات مخزون أمازون...")

        for page in range(1, self.max_pages + 1):
            url = TARGET_INVENTORY_URL.format(page=page, page_size=self.page_size)
            logger.info(f"فتح صفحة المخزون رقم {page}: {url}")
            driver.get(url)
            time.sleep(4)

            # فحص إذا تم التحويل لصفحة تسجيل الدخول
            if "signin" in driver.current_url.lower():
                print("\n⚠ يرجى إتمام تسجيل الدخول في نافذة المتصفح المفتوحة...")
                while "signin" in driver.current_url.lower():
                    time.sleep(3)

            page_source = driver.page_source

            # استخراج أسطر جدول المنتجات
            # في الواجهة الجديدة لأمازون، تُعرض المنتجات إما داخل <table> أو عبر بطاقات myi-table
            row_elements = driver.find_elements(
                by="css selector",
                value="table tbody tr, div[data-test-id='inventory-row'], tr[id^='myi-row-']"
            )

            # إذا لم توجد أسطر، نحاول البحث عن الـ SKUs في محتوى الصفحة
            page_found_count = 0

            if row_elements:
                for row in row_elements:
                    text = row.text.strip()
                    html = row.get_attribute("innerHTML") or ""
                    if not text and not html:
                        continue

                    # استخراج SKU
                    sku = None
                    sku_match = re.search(r"SKU:\s*([A-Za-z0-9_\-\.]+)", text)
                    if sku_match:
                        sku = sku_match.group(1).strip()
                    else:
                        sku_elem = self.scraper.find_first_element(
                            ["[data-column='sku']", ".myi-sku", "[data-test-id='sku']"],
                            parent=row
                        )
                        if sku_elem:
                            sku = sku_elem.text.replace("SKU:", "").strip()

                    # استخراج ASIN
                    asin = None
                    asin_match = re.search(r"\b(B0[A-Z0-9]{8})\b", text + " " + html)
                    if asin_match:
                        asin = asin_match.group(1)

                    # استخراج السعر
                    price = None
                    price_match = re.search(r"(?:SAR|ر\.س|\$)\s*(\d+(?:\.\d+)?)", text)
                    if price_match:
                        price = float(price_match.group(1))
                    else:
                        num_matches = re.findall(r"(\d+\.\d{2})", text)
                        if num_matches:
                            price = float(num_matches[0])

                    # استخراج الحالة (Active, Inactive, Suppressed...)
                    status = "Active"
                    if "غير نشط" in text or "Inactive" in text or "Out of Stock" in text:
                        status = "Inactive"
                    elif "محظور" in text or "Suppressed" in text:
                        status = "Suppressed"

                    # استخراج الكمية / المخزون
                    qty = 0
                    qty_elem = self.scraper.find_first_element(
                        ["input[data-column='quantity']", "[data-test-id='quantity-input']", "input.myi-quantity", "input[name*='quantity']"],
                        parent=row
                    )
                    if qty_elem:
                        qty_val = qty_elem.get_attribute("value") or qty_elem.text
                        m_qty = re.search(r"(\d+)", str(qty_val))
                        if m_qty:
                            qty = int(m_qty.group(1))
                    else:
                        if "غير متوفر" in text or "Out of Stock" in text or "غير متاح" in text:
                            qty = 0
                        else:
                            m_text_qty = re.search(r"(?:الكمية|المخزون|Quantity)[:\s]*(\d+)", text, re.IGNORECASE)
                            if m_text_qty:
                                qty = int(m_text_qty.group(1))

                    # استخراج العنوان
                    title = ""
                    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 10]
                    if lines:
                        title = lines[0]

                    if sku:
                        all_amazon_products[sku] = {
                            "sku": sku,
                            "asin": asin or "N/A",
                            "title": title,
                            "price": price,
                            "qty": qty,
                            "status": status,
                            "page": page
                        }
                        page_found_count += 1
            else:
                # محاولة استخراج كتل المنتجات عبر Regex مباشرة من HTML
                skus_found = set(re.findall(r"SKU[:\s\"]+([A-Za-z0-9_\-\.]+)", page_source))
                for sku in skus_found:
                    if len(sku) >= 4 and sku not in all_amazon_products:
                        all_amazon_products[sku] = {
                            "sku": sku,
                            "asin": "Detected",
                            "title": "Listed in Inventory",
                            "price": None,
                            "status": "Active",
                            "page": page
                        }
                        page_found_count += 1

            logger.info(f"تم رصد {page_found_count} منتج في الصفحة {page}.")

            # إذا كانت الصفحة خالية أو لا يوجد زر التالي، نتوقف
            if page_found_count == 0:
                logger.info("لا توجد منتجات إضافية، اكتمل الجلب.")
                break

            time.sleep(2)

        logger.info(f"إجمالي المنتجات المرصودة في أمازون: {len(all_amazon_products)} منتج.")
        return all_amazon_products

    def simulate_mock_inventory(self, salla_products: List[SallaProduct]) -> Dict[str, Dict[str, Any]]:
        """محاكاة قراءة المخزون في وضع الـ Dry-run لتجربة التقارير."""
        logger.info("[وضع المحاكاة] جلب بيانات تجريبية من ملفات الكتالوج الحالية...")
        mock_inventory = {}

        # استخدام amazon_ready.csv للمطابقة
        ar_path = BASE_DIR / "data" / "clean" / "amazon_ready.csv"
        if ar_path.exists():
            df_ar = pd.read_csv(ar_path)
            # نأخذ 60% من المنتجات كموجودة والباقي مفقودة لاختبار التقرير
            for idx, r in df_ar.iterrows():
                sku_str = str(r.get("sku", "")).strip()
                if not sku_str:
                    continue
                # محاكاة: وجود المنتج في أمازون
                mock_inventory[sku_str] = {
                    "sku": sku_str,
                    "asin": f"B0{abs(hash(sku_str)) % 100000000:08d}",
                    "title": str(r.get("name_ar", "")),
                    "price": float(r.get("price", 25.0)),
                    "status": "Active" if idx % 5 != 0 else "Inactive",
                    "page": 1
                }
        else:
            for idx, p in enumerate(salla_products):
                if idx % 3 != 0:  # محاكاة وجود ثلثي المنتجات
                    mock_inventory[p.sku] = {
                        "sku": p.sku,
                        "asin": f"B0{abs(hash(p.sku)) % 100000000:08d}",
                        "title": p.name,
                        "price": p.price,
                        "status": "Active",
                        "page": 1
                    }

        return mock_inventory

    def parse_amazon_inventory_html(self, html_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        قراءة ملف صفحة المخزون المحفوظ بصيغة HTML (التي تم حفظها من المتصفح عبر Ctrl+S).
        يستخرج المنتجات، الأسعار، الحالات، والأهم: المخزون والكميات.
        """
        from bs4 import BeautifulSoup

        logger.info(f"قراءة ملف HTML لصفحة المخزون: {html_path}")
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        soup = BeautifulSoup(content, "html.parser")
        products: Dict[str, Dict[str, Any]] = {}

        # 0. البحث عن منتجات أمازون الحديثة بتصميم Janus (ProductDetails & skucentral links)
        sku_links = soup.find_all("a", href=re.compile(r"skucentral\?mSku="))
        if sku_links:
            logger.info(f"تم رصد تصميم أمازون الحديث (Janus Layout): {len(sku_links)} منتج...")
            for a in sku_links:
                m = re.search(r"mSku=([^&]+)", a["href"])
                if not m:
                    continue
                sku = m.group(1).strip()

                curr = a
                row_container = None
                for _ in range(14):
                    if curr.parent:
                        curr = curr.parent
                        if "Available (FBM)" in curr.text or "Price" in curr.text or "Sales" in curr.text:
                            row_container = curr
                            break

                title = ""
                asin = "N/A"
                qty = 0
                price = None
                status = "Active"

                if row_container:
                    dp_link = row_container.find("a", href=re.compile(r"/dp/(B0[A-Z0-9]{8})"))
                    if dp_link:
                        title = dp_link.get_text(strip=True)
                        m_asin = re.search(r"/dp/(B0[A-Z0-9]{8})", dp_link["href"])
                        if m_asin:
                            asin = m_asin.group(1)

                    qty_box = row_container.select_one("div[class*='quantityInputBox'] kat-input, kat-input[value]")
                    if qty_box and qty_box.get("value") is not None:
                        try:
                            qty = int(qty_box.get("value"))
                        except Exception:
                            qty = 0

                    price_input = row_container.select_one("div[class*='priceInputRow'] kat-input, div[class*='VolusPriceInputComposite'] kat-input")
                    if price_input and price_input.get("value"):
                        try:
                            price = float(price_input.get("value"))
                        except Exception:
                            pass

                    text = row_container.get_text(separator=" ", strip=True)
                    if "Out of stock" in text or "غير نشط" in text:
                        status = "Inactive / Out of stock"
                    elif "Active" in text or "نشط" in text:
                        status = "Active"

                products[sku] = {
                    "sku": sku,
                    "asin": asin,
                    "title": title,
                    "price": price,
                    "qty": qty,
                    "status": status,
                    "page": 1
                }
            logger.info(f"✓ تم استخراج {len(products)} منتج بنجاح من واجهة Janus.")
            return products

        # 1. البحث عن الأسطر عبر محددات جدول المخزون التقليدي
        rows = soup.select(
            "table tbody tr, div[data-test-id='inventory-row'], tr[id^='myi-row-'], .myi-table-row, [data-row-id]"
        )
        for row in rows:
            text = row.get_text(separator=" ", strip=True)
            html = str(row)
            if not text and not html:
                continue

            # استخراج SKU
            sku = None
            sku_match = re.search(r"SKU[:\s]+([A-Za-z0-9_\-\.]+)", text)
            if sku_match:
                sku = sku_match.group(1).strip()
            else:
                elem = row.select_one("[data-column='sku'], .myi-sku, [data-test-id='sku']")
                if elem:
                    sku = elem.get_text().replace("SKU:", "").strip()

            # استخراج ASIN
            asin = "N/A"
            asin_match = re.search(r"\b(B0[A-Z0-9]{8})\b", text + " " + html)
            if asin_match:
                asin = asin_match.group(1)

            # استخراج السعر
            price = None
            price_match = re.search(r"(?:SAR|ر\.س|\$)\s*(\d+(?:\.\d+)?)", text)
            if price_match:
                price = float(price_match.group(1))
            else:
                num_matches = re.findall(r"(\d+\.\d{2})", text)
                if num_matches:
                    price = float(num_matches[0])

            # استخراج الحالة
            status = "Active"
            if any(w in text for w in ["غير نشط", "Inactive", "Out of Stock"]):
                status = "Inactive"
            elif any(w in text for w in ["محظور", "Suppressed", "محجوب"]):
                status = "Suppressed"

            # استخراج الكمية / المخزون
            qty = 0
            qty_input = row.select_one(
                "input[data-column='quantity'], [data-test-id='quantity-input'], input.myi-quantity, input[name*='quantity']"
            )
            if qty_input and qty_input.get("value"):
                m_qty = re.search(r"(\d+)", qty_input["value"])
                if m_qty:
                    qty = int(m_qty.group(1))
            else:
                if any(w in text for w in ["غير متوفر", "Out of Stock", "غير متاح"]):
                    qty = 0
                else:
                    m_text_qty = re.search(r"(?:الكمية|المخزون|Quantity)[:\s]*(\d+)", text, re.IGNORECASE)
                    if m_text_qty:
                        qty = int(m_text_qty.group(1))

            # العنوان
            title = ""
            title_elem = row.select_one("a[href*='/dp/'], [data-column='title'], .myi-title")
            if title_elem:
                title = title_elem.get_text().strip()

            if sku:
                products[sku] = {
                    "sku": sku,
                    "asin": asin,
                    "title": title,
                    "price": price,
                    "qty": qty,
                    "status": status,
                    "page": 1
                }

        # 2. خطة بديلة إذا كانت الصفحة لا تحتوي على جداول عادية بل نصوص مضمنة
        if not products:
            logger.info("لم يتم العثور على أسطر جدول مباشرة، جاري فحص جميع معرّفات الـ SKU في الصفحة...")
            skus_found = re.findall(r"SKU[:\s\"]+([A-Za-z0-9_\-\.]{4,})", content)
            for sku in set(skus_found):
                products[sku] = {
                    "sku": sku,
                    "asin": "N/A",
                    "title": "",
                    "price": None,
                    "qty": 0,
                    "status": "Active",
                    "page": 1
                }

        logger.info(f"✓ تم استخراج {len(products)} منتج بنجاح من ملف HTML.")
        return products

    def parse_amazon_report_tsv(self, report_path: Path) -> Dict[str, Dict[str, Any]]:
        """
        قراءة تقرير المخزون الرسمي المنزّل من أمازون (All Listings Report / Active Listings Report).
        يحتوي الملف على أعمدة:
        seller-sku, asin1, item-name, price, quantity, status
        """
        logger.info(f"قراءة تقرير مخزون أمازون الرسمي: {report_path}")
        df = pd.read_csv(report_path, sep="\t", encoding="utf-8", on_bad_lines="skip")
        products = {}

        col_map = {str(c).lower().strip(): c for c in df.columns}
        sku_col = col_map.get("seller-sku") or col_map.get("sku")
        asin_col = col_map.get("asin1") or col_map.get("asin")
        title_col = col_map.get("item-name") or col_map.get("title")
        price_col = col_map.get("price")
        qty_col = col_map.get("quantity") or col_map.get("qty")
        status_col = col_map.get("status")

        for _, row in df.iterrows():
            if not sku_col:
                continue
            sku = str(row.get(sku_col, "")).strip()
            if not sku or sku == "nan":
                continue

            asin = str(row.get(asin_col, "N/A")).strip() if asin_col else "N/A"
            title = str(row.get(title_col, "")).strip() if title_col else ""

            price = None
            if price_col and pd.notna(row.get(price_col)):
                try:
                    price = float(row.get(price_col))
                except Exception:
                    pass

            qty = 0
            if qty_col and pd.notna(row.get(qty_col)):
                try:
                    qty = int(float(row.get(qty_col)))
                except Exception:
                    qty = 0

            status = str(row.get(status_col, "Active")).strip() if status_col else "Active"

            products[sku] = {
                "sku": sku,
                "asin": asin,
                "title": title,
                "price": price,
                "qty": qty,
                "status": status,
                "page": 1
            }

        logger.info(f"✓ تم استخراج {len(products)} منتج بنجاح من تقرير أمازون الرسمي.")
        return products

    def run_audit(
        self,
        dry_run: bool = False,
        html_path: Optional[Path] = None,
        report_path: Optional[Path] = None
    ):
        """تنفيذ الفحص والمقارنة واستخراج التقرير الشامل."""
        salla_products = self.load_salla_catalog()

        if dry_run:
            amazon_inventory = self.simulate_mock_inventory(salla_products)
        elif html_path:
            amazon_inventory = self.parse_amazon_inventory_html(Path(html_path))
        elif report_path:
            amazon_inventory = self.parse_amazon_report_tsv(Path(report_path))
        else:
            try:
                amazon_inventory = self.scrape_all_amazon_inventory()
            finally:
                if self.scraper:
                    self.scraper.close()

        # بناء فهرس ذكي للبحث في مخزون أمازون يدعم الـ SKU مع -V2 ومع/بدون الأصفار والباركود
        amz_index: Dict[str, Dict[str, Any]] = {}
        for amz_sku, item in amazon_inventory.items():
            amz_index[amz_sku] = item
            clean_sku = re.sub(r"-[vV]\d+$", "", str(amz_sku)).strip()
            amz_index[clean_sku] = item
            amz_index[clean_sku.lstrip("0")] = item
            amz_index[str(amz_sku).lstrip("0")] = item
            if item.get("asin") and item["asin"] != "N/A":
                amz_index[item["asin"]] = item

        # تجهيز قوائم المنتجات الموجودة وغير الموجودة
        found_products: List[Dict[str, Any]] = []
        missing_products: List[Dict[str, Any]] = []

        for p in salla_products:
            sku = p.sku.strip()
            barcode = (p.barcode or "").strip()
            clean_salla_sku = re.sub(r"\.0$", "", sku).strip()
            clean_salla_barcode = re.sub(r"\.0$", "", barcode).strip()

            # محاولة المطابقة بالـ SKU أو الباركود مع إزالة الأصفار و -V2
            amz_item = (
                amz_index.get(clean_salla_sku)
                or amz_index.get(clean_salla_sku.lstrip("0"))
                or amz_index.get(clean_salla_barcode)
                or amz_index.get(clean_salla_barcode.lstrip("0"))
                or amazon_inventory.get(sku)
                or amazon_inventory.get(barcode)
            )

            if amz_item:
                amz_price = amz_item.get("price")
                amz_qty = amz_item.get("qty", 0)
                is_zero_stock = (amz_qty == 0)
                price_diff = None
                if amz_price is not None and p.price:
                    price_diff = round(amz_price - p.price, 2)

                found_products.append({
                    "رمز SKU في سلة": sku,
                    "الباركود": barcode or "غير محدد",
                    "معرف أمازون ASIN": amz_item.get("asin", "N/A"),
                    "اسم المنتج في سلة": p.name,
                    "عنوان المنتج في أمازون": amz_item.get("title") or p.name,
                    "سعر سلة (SAR)": p.price,
                    "سعر أمازون (SAR)": amz_price if amz_price is not None else "غير متوفر",
                    "فرق السعر": f"{price_diff:+} SAR" if price_diff is not None else "مطابق",
                    "الكمية في أمازون": amz_qty,
                    "فحص المخزون صفر": "✓ صفر (مضبوط)" if is_zero_stock else f"⚠ ليس صفراً ({amz_qty})",
                    "حالة الإدراج في أمازون": amz_item.get("status", "Active"),
                    "حالة المنتج في سلة": p.status or "متاح",
                    "تصنيف المنتج": p.category or "",
                    "رابط الصورة في سلة": p.images[0] if p.images else "",
                })
            else:
                missing_products.append({
                    "رمز SKU في سلة": sku,
                    "الباركود الدولي": barcode or "مفقود",
                    "اسم المنتج المفقود": p.name,
                    "سعر البيع في سلة (SAR)": p.price,
                    "السعر المخفض": p.sale_price or "",
                    "حالة المنتج في سلة": p.status or "متاح",
                    "الماركة": p.brand or "قطاف الطبيعة",
                    "القسم / التصنيف": p.category or "",
                    "الوزن": f"{p.weight or ''} {p.weight_unit or ''}".strip(),
                    "رابط الصورة الأساسية": p.images[0] if p.images else "",
                    "حالة الوجود على أمازون": "غير موجود (مفقود)",
                    "الإجراء المطلوب": "إضافة ورفع المنتج إلى أمازون",
                })

        # طباعة الملخص على الشاشة
        total_salla = len(salla_products)
        total_found = len(found_products)
        total_missing = len(missing_products)
        coverage_pct = round((total_found / total_salla * 100), 1) if total_salla else 0
        zero_stock_count = sum(1 for item in found_products if item.get("الكمية في أمازون") == 0)
        non_zero_stock_count = total_found - zero_stock_count

        safe_print("\n" + "=" * 80)
        safe_print("           تقرير فحص مخزون أمازون ومطابقته مع سلة")
        safe_print("=" * 80)
        safe_print(f"  إجمالي منتجات سلة المفحوصة:             {total_salla}")
        safe_print(f"  المنتجات الموجودة على أمازون:           {total_found}  (✓)")
        safe_print(f"  المنتجات المفقودة (غير مدرجة):         {total_missing}  (✗)")
        safe_print(f"  المنتجات التي مخزونها = 0 (مطابق):       {zero_stock_count}  (✓)")
        if non_zero_stock_count > 0:
            safe_print(f"  المنتجات التي مخزونها > 0 (تحتاج تصفير):  {non_zero_stock_count}  (⚠)")
        safe_print(f"  نسبة التواجد على أمازون:                {coverage_pct}%")
        safe_print("=" * 80 + "\n")

        # تصدير ملفات التقارير
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        excel_path = self.output_dir / f"تقرير_حالة_منتجات_أمازون_{timestamp}.xlsx"
        latest_excel = self.output_dir / "تقرير_حالة_منتجات_أمازون_المحدث.xlsx"

        csv_found_path = self.output_dir / "amazon_products_found.csv"
        csv_missing_path = self.output_dir / "amazon_products_missing.csv"

        # حفظ CSV
        pd.DataFrame(found_products).to_csv(csv_found_path, index=False, encoding="utf-8-sig")
        pd.DataFrame(missing_products).to_csv(csv_missing_path, index=False, encoding="utf-8-sig")

        # إنشاء وتنسيق ملف الإكسيل الاحترافي بتبويبين
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        wb = openpyxl.Workbook()

        # تبويب 1: ملخص تنفيذي
        ws_sum = wb.active
        ws_sum.title = "ملخص الفحص"
        ws_sum.views.sheetView[0].rightToLeft = True

        ws_sum.append(["تقرير مطابقة منتجات سلة مع مخزون أمازون المباشر"])
        ws_sum.append([])
        ws_sum.append(["المؤشر", "القيمة"])
        ws_sum.append(["إجمالي منتجات سلة", total_salla])
        ws_sum.append(["المنتجات المتوفرة والمدرجة في أمازون (✓)", total_found])
        ws_sum.append(["المنتجات المفقودة وغير المدرجة في أمازون (✗)", total_missing])
        ws_sum.append(["نسبة التغطية على أمازون", f"{coverage_pct}%"])
        ws_sum.append(["رابط صفحة المخزون المفحوصة", "sellercentral.amazon.sa/myinventory/inventory"])
        ws_sum.append(["تاريخ ووقت الفحص", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        # تنسيق تبويب الملخص
        header_fill_blue = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_font_white = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        ws_sum.cell(1, 1).font = Font(name="Segoe UI", size=14, bold=True, color="1E3A8A")
        ws_sum.cell(3, 1).fill = header_fill_blue
        ws_sum.cell(3, 1).font = header_font_white
        ws_sum.cell(3, 2).fill = header_fill_blue
        ws_sum.cell(3, 2).font = header_font_white
        ws_sum.column_dimensions["A"].width = 45
        ws_sum.column_dimensions["B"].width = 25

        thin_border = Border(
            left=Side(style="thin", color="E5E7EB"),
            right=Side(style="thin", color="E5E7EB"),
            top=Side(style="thin", color="E5E7EB"),
            bottom=Side(style="thin", color="E5E7EB")
        )

        # تبويب 2: المنتجات الموجودة (أخضر)
        ws_found = wb.create_sheet(title="المنتجات الموجودة في أمازون")
        ws_found.views.sheetView[0].rightToLeft = True

        if found_products:
            headers_found = list(found_products[0].keys())
            ws_found.append(headers_found)
            fill_green_header = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")
            for c_idx in range(1, len(headers_found) + 1):
                cell = ws_found.cell(1, c_idx)
                cell.fill = fill_green_header
                cell.font = header_font_white
                cell.alignment = Alignment(horizontal="center", vertical="center")

            fill_green_light = PatternFill(start_color="F0FDF4", end_color="F0FDF4", fill_type="solid")
            for item in found_products:
                ws_found.append(list(item.values()))
                curr = ws_found.max_row
                for c_idx in range(1, len(headers_found) + 1):
                    c = ws_found.cell(curr, c_idx)
                    c.border = thin_border
                    c.fill = fill_green_light

            for col in ws_found.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                ws_found.column_dimensions[col_letter].width = max(14, min(max_len + 3, 50))

        # تبويب 3: المنتجات المفقودة (أحمر)
        ws_miss = wb.create_sheet(title="المنتجات المفقودة (غير موجودة)")
        ws_miss.views.sheetView[0].rightToLeft = True

        if missing_products:
            headers_miss = list(missing_products[0].keys())
            ws_miss.append(headers_miss)
            fill_red_header = PatternFill(start_color="991B1B", end_color="991B1B", fill_type="solid")
            for c_idx in range(1, len(headers_miss) + 1):
                cell = ws_miss.cell(1, c_idx)
                cell.fill = fill_red_header
                cell.font = header_font_white
                cell.alignment = Alignment(horizontal="center", vertical="center")

            fill_red_light = PatternFill(start_color="FEF2F2", end_color="FEF2F2", fill_type="solid")
            for item in missing_products:
                ws_miss.append(list(item.values()))
                curr = ws_miss.max_row
                for c_idx in range(1, len(headers_miss) + 1):
                    c = ws_miss.cell(curr, c_idx)
                    c.border = thin_border
                    c.fill = fill_red_light

            for col in ws_miss.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                ws_miss.column_dimensions[col_letter].width = max(14, min(max_len + 3, 50))

        # حفظ الملف
        wb.save(excel_path)
        try:
            wb.save(latest_excel)
        except (PermissionError, IOError):
            pass

        safe_print("تم إنشاء التقارير بنجاح:")
        safe_print(f"  • ملف الإكسيل التفاعلي الشامل:  {excel_path}")
        safe_print(f"  • ملف المنتجات الموجودة (CSV):   {csv_found_path}")
        safe_print(f"  • ملف المنتجات المفقودة (CSV):   {csv_missing_path}")
        safe_print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="فحص مخزون أمازون المباشر واستخراج تقرير بالمنتجات الموجودة والمفقودة مقارنة بسلة."
    )
    parser.add_argument(
        "--excel", "-e",
        type=str,
        default="data/clean/amazon_ready.csv",
        help="مسار ملف المنتجات الجاهزة للمطابقة (افتراضي: 290 منتج جاهز لأمازون)."
    )
    parser.add_argument(
        "--profile-dir", "-p",
        type=str,
        default="chrome_profile",
        help="مسار مجلد جلسة كروم لحفظ تسجيل الدخول ورمز التحقق 2FA."
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="inventory_audit_reports",
        help="المجلد الذي سيتم حفظ التقارير داخله."
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=15,
        help="أقصى عدد صفحات للمخزون يتم فحصها (افتراضي: 15 صفحة)."
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="عدد المنتجات في كل صفحة (25 أو 50 أو 100)."
    )
    parser.add_argument(
        "--email",
        type=str,
        default="lawazimplus93@gmail.com",
        help="بريد تسجيل الدخول لأمازون Seller Central."
    )
    parser.add_argument(
        "--password",
        type=str,
        default="Qitaf@123456",
        help="كلمة مرور أمازون Seller Central."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="تشغيل المتصفح في الخلفية بدون واجهة مرئية."
    )
    parser.add_argument(
        "--html",
        type=str,
        default=None,
        help="مسار ملف HTML لصفحة المخزون (المحفوظة مسبقاً عبر Ctrl+S) لفحصها فوراً دون فتح المتصفح."
    )
    parser.add_argument(
        "--report",
        type=str,
        default=None,
        help="مسار ملف تقرير المخزون الرسمي المنزّل من أمازون (All Listings Report / .txt / .tsv)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="تشغيل تجريبي بدون فتح المتصفح لاختبار التقارير."
    )

    args = parser.parse_args()

    excel_file = Path(args.excel)
    if not excel_file.exists():
        # محاولة البحث عن بديل
        alt = Path("data/clean/amazon_ready.csv")
        if alt.exists():
            excel_file = alt
        else:
            print(f"خطأ: ملف سلة غير موجود في المسار: {excel_file}")
            sys.exit(1)

    # الكشف التلقائي عن ملفات HTML المحفوظة في المجلد في حال لم يتم تحديد خيار
    html_file = Path(args.html) if args.html else None
    if not html_file and not args.report and not args.dry_run:
        for cand in ["Manage Your Inventory.html", "amazon_inventory.html"]:
            p_cand = Path(cand)
            if p_cand.exists():
                html_file = p_cand
                logger.info(f"تم رصد ملف مخزون محفوظ تلقائياً: {cand}")
                break

    auditor = LiveInventoryAuditor(
        excel_path=excel_file,
        profile_dir=Path(args.profile_dir),
        output_dir=Path(args.output_dir),
        email=args.email,
        password=args.password,
        headless=args.headless,
        max_pages=args.pages,
        page_size=args.page_size
    )

    auditor.run_audit(
        dry_run=args.dry_run,
        html_path=html_file,
        report_path=Path(args.report) if args.report else None
    )


if __name__ == "__main__":
    main()
