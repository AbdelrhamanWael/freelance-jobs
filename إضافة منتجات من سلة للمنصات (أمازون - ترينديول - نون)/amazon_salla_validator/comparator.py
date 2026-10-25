"""
Product Data Comparator Engine.
Compares Salla source records against live Amazon listings and produces
detailed field-by-field diffs with similarity scoring and mismatch reasons.
"""

import re
from difflib import SequenceMatcher
from typing import List, Optional

from .config import (
    SallaProduct, AmazonProduct, FieldDiff, ProductComparison, ValidatorConfig
)


def normalize_text_ar_en(text: Optional[str]) -> str:
    """
    Normalizes Arabic and English text:
    - Removes Arabic diacritics (tashkeel), tatweel (kashida).
    - Unifies alef forms (أ, إ, آ -> ا), taa marbuta (ة -> ه), yaa (ى -> ي).
    - Normalizes multiple spaces and lowercases English.
    """
    if not text:
        return ""

    t = str(text)

    # Remove Arabic Tashkeel
    t = re.sub(r"[\u064B-\u0652\u0670]", "", t)
    # Remove Tatweel (ـ)
    t = t.replace("\u0640", "")

    # Unify Arabic letters
    t = re.sub(r"[أإآ]", "ا", t)
    t = t.replace("ة", "ه")
    t = t.replace("ى", "ي")

    # Remove non-word punctuation
    t = re.sub(r"[^\w\s\d]", " ", t)

    # Normalize whitespace
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculates string similarity ratio between 0.0 and 1.0."""
    n1 = normalize_text_ar_en(text1)
    n2 = normalize_text_ar_en(text2)
    if not n1 and not n2:
        return 1.0
    if not n1 or not n2:
        return 0.0
    if n1 == n2:
        return 1.0
    # Also check if one contains the other
    if n1 in n2 or n2 in n1:
        shorter_len = min(len(n1), len(n2))
        longer_len = max(len(n1), len(n2))
        if shorter_len / longer_len > 0.6:
            return max(0.85, SequenceMatcher(None, n1, n2).ratio())
    return SequenceMatcher(None, n1, n2).ratio()


class ProductComparator:
    """Compares SallaProduct against AmazonProduct."""

    def __init__(self, config: Optional[ValidatorConfig] = None):
        self.config = config or ValidatorConfig()

    def compare(self, salla: SallaProduct, amazon: Optional[AmazonProduct]) -> ProductComparison:
        """Runs comprehensive field-level comparison."""
        diffs: List[FieldDiff] = []

        if not amazon or not amazon.found:
            err_msg = amazon.error if amazon else "Product not found on Amazon"
            diffs.append(FieldDiff(
                field_name="Catalog Presence",
                expected_val="Listed in Amazon Inventory",
                actual_val="Not Found (404 / 0 search results)",
                matched=False,
                status_icon="✗",
                difference_note=err_msg or "Listing does not exist in Amazon Seller Central",
                severity="MISMATCH",
            ))
            return ProductComparison(
                identifier=salla.sku,
                sku=salla.sku,
                asin="N/A",
                salla_name=salla.name,
                amazon_title="NOT FOUND",
                overall_match=False,
                diffs=diffs,
                error_message=err_msg,
            )

        # 1. Compare SKU
        sku_matched = (salla.sku.strip() == (amazon.sku or "").strip())
        diffs.append(FieldDiff(
            field_name="SKU",
            expected_val=salla.sku,
            actual_val=amazon.sku or "Missing",
            matched=sku_matched,
            status_icon="✓" if sku_matched else "✗",
            difference_note="" if sku_matched else f"SKU mismatch (Expected '{salla.sku}', Got '{amazon.sku}')",
            severity="MATCH" if sku_matched else "MISMATCH",
        ))

        # 2. Check ASIN
        asin_val = amazon.asin or "Not assigned"
        diffs.append(FieldDiff(
            field_name="ASIN",
            expected_val="Assigned B0...",
            actual_val=asin_val,
            matched=bool(amazon.asin and amazon.asin.startswith("B0")),
            status_icon="✓" if (amazon.asin and amazon.asin.startswith("B0")) else "⚠",
            difference_note="" if amazon.asin else "ASIN not detected or listing is a draft",
            severity="MATCH" if amazon.asin else "WARNING",
        ))

        # 3. Compare Title
        title_sim = calculate_similarity(salla.name, amazon.title or "")
        title_matched = title_sim >= self.config.title_similarity_threshold
        sim_pct = int(title_sim * 100)

        if title_matched:
            note = f"Match ({sim_pct}% similarity)"
            icon = "✓"
            sev = "MATCH"
        else:
            note = f"Title discrepancy ({sim_pct}% similarity below {int(self.config.title_similarity_threshold*100)}% threshold)"
            icon = "✗"
            sev = "MISMATCH"

        diffs.append(FieldDiff(
            field_name="Product Title",
            expected_val=salla.name,
            actual_val=amazon.title or "Empty",
            matched=title_matched,
            status_icon=icon,
            difference_note=note,
            severity=sev,
        ))

        # 4. Compare Price
        expected_price = salla.sale_price if (salla.sale_price and salla.sale_price > 0) else salla.price
        actual_price = amazon.price

        if actual_price is None or actual_price <= 0:
            diffs.append(FieldDiff(
                field_name="Price",
                expected_val=f"{expected_price:.2f} SAR",
                actual_val="Missing / Price not displayed",
                matched=False,
                status_icon="✗",
                difference_note="Price could not be retrieved from Amazon listing",
                severity="MISMATCH",
            ))
        else:
            # Check price tolerance (absolute difference)
            price_diff = abs(expected_price - actual_price)
            price_matched = price_diff <= self.config.price_tolerance

            # Also check base price if sale price was checked
            if not price_matched and salla.sale_price:
                if abs(salla.price - actual_price) <= self.config.price_tolerance:
                    price_matched = True
                    expected_price = salla.price

            if price_matched:
                price_note = f"Exact match ({actual_price:.2f} {amazon.currency or 'SAR'})"
                price_icon = "✓"
                price_sev = "MATCH"
            else:
                diff_val = actual_price - expected_price
                sign = "+" if diff_val > 0 else ""
                price_note = f"Price mismatch ({sign}{diff_val:.2f} {amazon.currency or 'SAR'} difference)"
                price_icon = "✗"
                price_sev = "MISMATCH"

            diffs.append(FieldDiff(
                field_name="Price",
                expected_val=f"{expected_price:.2f} SAR",
                actual_val=f"{actual_price:.2f} {amazon.currency or 'SAR'}",
                matched=price_matched,
                status_icon=price_icon,
                difference_note=price_note,
                severity=price_sev,
            ))

        # 5. Compare Images
        salla_img_count = len(salla.images)
        amazon_img_count = amazon.image_count or len(amazon.images)

        if amazon_img_count == 0:
            diffs.append(FieldDiff(
                field_name="Images",
                expected_val=f"{salla_img_count} images",
                actual_val="0 images (Missing main image)",
                matched=False,
                status_icon="✗",
                difference_note="No images found on Amazon listing. Listing may be suppressed.",
                severity="MISMATCH",
            ))
        else:
            img_note = f"Amazon has {amazon_img_count} image(s), Salla has {salla_img_count}"
            img_icon = "✓" if amazon_img_count >= 1 else "✗"
            diffs.append(FieldDiff(
                field_name="Images",
                expected_val=f"{salla_img_count} images ({salla.images[0] if salla.images else 'None'})",
                actual_val=f"{amazon_img_count} images ({amazon.images[0] if amazon.images else 'None'})",
                matched=amazon_img_count >= 1,
                status_icon=img_icon,
                difference_note=img_note,
                severity="MATCH" if amazon_img_count >= 1 else "MISMATCH",
            ))

        # 6. Compare Description / Bullet Points (if detail page scraped)
        if amazon.detail_page_scraped:
            amazon_bullets_count = len(amazon.bullet_points)
            salla_bullets_count = len(salla.bullet_points)
            bullets_present = amazon_bullets_count > 0

            bullets_diff = FieldDiff(
                field_name="Bullet Points",
                expected_val=f"{salla_bullets_count} bullets in Salla",
                actual_val=f"{amazon_bullets_count} bullets on Amazon",
                matched=bullets_present,
                status_icon="✓" if bullets_present else "⚠",
                difference_note="" if bullets_present else "Listing lacks bullet points on live page",
                severity="MATCH" if bullets_present else "WARNING",
            )
            diffs.append(bullets_diff)

            # Description presence
            desc_present = bool(amazon.description and len(amazon.description) > 20)
            diffs.append(FieldDiff(
                field_name="Description",
                expected_val=f"{len(salla.description_text or '')} characters",
                actual_val=f"{len(amazon.description or '')} characters",
                matched=desc_present,
                status_icon="✓" if desc_present else "⚠",
                difference_note="" if desc_present else "Product description empty on Amazon",
                severity="MATCH" if desc_present else "WARNING",
            ))

        # 7. Check Listing Status
        if amazon.status:
            is_active = any(act in amazon.status.lower() for act in ["active", "نشط", "available", "متاح"])
            diffs.append(FieldDiff(
                field_name="Listing Status",
                expected_val="Active",
                actual_val=amazon.status,
                matched=is_active,
                status_icon="✓" if is_active else "⚠",
                difference_note="" if is_active else f"Listing status is '{amazon.status}' (Check for suppression)",
                severity="MATCH" if is_active else "WARNING",
            ))

        # Determine overall match
        # Critical fields: Title, Price, SKU, Images
        critical_mismatches = [
            d for d in diffs
            if d.severity == "MISMATCH" and d.field_name in ["SKU", "Product Title", "Price", "Images", "Catalog Presence"]
        ]
        overall_matched = len(critical_mismatches) == 0

        return ProductComparison(
            identifier=salla.sku,
            sku=salla.sku,
            asin=amazon.asin or "N/A",
            salla_name=salla.name,
            amazon_title=amazon.title or "N/A",
            overall_match=overall_matched,
            diffs=diffs,
            error_message=None,
        )
