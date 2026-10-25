"""
Unit and Integration Tests for Amazon vs Salla Product Data Validator.
"""

import unittest
from pathlib import Path
import tempfile
import json
import pandas as pd

from amazon_salla_validator.config import (
    SallaProduct, AmazonProduct, ValidatorConfig
)
from amazon_salla_validator.salla_reader import (
    SallaExcelReader, clean_html_text, normalize_price, normalize_sku
)
from amazon_salla_validator.comparator import ProductComparator
from amazon_salla_validator.reporter import ValidationReporter


class TestSallaReader(unittest.TestCase):
    """Tests for Salla export ingestion and HTML cleanup."""

    def test_clean_html_text(self):
        raw_html = (
            "<p>عسل طبيعي نقي 100% مستخلص من أزهار السدر البري</p>"
            "<ul><li>الوزن: 500 جرام</li><li>المنشأ: المملكة العربية السعودية</li></ul>"
        )
        cleaned_text, bullets = clean_html_text(raw_html)
        self.assertIn("عسل طبيعي نقي", cleaned_text)
        self.assertNotIn("<p>", cleaned_text)
        self.assertEqual(len(bullets), 2)
        self.assertEqual(bullets[0], "الوزن: 500 جرام")

    def test_normalize_sku(self):
        self.assertEqual(normalize_sku(6288202684011.0), "6288202684011")
        self.assertEqual(normalize_sku("6288202684011"), "6288202684011")
        self.assertEqual(normalize_sku("SKU-12345.0"), "SKU-12345")

    def test_normalize_price(self):
        self.assertEqual(normalize_price("15.50 SAR"), 15.50)
        self.assertEqual(normalize_price(" 25.0 ر.س "), 25.0)
        self.assertEqual(normalize_price(30.0), 30.0)

    def test_load_real_salla_export(self):
        real_file = Path("data/raw/salla_products_export.xlsx")
        if real_file.exists():
            reader = SallaExcelReader(real_file)
            products = reader.load_products(limit=5)
            self.assertGreater(len(products), 0)
            p1 = products[0]
            self.assertTrue(p1.sku)
            self.assertTrue(p1.name)
            self.assertGreater(p1.price, 0)
            self.assertTrue(len(p1.images) > 0)


class TestComparator(unittest.TestCase):
    """Tests for field-level comparison and discrepancy flagging."""

    def setUp(self):
        self.comparator = ProductComparator()

    def test_perfect_match(self):
        salla = SallaProduct(
            sku="SKU-TEST-01",
            name="حناء المدينة مطحونة 250 جرام",
            price=15.0,
            images=["https://cdn.salla.sa/test.jpg"],
            bullet_points=["طبيعي 100%", "خالٍ من الشوائب"]
        )
        amazon = AmazonProduct(
            sku="SKU-TEST-01",
            asin="B0ABC12345",
            title="حناء المدينة مطحونة 250 جرام",
            price=15.0,
            currency="SAR",
            status="Active",
            images=["https://m.media-amazon.com/test.jpg"],
            image_count=1,
            found=True,
            detail_page_scraped=True,
            bullet_points=["طبيعي 100%", "خالٍ من الشوائب"],
            description="مسحوق حناء طبيعي"
        )
        res = self.comparator.compare(salla, amazon)
        self.assertTrue(res.overall_match)
        # Check all icons are checkmarks
        self.assertTrue(all(d.matched for d in res.diffs if d.field_name in ["SKU", "Product Title", "Price"]))

    def test_price_and_title_mismatch(self):
        salla = SallaProduct(
            sku="SKU-TEST-02",
            name="زيت زيتون بكر ممتاز 1 لتر",
            price=45.0,
            images=["https://cdn.salla.sa/olive.jpg"],
        )
        amazon = AmazonProduct(
            sku="SKU-TEST-02",
            asin="B0DEF67890",
            title="خل تفاح طبيعي 500 مل",  # completely different product
            price=20.0,  # mismatch
            currency="SAR",
            status="Active",
            images=[],  # missing images
            image_count=0,
            found=True,
        )
        res = self.comparator.compare(salla, amazon)
        self.assertFalse(res.overall_match)

        # Title diff
        title_diff = next(d for d in res.diffs if d.field_name == "Product Title")
        self.assertFalse(title_diff.matched)
        self.assertEqual(title_diff.status_icon, "✗")

        # Price diff
        price_diff = next(d for d in res.diffs if d.field_name == "Price")
        self.assertFalse(price_diff.matched)
        self.assertIn("Price mismatch", price_diff.difference_note)

        # Images diff
        img_diff = next(d for d in res.diffs if d.field_name == "Images")
        self.assertFalse(img_diff.matched)

    def test_product_not_found(self):
        salla = SallaProduct(
            sku="SKU-MISSING-99",
            name="منتج تجريبي غير مدرج",
            price=10.0,
        )
        amazon = AmazonProduct(
            sku="SKU-MISSING-99",
            found=False,
            error="Not found in Seller Central inventory"
        )
        res = self.comparator.compare(salla, amazon)
        self.assertFalse(res.overall_match)
        self.assertEqual(res.amazon_title, "NOT FOUND")


class TestReporter(unittest.TestCase):
    """Tests report generation in CSV, JSON, and Excel formats."""

    def test_export_all_formats(self):
        salla1 = SallaProduct(sku="SKU-01", name="منتج تجريبي 1", price=25.0)
        amazon1 = AmazonProduct(sku="SKU-01", asin="B011111111", title="منتج تجريبي 1", price=25.0, found=True, images=["img1"])

        salla2 = SallaProduct(sku="SKU-02", name="منتج تجريبي 2", price=50.0)
        amazon2 = AmazonProduct(sku="SKU-02", asin="B022222222", title="منتج تجريبي 2", price=65.0, found=True, images=["img2"])

        comparator = ProductComparator()
        c1 = comparator.compare(salla1, amazon1)
        c2 = comparator.compare(salla2, amazon2)

        with tempfile.TemporaryDirectory() as tmpdir:
            out_dir = Path(tmpdir)
            reporter = ValidationReporter([c1, c2], output_dir=out_dir)

            exported = reporter.export_all()

            # Verify files exist and are non-empty
            self.assertTrue(exported["csv"].exists())
            self.assertTrue(exported["json"].exists())
            self.assertTrue(exported["excel"].exists())

            self.assertGreater(exported["csv"].stat().st_size, 100)
            self.assertGreater(exported["json"].stat().st_size, 100)
            self.assertGreater(exported["excel"].stat().st_size, 1000)

            # Check JSON contents
            with open(exported["json"], "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertEqual(data["summary"]["total_products"], 2)
                self.assertEqual(data["summary"]["overall_matched"], 1)
                self.assertEqual(data["summary"]["overall_mismatched"], 1)

            # Check CSV contents
            df = pd.read_csv(exported["csv"])
            self.assertIn("Match Status", df.columns)
            self.assertIn("✓", df["Match Status"].values)
            self.assertIn("✗", df["Match Status"].values)


if __name__ == "__main__":
    unittest.main()
