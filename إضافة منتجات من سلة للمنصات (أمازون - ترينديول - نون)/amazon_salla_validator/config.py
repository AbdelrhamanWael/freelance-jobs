"""
Configuration and data models for Salla vs Amazon Product Data Validator.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Root Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Marketplace Configuration
MARKETPLACE_CONFIGS: Dict[str, Dict[str, str]] = {
    "SA": {
        "name": "Saudi Arabia",
        "currency": "SAR",
        "seller_central_url": "https://sellercentral.amazon.sa/myinventory/inventory?fulfilledBy=all&page=1&pageSize=50&sort=date_created_desc&status=all",
        "login_url": "https://sellercentral.amazon.sa/signin",
        "dp_base_url": "https://www.amazon.sa/dp/",
        "domain": "amazon.sa",
    },
    "AE": {
        "name": "United Arab Emirates",
        "currency": "AED",
        "seller_central_url": "https://sellercentral.amazon.ae/inventory",
        "login_url": "https://sellercentral.amazon.ae/signin",
        "dp_base_url": "https://www.amazon.ae/dp/",
        "domain": "amazon.ae",
    },
    "US": {
        "name": "United States",
        "currency": "USD",
        "seller_central_url": "https://sellercentral.amazon.com/inventory",
        "login_url": "https://sellercentral.amazon.com/signin",
        "dp_base_url": "https://www.amazon.com/dp/",
        "domain": "amazon.com",
    },
    "EG": {
        "name": "Egypt",
        "currency": "EGP",
        "seller_central_url": "https://sellercentral.amazon.eg/inventory",
        "login_url": "https://sellercentral.amazon.eg/signin",
        "dp_base_url": "https://www.amazon.eg/dp/",
        "domain": "amazon.eg",
    },
}

# Selectors for Amazon Seller Central Manage Inventory Page
SELLER_CENTRAL_SELECTORS = {
    "search_input": [
        "input[data-test-id='search-input']",
        "input#myi-search-input",
        "input#sc-search-field",
        "input[type='search']",
        "input.myi-search-input",
        "#search-box",
    ],
    "search_button": [
        "button[data-test-id='search-button']",
        "button#myi-search-button",
        "input[type='submit']",
        "button.myi-search-button",
    ],
    "inventory_rows": [
        "table[data-test-id='inventory-table'] tbody tr",
        ".myi-table tbody tr",
        "div[data-test-id='inventory-row']",
        "tr.myi-table-row",
        "tr[id^='myi-row-']",
    ],
    "sku": [
        "[data-test-id='sku']",
        "[data-column='sku']",
        ".myi-sku",
        ".sku-cell",
    ],
    "asin": [
        "[data-test-id='asin']",
        "[data-column='asin']",
        ".myi-asin",
        "a[href*='/dp/']",
    ],
    "title": [
        "[data-test-id='product-title']",
        "[data-column='title']",
        ".myi-title a",
        ".product-title a",
    ],
    "price": [
        "[data-test-id='price-input']",
        "[data-column='price'] input",
        "[data-column='price']",
        ".myi-price",
        ".price-cell",
    ],
    "status": [
        "[data-test-id='status']",
        "[data-column='status']",
        ".myi-status",
        ".status-cell",
    ],
    "image": [
        "img[data-test-id='product-image']",
        ".myi-image img",
        "td.image-cell img",
    ],
    "quantity": [
        "[data-test-id='quantity-input']",
        "[data-column='quantity'] input",
        "[data-column='quantity']",
        ".myi-quantity",
    ],
    "no_results": [
        "[data-test-id='empty-results']",
        ".myi-no-results",
        ".no-results-message",
        "div:contains('No records found')",
    ]
}

# Selectors for Live Product Detail Page (/dp/<ASIN>)
DETAIL_PAGE_SELECTORS = {
    "title": ["#productTitle", "h1#title", "span#productTitle"],
    "price": [
        ".a-price .a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#corePrice_feature_div .a-price .a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
    ],
    "bullets": [
        "#feature-bullets ul li span.a-list-item",
        "#featurebullets_feature_div ul li span",
    ],
    "description": [
        "#productDescription p",
        "#productDescription span",
        "#productDescription",
        "#aplus",
    ],
    "images": [
        "#altImages ul li img",
        "#imageBlock img",
        "#landingImage",
    ],
    "brand": [
        "#bylineInfo",
        "a#bylineInfo",
        "#brand",
    ],
}


@dataclass
class SallaProduct:
    """Represents a product parsed from Salla Excel export."""
    sku: str
    name: str
    price: float
    sale_price: Optional[float] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    weight: Optional[float] = None
    weight_unit: Optional[str] = None
    status: Optional[str] = None
    description_raw: Optional[str] = None
    description_text: Optional[str] = None
    bullet_points: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    raw_data: Dict[str, str] = field(default_factory=dict)


@dataclass
class AmazonProduct:
    """Represents live product data retrieved from Amazon."""
    sku: str
    asin: Optional[str] = None
    title: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    quantity: Optional[int] = None
    bullet_points: List[str] = field(default_factory=list)
    description: Optional[str] = None
    images: List[str] = field(default_factory=list)
    image_count: int = 0
    found: bool = False
    error: Optional[str] = None
    detail_page_scraped: bool = False


@dataclass
class FieldDiff:
    """Represents comparison details for a single product field."""
    field_name: str
    expected_val: str
    actual_val: str
    matched: bool
    status_icon: str  # '✓' or '✗' or '⚠'
    difference_note: str = ""
    severity: str = "INFO"  # 'MATCH', 'MISMATCH', 'WARNING', 'MISSING'


@dataclass
class ProductComparison:
    """Represents the overall comparison results for a product."""
    identifier: str
    sku: str
    asin: str
    salla_name: str
    amazon_title: str
    overall_match: bool
    diffs: List[FieldDiff] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass
class ValidatorConfig:
    """Global configuration settings for validation."""
    marketplace: str = "SA"
    excel_path: Optional[Path] = None
    output_dir: Path = BASE_DIR / "validation_reports"
    chrome_profile_dir: Optional[Path] = None
    headless: bool = False
    deep_check: bool = True  # Check live /dp/<ASIN> page for full bullets & description
    limit: Optional[int] = None
    request_delay_min: float = 2.0
    request_delay_max: float = 4.5
    title_similarity_threshold: float = 0.80
    price_tolerance: float = 0.05
    amazon_email: Optional[str] = None
    amazon_password: Optional[str] = None

    def __post_init__(self):
        if not self.amazon_email:
            self.amazon_email = os.getenv("AMAZON_EMAIL")
        if not self.amazon_password:
            self.amazon_password = os.getenv("AMAZON_PASSWORD")
        if not self.chrome_profile_dir and os.getenv("CHROME_PROFILE_DIR"):
            self.chrome_profile_dir = Path(os.getenv("CHROME_PROFILE_DIR"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
