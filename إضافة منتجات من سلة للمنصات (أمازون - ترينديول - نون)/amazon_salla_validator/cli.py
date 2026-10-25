"""
Command-line interface and execution orchestrator for Amazon vs Salla Validator.
"""

import sys
import argparse
import getpass
import logging
from pathlib import Path
from typing import Optional, List

from .config import ValidatorConfig, ProductComparison, AmazonProduct
from .salla_reader import SallaExcelReader
from .amazon_scraper import AmazonScraper
from .comparator import ProductComparator
from .reporter import ValidationReporter


def setup_logging(verbose: bool = False):
    """Sets up unified logging."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )


def find_default_excel() -> Optional[Path]:
    """Finds available Salla export files in default workspace directories."""
    candidates = [
        Path("data/raw/salla_products_export.xlsx"),
        Path("data/clean/amazon_ready.csv"),
        Path("qitafaltabiea_13-09-2026-01-48_OZjH2K61peroLtoTcf55nd6F8O8zBkXe1ubO1qRS_products.xlsx"),
        Path("جميع_بيانات_منتجات_أمازون_الـ134_جاهزة.xlsx"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def parse_arguments() -> argparse.Namespace:
    """Parses CLI flags and arguments."""
    parser = argparse.ArgumentParser(
        description="Validate product data accuracy between Salla Excel exports and Amazon Seller Central."
    )

    parser.add_argument(
        "--excel", "-e",
        type=str,
        default=None,
        help="Path to Salla Excel (.xlsx, .xlsm, .xls) or CSV export file."
    )
    parser.add_argument(
        "--marketplace", "-m",
        type=str,
        default="SA",
        choices=["SA", "AE", "US", "EG"],
        help="Target Amazon marketplace (default: SA for Amazon Saudi Arabia)."
    )
    parser.add_argument(
        "--profile-dir", "-p",
        type=str,
        default="chrome_profile",
        help="Path to persistent Chrome user profile directory to keep login session active across runs."
    )
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="Amazon Seller Central login email."
    )
    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Amazon Seller Central login password (can also be entered securely via prompt or .env)."
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="Limit number of products to validate (useful for quick testing)."
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="validation_reports",
        help="Directory to save generated CSV, JSON, and Excel audit reports."
    )
    parser.add_argument(
        "--no-deep-check",
        action="store_true",
        help="Only scrape Seller Central inventory table without navigating to live /dp/<ASIN> pages."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (Note: first-time login requiring 2FA should run non-headless)."
    )
    parser.add_argument(
        "--delay-min",
        type=float,
        default=2.0,
        help="Minimum request delay in seconds to avoid rate limiting (default: 2.0)."
    )
    parser.add_argument(
        "--delay-max",
        type=float,
        default=4.0,
        help="Maximum request delay in seconds to avoid rate limiting (default: 4.0)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validation in simulation mode without connecting to live browser. Useful for testing reporting and comparison."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable detailed debug logging."
    )

    return parser.parse_args()


def run_validation(
    excel_path: Path,
    config: ValidatorConfig,
    scraper: Optional[AmazonScraper] = None,
    dry_run: bool = False
) -> List[ProductComparison]:
    """Executes the validation workflow across all products."""
    logger = logging.getLogger(__name__)

    # 1. Ingest Salla Excel
    logger.info(f"Reading Salla products from: {excel_path}")
    reader = SallaExcelReader(excel_path)
    products = reader.load_products(limit=config.limit)
    logger.info(f"Loaded {len(products)} products from Salla export.")

    if not products:
        logger.warning("No products found to validate.")
        return []

    comparator = ProductComparator(config)
    comparisons: List[ProductComparison] = []
    total = len(products)

    # If Dry Run / Simulation mode requested
    if dry_run:
        print("\n" + "=" * 80)
        print(f"  RUNNING IN SIMULATION / DRY-RUN MODE ({total} PRODUCTS)")
        print("=" * 80 + "\n")

        # Load local amazon_ready if available for realistic simulation
        amazon_ready_map = {}
        ar_path = Path("data/clean/amazon_ready.csv")
        if ar_path.exists():
            try:
                import pandas as pd
                df_ar = pd.read_csv(ar_path)
                for _, r in df_ar.iterrows():
                    sku_key = str(r.get("sku", "")).strip()
                    if sku_key:
                        amazon_ready_map[sku_key] = r
            except Exception:
                pass

        for idx, salla_prod in enumerate(products, 1):
            print(f"[{idx}/{total}] [SIMULATION] Checking SKU: {salla_prod.sku} | Name: {salla_prod.name[:45]}...")
            mock_ar = amazon_ready_map.get(salla_prod.sku)

            if mock_ar is not None:
                simulated_amazon = AmazonProduct(
                    sku=salla_prod.sku,
                    asin=f"B0{abs(hash(salla_prod.sku)) % 100000000:08d}",
                    title=str(mock_ar.get("name_ar", salla_prod.name)),
                    price=float(mock_ar.get("price", salla_prod.price)),
                    currency="SAR",
                    status="Active",
                    quantity=10,
                    bullet_points=[
                        str(mock_ar.get(f"amazon_bullet_{i}", ""))
                        for i in range(1, 6)
                        if str(mock_ar.get(f"amazon_bullet_{i}", "")) not in ["", "nan", "None"]
                    ],
                    images=salla_prod.images,
                    image_count=len(salla_prod.images),
                    found=True,
                    detail_page_scraped=True,
                )
            else:
                # Alternate simulated responses: perfect match, slight difference, or missing
                if idx % 3 == 0:
                    simulated_amazon = AmazonProduct(
                        sku=salla_prod.sku,
                        asin=f"B0{abs(hash(salla_prod.sku)) % 100000000:08d}",
                        title=f"{salla_prod.brand or 'قطاف الطبيعة'} - {salla_prod.name}",
                        price=round(salla_prod.price + 5.0, 2),  # Simulated markup
                        currency="SAR",
                        status="Active",
                        quantity=10,
                        bullet_points=salla_prod.bullet_points,
                        images=salla_prod.images,
                        image_count=len(salla_prod.images),
                        found=True,
                        detail_page_scraped=True,
                    )
                else:
                    simulated_amazon = AmazonProduct(
                        sku=salla_prod.sku,
                        asin=f"B0{abs(hash(salla_prod.sku)) % 100000000:08d}",
                        title=salla_prod.name,
                        price=salla_prod.price,
                        currency="SAR",
                        status="Active",
                        quantity=10,
                        bullet_points=salla_prod.bullet_points,
                        images=salla_prod.images,
                        image_count=len(salla_prod.images),
                        found=True,
                        detail_page_scraped=True,
                    )

            comp = comparator.compare(salla_prod, simulated_amazon)
            comparisons.append(comp)

        reporter = ValidationReporter(comparisons, output_dir=config.output_dir)
        exported_files = reporter.export_all()

        print("\n" + "=" * 80)
        print("  SIMULATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"  • Excel Report:  {exported_files['excel']}")
        print(f"  • CSV Report:    {exported_files['csv']}")
        print(f"  • JSON Report:   {exported_files['json']}")
        print("=" * 80 + "\n")
        return comparisons

    # 2. Initialize Browser & Login
    close_scraper_at_end = False
    if scraper is None:
        scraper = AmazonScraper(config)
        close_scraper_at_end = True

    try:
        logged_in = scraper.login_seller_central()
        if not logged_in:
            logger.error("Failed to authenticate into Amazon Seller Central. Aborting validation.")
            return []

        comparator = ProductComparator(config)
        comparisons: List[ProductComparison] = []

        total = len(products)
        print("\n" + "=" * 80)
        print(f"  STARTING DATA VALIDATION ({total} PRODUCTS)")
        print("=" * 80 + "\n")

        for idx, salla_prod in enumerate(products, 1):
            print(f"[{idx}/{total}] Checking SKU: {salla_prod.sku} | Name: {salla_prod.name[:45]}...")

            # Search by SKU, or barcode if SKU is missing
            search_query = salla_prod.sku or salla_prod.barcode or salla_prod.name
            try:
                amazon_prod = scraper.fetch_product_data(
                    query=search_query,
                    deep_check=config.deep_check
                )
            except Exception as e:
                logger.error(f"Error scraping product {search_query}: {e}")
                amazon_prod = None

            # Compare records
            comp = comparator.compare(salla_prod, amazon_prod)
            comparisons.append(comp)

            # Quick status line
            status_tag = "✓ MATCH" if comp.overall_match else "✗ MISMATCH"
            print(f"       -> Status: {status_tag} (ASIN: {comp.asin}, Price: {comp.diffs[3].actual_val if len(comp.diffs) > 3 else 'N/A'})\n")

            # Delay between requests to avoid rate limits
            if idx < total:
                scraper.sleep_delay()

        # 3. Generate Reports
        reporter = ValidationReporter(comparisons, output_dir=config.output_dir)
        exported_files = reporter.export_all()

        print("\n" + "=" * 80)
        print("  VALIDATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"  • Excel Report:  {exported_files['excel']}")
        print(f"  • CSV Report:    {exported_files['csv']}")
        print(f"  • JSON Report:   {exported_files['json']}")
        print("=" * 80 + "\n")

        return comparisons

    finally:
        if close_scraper_at_end and scraper:
            scraper.close()


def main():
    """Main CLI entrypoint."""
    args = parse_arguments()
    setup_logging(args.verbose)

    # Resolve Excel file path
    excel_file = Path(args.excel) if args.excel else find_default_excel()
    if not excel_file or not excel_file.exists():
        print("⚠ No Salla Excel file specified and none found in default directories.")
        user_input = input("Please enter the path to your Salla Excel file: ").strip().strip('"').strip("'")
        excel_file = Path(user_input)
        if not excel_file.exists():
            print(f"Error: File not found at '{excel_file}'")
            sys.exit(1)

    # Check credentials if email provided without password
    email = args.email
    password = args.password
    if email and not password:
        password = getpass.getpass(f"Enter Amazon password for {email}: ")

    profile_dir = Path(args.profile_dir) if args.profile_dir else None

    config = ValidatorConfig(
        marketplace=args.marketplace,
        excel_path=excel_file,
        output_dir=Path(args.output_dir),
        chrome_profile_dir=profile_dir,
        headless=args.headless,
        deep_check=not args.no_deep_check,
        limit=args.limit,
        request_delay_min=args.delay_min,
        request_delay_max=args.delay_max,
        amazon_email=email,
        amazon_password=password,
    )

    run_validation(excel_path=excel_file, config=config, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
