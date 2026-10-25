"""
Amazon Seller Central & Product Detail Page Scraper using Selenium.
Handles authentication, session persistence, Manage Inventory search,
and deep product listing data extraction.
"""

import time
import random
import logging
import re
from pathlib import Path
from typing import Optional, List, Dict, Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException
)
from webdriver_manager.chrome import ChromeDriverManager

from .config import (
    ValidatorConfig, AmazonProduct, MARKETPLACE_CONFIGS,
    SELLER_CENTRAL_SELECTORS, DETAIL_PAGE_SELECTORS
)

logger = logging.getLogger(__name__)


class AmazonScraper:
    """Automates Amazon Seller Central and Detail Page scraping."""

    def __init__(self, config: ValidatorConfig):
        self.config = config
        self.market_info = MARKETPLACE_CONFIGS.get(
            self.config.marketplace.upper(),
            MARKETPLACE_CONFIGS["SA"]
        )
        self.driver: Optional[webdriver.Chrome] = None
        self.logged_in = False

    def start_browser(self) -> webdriver.Chrome:
        """Initializes Chrome WebDriver, attaching to existing session if port 9222 is open, or launching new instance."""
        import socket

        # Check if Chrome is already open with remote debugging port 9222
        port_open = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                port_open = (s.connect_ex(("127.0.0.1", 9222)) == 0)
        except Exception:
            port_open = False

        if port_open:
            logger.info("✓ رصد متصفح Chrome مفتوح مسبقاً على منفذ 9222! جاري الاتصال المباشر بمتصفحك الفعلي (بدون طلب تسجيل دخول أو OTP)...")
            options = Options()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            try:
                driver_path = ChromeDriverManager().install()
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            except Exception:
                self.driver = webdriver.Chrome(options=options)
            return self.driver

        options = Options()

        # Stealth and bot-detection bypass flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Standard desktop User-Agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--lang=ar,en-US,en")

        # Headless mode
        if self.config.headless:
            options.add_argument("--headless=new")

        # Safe Persistent Chrome Profile (always in user home to prevent non-ASCII/Arabic path bugs)
        safe_profile = Path.home() / ".amazon_chrome_profile"
        safe_profile.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={safe_profile}")
        logger.info(f"Using persistent Chrome profile directory: {safe_profile}")

        try:
            # First try webdriver_manager to get matching driver
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            logger.warning(f"WebDriverManager fallback to default Chrome: {e}")
            self.driver = webdriver.Chrome(options=options)

        self.driver.set_page_load_timeout(45)
        self.driver.implicitly_wait(4)
        try:
            self.driver.maximize_window()
        except Exception:
            pass

        # Mask navigator.webdriver
        try:
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
            )
        except Exception:
            pass

        return self.driver

    def close(self):
        """Closes the browser session."""
        if self.driver:
            try:
                # If connected via debuggerAddress, don't close user's real browser
                if "127.0.0.1:9222" in str(self.driver.capabilities.get("goog:chromeOptions", {})):
                    logger.info("Detached from user's Chrome session without closing.")
                    return
                self.driver.quit()
            except Exception:
                pass
            self.driver = None

    def sleep_delay(self):
        """Sleeps with random jitter to avoid rate limits."""
        delay = random.uniform(self.config.request_delay_min, self.config.request_delay_max)
        time.sleep(delay)

    def is_session_active(self) -> bool:
        """Checks if current page indicates an active Seller Central session."""
        if not self.driver:
            return False
        return self.is_authenticated_url(self.driver.current_url)

    @staticmethod
    def is_authenticated_url(url: str) -> bool:
        """Checks if URL is actually inside Seller Central and NOT on a signin/ap page."""
        u = url.lower()
        if any(x in u for x in ["signin", "ap/signin", "openid.assoc_handle", "ap/mfa", "ap/cvf", "approval"]):
            return False
        if "sellercentral.amazon" in u:
            return True
        return False

    def handle_account_switcher(self) -> bool:
        """
        Handles the 'Select an account' screen (account-switcher), selecting
        'Saudi Arabia' and clicking 'Select account'.
        """
        if not self.driver:
            return False
        curr_url = self.driver.current_url.lower()
        if "account-switcher" not in curr_url and "merchantmarketplace" not in curr_url:
            return False

        logger.info("✓ رصد صفحة اختيار المتجر والسوق (Select an account)! جاري اختيار 'Saudi Arabia' تلقائياً...")
        time.sleep(2)

        # Look for Saudi Arabia option and click it
        sa_clicked = False
        sa_xpaths = [
            "//*[contains(text(), 'Saudi Arabia')]",
            "//*[contains(text(), 'المملكة العربية السعودية')]",
            "//span[contains(text(), 'Saudi Arabia')]",
            "//div[contains(text(), 'Saudi Arabia')]",
            "//input[contains(@value, 'SA') or contains(@id, 'SA')]",
        ]
        for xpath in sa_xpaths:
            try:
                elems = self.driver.find_elements(By.XPATH, xpath)
                for elem in elems:
                    if elem.is_displayed():
                        try:
                            elem.click()
                        except Exception:
                            self.driver.execute_script("arguments[0].click();", elem)
                        sa_clicked = True
                        logger.info("✓ تم النقر على خيار سوق السعودية (Saudi Arabia).")
                        time.sleep(1)
                        break
                if sa_clicked:
                    break
            except Exception:
                continue

        # Click "Select account" button
        btn_xpaths = [
            "//button[contains(., 'Select account')]",
            "//button[contains(., 'اختيار الحساب')]",
            "//input[@value='Select account']",
            "button[data-testid='select-account-btn']",
            "button#select-account-btn",
            "button.a-button-input",
            "//span[contains(text(), 'Select account')]/parent::button",
            "//button",
        ]
        for sel in btn_xpaths:
            try:
                if sel.startswith("//"):
                    btns = self.driver.find_elements(By.XPATH, sel)
                else:
                    btns = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for btn in btns:
                    btn_text = btn.text.strip().lower()
                    if ("select account" in btn_text or "اختيار" in btn_text or btn.get_attribute("value") == "Select account") and btn.is_displayed():
                        try:
                            btn.click()
                        except Exception:
                            self.driver.execute_script("arguments[0].click();", btn)
                        time.sleep(3)
                        logger.info("✓ تم النقر على زر 'Select account' بنجاح!")
                        return True
            except Exception:
                continue

        return sa_clicked

    def login_seller_central(self) -> bool:
        """
        Navigates to Seller Central. Handles automated login or waits for 2FA/OTP.
        """
        if not self.driver:
            self.start_browser()

        inv_url = self.market_info["seller_central_url"]
        logger.info(f"Navigating to Amazon Seller Central: {inv_url}")
        self.driver.get(inv_url)
        time.sleep(3)

        # Check for account switcher
        self.handle_account_switcher()

        current_url = self.driver.current_url

        # If already on Seller Central and NOT on signin page, we are authenticated
        if self.is_authenticated_url(current_url):
            logger.info("✓ Already authenticated into Seller Central via persistent session.")
            self.logged_in = True
            return True

        # Check if on Sign-In Page
        if "signin" in current_url or "ap/signin" in current_url:
            logger.info("Seller Central login required.")

            # Attempt auto-fill if credentials configured
            if self.config.amazon_email:
                try:
                    email_field = self.find_first_element([
                        "input#ap_email", "input[name='email']", "input[type='email']"
                    ])
                    if email_field and email_field.is_displayed():
                        email_field.clear()
                        email_field.send_keys(self.config.amazon_email)
                        time.sleep(1)

                        # Click continue or submit if present
                        continue_btn = self.find_first_element(["input#continue", "input.a-button-input"])
                        if continue_btn:
                            continue_btn.click()
                            time.sleep(2)
                except Exception as e:
                    logger.debug(f"Email entry note: {e}")

            if self.config.amazon_password:
                try:
                    pass_field = self.find_first_element([
                        "input#ap_password", "input[name='password']", "input[type='password']"
                    ])
                    if pass_field and pass_field.is_displayed():
                        pass_field.clear()
                        pass_field.send_keys(self.config.amazon_password)
                        time.sleep(1)

                        remember_box = self.find_first_element(["input[name='rememberMe']"])
                        if remember_box and not remember_box.is_selected():
                            try:
                                remember_box.click()
                            except Exception:
                                pass

                        sign_in_btn = self.find_first_element([
                            "input#signInSubmit", "input#auth-signin-button"
                        ])
                        if sign_in_btn:
                            sign_in_btn.click()
                            time.sleep(3)
                except Exception as e:
                    logger.debug(f"Password entry note: {e}")

            # Now wait if 2FA / OTP / CAPTCHA or approval is needed
            current_url = self.driver.current_url.lower()
            if "signin" in current_url or "mfa" in current_url or "approval" in current_url:
                print("\n" + "=" * 70)
                print("⚠  ACTION REQUIRED: Amazon Authentication / 2FA Challenge Detected!")
                print("   Please complete the sign-in / OTP in the opened Chrome browser.")
                print("   The script will automatically continue once logged in...")
                print("=" * 70 + "\n")

                # Wait up to 180 seconds for user to complete login
                start_wait = time.time()
                while time.time() - start_wait < 180:
                    time.sleep(3)
                    curr = self.driver.current_url.lower()
                    if "inventory" in curr or ("sellercentral" in curr and "signin" not in curr):
                        logger.info("✓ Login confirmed! Continuing automation...")
                        self.logged_in = True
                        time.sleep(2)
                        return True

                logger.error("Timed out waiting for manual Amazon login completion.")
                return False

        self.logged_in = True
        return True

    def find_first_element(self, selectors: List[str], parent=None):
        """Finds the first matching element from a list of CSS selectors."""
        scope = parent or self.driver
        for selector in selectors:
            try:
                elem = scope.find_element(By.CSS_SELECTOR, selector)
                if elem:
                    return elem
            except NoSuchElementException:
                continue
        return None

    def find_elements(self, selectors: List[str], parent=None) -> List[Any]:
        """Finds all matching elements from a list of CSS selectors."""
        scope = parent or self.driver
        for selector in selectors:
            try:
                elems = scope.find_elements(By.CSS_SELECTOR, selector)
                if elems:
                    return elems
            except NoSuchElementException:
                continue
        return []

    def navigate_to_manage_inventory(self):
        """Ensures the browser is on the Manage Inventory page."""
        inv_url = self.market_info["seller_central_url"]
        if "inventory" not in self.driver.current_url.lower():
            logger.info(f"Navigating to: {inv_url}")
            self.driver.get(inv_url)
            time.sleep(3)

    def search_inventory_product(self, search_term: str) -> Optional[AmazonProduct]:
        """
        Searches Manage Inventory by SKU, ASIN, or Title.
        Returns parsed AmazonProduct or None if not found.
        """
        self.navigate_to_manage_inventory()

        search_term_clean = str(search_term).strip()
        if not search_term_clean:
            return None

        # Find search box
        search_input = self.find_first_element(SELLER_CENTRAL_SELECTORS["search_input"])
        if not search_input:
            # Fallback: wait explicitly for search box
            try:
                search_input = WebDriverWait(self.driver, 10).until(
                    lambda d: self.find_first_element(SELLER_CENTRAL_SELECTORS["search_input"])
                )
            except TimeoutException:
                logger.warning("Could not locate search box on Manage Inventory page.")
                return None

        try:
            # Clear and enter search query
            search_input.click()
            search_input.send_keys(Keys.CONTROL, "a")
            search_input.send_keys(Keys.BACKSPACE)
            time.sleep(0.5)
            search_input.send_keys(search_term_clean)
            time.sleep(0.5)

            # Hit enter or click search
            search_btn = self.find_first_element(SELLER_CENTRAL_SELECTORS["search_button"])
            if search_btn and search_btn.is_displayed():
                search_btn.click()
            else:
                search_input.send_keys(Keys.ENTER)

            time.sleep(2.5)  # Wait for AJAX search
        except Exception as e:
            logger.error(f"Error executing search for '{search_term_clean}': {e}")
            return None

        # Check for empty results
        no_res_elem = self.find_first_element(SELLER_CENTRAL_SELECTORS["no_results"])
        if no_res_elem and no_res_elem.is_displayed():
            logger.info(f"Product '{search_term_clean}' not found in Manage Inventory.")
            return AmazonProduct(
                sku=search_term_clean,
                found=False,
                error="Not found in Seller Central inventory"
            )

        # Look for table rows
        rows = self.find_elements(SELLER_CENTRAL_SELECTORS["inventory_rows"])
        if not rows:
            # Try waiting briefly
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d: len(self.find_elements(SELLER_CENTRAL_SELECTORS["inventory_rows"])) > 0
                )
                rows = self.find_elements(SELLER_CENTRAL_SELECTORS["inventory_rows"])
            except TimeoutException:
                pass

        if not rows:
            # Check page source for 0 results indicator
            if "0 results" in self.driver.page_source.lower() or "no records found" in self.driver.page_source.lower():
                return AmazonProduct(
                    sku=search_term_clean,
                    found=False,
                    error="Not found in Seller Central inventory"
                )
            logger.warning(f"No inventory rows identified for search '{search_term_clean}'.")
            return AmazonProduct(
                sku=search_term_clean,
                found=False,
                error="No row found"
            )

        # Parse the first matching row
        target_row = rows[0]
        row_text = target_row.text

        # Extract SKU
        sku_elem = self.find_first_element(SELLER_CENTRAL_SELECTORS["sku"], parent=target_row)
        scraped_sku = sku_elem.text.strip() if sku_elem else search_term_clean

        # Extract ASIN
        scraped_asin = None
        asin_elem = self.find_first_element(SELLER_CENTRAL_SELECTORS["asin"], parent=target_row)
        if asin_elem:
            scraped_asin = asin_elem.text.strip()
        else:
            # Regex search for B0... in row HTML/text
            asin_match = re.search(r"\b(B0[A-Z0-9]{8})\b", target_row.get_attribute("innerHTML") or "")
            if asin_match:
                scraped_asin = asin_match.group(1)

        # Extract Title
        title_elem = self.find_first_element(SELLER_CENTRAL_SELECTORS["title"], parent=target_row)
        scraped_title = title_elem.text.strip() if title_elem else ""

        # Extract Price
        scraped_price = None
        price_elem = self.find_first_element(SELLER_CENTRAL_SELECTORS["price"], parent=target_row)
        if price_elem:
            val = price_elem.get_attribute("value") or price_elem.text
            match = re.search(r"(\d+(?:\.\d+)?)", str(val))
            if match:
                try:
                    scraped_price = float(match.group(1))
                except ValueError:
                    pass

        # Extract Status
        status_elem = self.find_first_element(SELLER_CENTRAL_SELECTORS["status"], parent=target_row)
        scraped_status = status_elem.text.strip() if status_elem else "Active"

        # Extract Quantity
        scraped_qty = None
        qty_elem = self.find_first_element(SELLER_CENTRAL_SELECTORS["quantity"], parent=target_row)
        if qty_elem:
            val = qty_elem.get_attribute("value") or qty_elem.text
            match = re.search(r"(\d+)", str(val))
            if match:
                try:
                    scraped_qty = int(match.group(1))
                except ValueError:
                    pass

        # Extract Image Thumbnail
        images = []
        img_elem = self.find_first_element(SELLER_CENTRAL_SELECTORS["image"], parent=target_row)
        if img_elem:
            src = img_elem.get_attribute("src")
            if src and "http" in src:
                images.append(src)

        prod = AmazonProduct(
            sku=scraped_sku,
            asin=scraped_asin,
            title=scraped_title,
            price=scraped_price,
            currency=self.market_info["currency"],
            status=scraped_status,
            quantity=scraped_qty,
            images=images,
            image_count=len(images),
            found=True,
        )

        return prod

    def scrape_product_detail_page(self, asin: str, amazon_prod: AmazonProduct) -> AmazonProduct:
        """
        Navigates to the live Amazon product page (amazon.sa/dp/<ASIN>) to retrieve
        full title, bullet points, high-res gallery images, and full description.
        """
        if not asin or not asin.startswith("B0"):
            return amazon_prod

        dp_url = f"{self.market_info['dp_base_url']}{asin}"
        logger.info(f"Scraping live Amazon detail page: {dp_url}")

        try:
            self.driver.get(dp_url)
            time.sleep(2)

            # Check for page not found (Dogs of Amazon)
            if "page not found" in self.driver.title.lower() or "404" in self.driver.title:
                logger.warning(f"ASIN {asin} returned 404 / Page Not Found on live store.")
                amazon_prod.error = "Live detail page returned 404 (suppressed or not indexed)"
                return amazon_prod

            # Scrape Title
            title_elem = self.find_first_element(DETAIL_PAGE_SELECTORS["title"])
            if title_elem and title_elem.text.strip():
                amazon_prod.title = title_elem.text.strip()

            # Scrape Price
            price_elem = self.find_first_element(DETAIL_PAGE_SELECTORS["price"])
            if price_elem:
                price_text = price_elem.text.strip() or price_elem.get_attribute("textContent")
                match = re.search(r"(\d+(?:\.\d+)?)", price_text.replace(",", ""))
                if match:
                    try:
                        amazon_prod.price = float(match.group(1))
                    except ValueError:
                        pass

            # Scrape Bullet Points
            bullet_elems = self.find_elements(DETAIL_PAGE_SELECTORS["bullets"])
            bullets = [b.text.strip() for b in bullet_elems if b.text.strip() and len(b.text.strip()) > 3]
            if bullets:
                amazon_prod.bullet_points = bullets

            # Scrape Description
            desc_elem = self.find_first_element(DETAIL_PAGE_SELECTORS["description"])
            if desc_elem:
                amazon_prod.description = desc_elem.text.strip()

            # Scrape Image Gallery
            img_elems = self.find_elements(DETAIL_PAGE_SELECTORS["images"])
            dp_images = []
            for img in img_elems:
                src = img.get_attribute("src") or img.get_attribute("data-old-hires")
                if src and "http" in src:
                    # Upgrade thumbnail to high-res if applicable
                    high_res = re.sub(r"\._[A-Z0-9_,]+_\.", ".", src)
                    if high_res not in dp_images and not high_res.endswith(".gif"):
                        dp_images.append(high_res)

            if dp_images:
                amazon_prod.images = dp_images
                amazon_prod.image_count = len(dp_images)

            amazon_prod.detail_page_scraped = True

        except Exception as e:
            logger.error(f"Error scraping detail page for ASIN {asin}: {e}")

        return amazon_prod

    def fetch_product_data(self, query: str, deep_check: bool = True) -> AmazonProduct:
        """
        Orchestrates finding product in Manage Inventory and optionally
        deep-scraping its live detail page.
        """
        prod = self.search_inventory_product(query)

        if not prod or not prod.found:
            return prod or AmazonProduct(sku=query, found=False, error="Product not found")

        # Deep check live detail page if ASIN found
        if deep_check and prod.asin:
            self.sleep_delay()
            prod = self.scrape_product_detail_page(prod.asin, prod)

        return prod
