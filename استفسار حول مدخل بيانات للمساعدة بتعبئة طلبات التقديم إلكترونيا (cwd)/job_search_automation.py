"""
Job Search Automation Script
Uses Playwright to search for jobs across multiple platforms with provided keywords
"""

import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import json

# Search keywords from user requirements
JOB_TITLES = [
    "Embedded AI Intern",
    "Edge AI Intern",
    "TinyML Intern",
    "Embedded Machine Learning Intern",
    "On-Device ML Intern",
    "Firmware Engineer Intern",
    "Embedded Software Intern",
    "ML Systems Intern",
    "Model Optimization Intern",
    "Efficient Deep Learning Intern",
    "Signal Processing Intern",
    "DSP Intern",
    "Sensor Fusion Intern",
    "Wearable ML Intern",
    "Biomedical Signal Processing Intern"
]

CATEGORY_KEYWORDS = [
    "PhD Intern",
    "PhD Research Intern",
    "Graduate Intern",
    "Summer 2027",
    "Spring 2027",
    "Winter 2027",
    "2027 Internship",
    "Co-op 2027",
    "Student Researcher",
    "University Graduate"
]

SKILL_KEYWORDS = [
    "quantization",
    "TensorFlow Lite Micro",
    "LiteRT",
    "ONNX",
    "CMSIS-NN",
    "ARM Cortex-M",
    "RTOS",
    "FreeRTOS",
    "Zephyr",
    "BLE",
    "PPG",
    "ECG",
    "IMU",
    "time series"
]

COMPANY_CAREER_PAGES = [
    {"name": "Texas Instruments", "url": "https://careers.ti.com"},
    {"name": "ARM", "url": "https://www.arm.com/careers"},
    {"name": "STMicroelectronics", "url": "https://www.st.com/content/st_com/en/about/careers.html"},
    {"name": "Medtronic", "url": "https://www.medtronic.com/careers"},
    {"name": "Garmin", "url": "https://careers.garmin.com"},
    {"name": "Bosch", "url": "https://www.bosch.com/careers"},
    {"name": "Honeywell", "url": "https://careers.honeywell.com"},
    {"name": "NVIDIA", "url": "https://www.nvidia.com/en-us/about-nvidia/careers"},
    {"name": "Qualcomm", "url": "https://www.qualcomm.com/company/careers"},
    {"name": "Analog Devices", "url": "https://www.analog.com/en/careers.html"},
    {"name": "Infineon", "url": "https://www.infineon.com/careers"},
    {"name": "Microchip", "url": "https://www.microchip.com/en-us/about-us/careers"}
]

# Excel columns (matching existing format)
EXCEL_COLUMNS = [
    "Employer",
    "Internship / program",
    "Priority",
    "Location",
    "Timing",
    "Listing type",
    "Why it fits your CV",
    "Eligibility / next step",
    "Employer sponsorship policy",
    "Listed deadline",
    "Application status",
    "Requisition / ID",
    "Application / source"
]

class JobSearcher:
    def __init__(self):
        self.jobs_found = []

    async def search_linkedin_jobs(self, page, search_query):
        """Search LinkedIn Jobs with the given query"""
        print(f"Searching LinkedIn for: {search_query}")
        try:
            await page.goto("https://www.linkedin.com/jobs/")
            await page.wait_for_load_state("networkidle")

            # Enter search query
            search_box = page.locator('input[aria-label*="Search"]')
            await search_box.fill(search_query)
            await page.keyboard.press("Enter")
            await page.wait_for_load_state("networkidle")

            # Wait for job listings to load
            await page.wait_for_timeout(3000)

            # Extract job cards
            job_cards = page.locator('.job-card-container')
            count = await job_cards.count()

            for i in range(min(count, 10)):  # Limit to first 10 results
                try:
                    card = job_cards.nth(i)
                    title = await card.locator('.job-card-list__title').inner_text() if await card.locator('.job-card-list__title').count() > 0 else "N/A"
                    company = await card.locator('.job-card-container__company-name').inner_text() if await card.locator('.job-card-container__company-name').count() > 0 else "N/A"
                    location = await card.locator('.job-card-container__metadata-item').first.inner_text() if await card.locator('.job-card-container__metadata-item').count() > 0 else "N/A"

                    self.jobs_found.append({
                        "Employer": company,
                        "Internship / program": title,
                        "Priority": "To be evaluated",
                        "Location": location,
                        "Timing": "2027",
                        "Listing type": "LinkedIn",
                        "Why it fits your CV": "Keyword match",
                        "Eligibility / next step": "Check eligibility",
                        "Employer sponsorship policy": "To be verified",
                        "Listed deadline": None,
                        "Application status": "Not applied",
                        "Requisition / ID": "N/A",
                        "Application / source": "LinkedIn"
                    })
                except Exception as e:
                    print(f"Error extracting job card {i}: {e}")
                    continue

            print(f"Found {count} jobs on LinkedIn for: {search_query}")
        except Exception as e:
            print(f"Error searching LinkedIn: {e}")

    async def search_google_jobs(self, page, search_query):
        """Search Google Jobs with the given query"""
        print(f"Searching Google Jobs for: {search_query}")
        try:
            await page.goto("https://www.google.com")
            await page.wait_for_load_state("networkidle")

            # Enter search query
            search_box = page.locator('textarea[name="q"]')
            await search_box.fill(search_query + " jobs")
            await page.keyboard.press("Enter")
            await page.wait_for_load_state("networkidle")

            # Wait for job listings to load
            await page.wait_for_timeout(3000)

            # Look for Google Jobs panel
            job_cards = page.locator('.gws-ce-zFp').or_(page.locator('[data-hveid]'))
            count = await job_cards.count()

            print(f"Found {count} potential job listings on Google for: {search_query}")
        except Exception as e:
            print(f"Error searching Google Jobs: {e}")

    async def search_company_career_page(self, page, company_info):
        """Search a specific company's career page"""
        print(f"Searching career page for: {company_info['name']}")
        try:
            await page.goto(company_info['url'])
            await page.wait_for_load_state("networkidle", timeout=10000)

            # Look for search box
            search_box = page.locator('input[type="search"], input[placeholder*="search" i], input[placeholder*="Search" i]').first
            if await search_box.count() > 0:
                for keyword in ["Intern", "PhD", "Embedded", "Firmware", "Machine Learning"]:
                    try:
                        await search_box.fill(keyword)
                        await page.keyboard.press("Enter")
                        await page.wait_for_timeout(2000)
                        # Extract job information here
                        print(f"  Searched for: {keyword}")
                    except:
                        continue

            print(f"Completed search for: {company_info['name']}")
        except Exception as e:
            print(f"Error searching {company_info['name']}: {e}")

    async def run_searches(self):
        """Run all searches"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # Search LinkedIn with key combinations
            search_queries = [
                "Embedded AI Intern PhD 2027",
                "TinyML Intern 2027",
                "Edge AI Intern Summer 2027",
                "Embedded Machine Learning Intern PhD",
                "Firmware Engineer Intern 2027",
                "Signal Processing Intern PhD 2027"
            ]

            for query in search_queries:
                await self.search_linkedin_jobs(page, query)
                await page.wait_for_timeout(2000)

            # Search Google Jobs
            for query in search_queries[:3]:  # Limit Google searches
                await self.search_google_jobs(page, query)
                await page.wait_for_timeout(2000)

            # Search company career pages
            for company in COMPANY_CAREER_PAGES[:5]:  # Limit to first 5 companies
                await self.search_company_career_page(page, company)
                await page.wait_for_timeout(2000)

            await browser.close()

    def save_to_excel(self, filename="job_search_results.xlsx"):
        """Save found jobs to Excel file"""
        if not self.jobs_found:
            print("No jobs found to save")
            return

        df = pd.DataFrame(self.jobs_found, columns=EXCEL_COLUMNS)

        # Add header info rows (matching existing format)
        header_data = [
            ["Job Search Results", None, None, None, None, None, None, None, None, None, None, None, None],
            [f"Generated on {datetime.now().strftime('%B %d, %Y')}", None, None, None, None, None, None, None, None, None, None, None, None],
            [f"Total jobs found: {len(self.jobs_found)}", None, None, None, None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None, None, None, None, None],
            EXCEL_COLUMNS
        ]

        header_df = pd.DataFrame(header_data)
        final_df = pd.concat([header_df, df], ignore_index=True)

        final_df.to_excel(filename, index=False, header=False)
        print(f"Saved {len(self.jobs_found)} jobs to {filename}")

async def main():
    searcher = JobSearcher()
    await searcher.run_searches()
    searcher.save_to_excel()

if __name__ == "__main__":
    asyncio.run(main())
