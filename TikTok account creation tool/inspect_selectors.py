"""
inspect_selectors.py
──────────────────────
Opens TikTok signup in a VISIBLE browser window.
Waits 30 seconds so you can see/interact, then dumps
all inputs and buttons found on the page.

Run: .venv\Scripts\python inspect_selectors.py
"""
import asyncio
from playwright.async_api import async_playwright

URL = "https://www.tiktok.com/signup/phone-or-email/email"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--window-size=1280,900",
            ],
        )
        ctx = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = await ctx.new_page()

        print(f"\n[*] Navigating to {URL} ...")
        await page.goto(URL, wait_until="domcontentloaded")

        print("[*] Waiting 30 seconds — watch the browser window.\n")
        await asyncio.sleep(30)

        print(f"\n[*] Final URL: {page.url}\n")

        # ── Dump all inputs ────────────────────────────────────────────────
        print("=" * 60)
        print("INPUTS FOUND:")
        print("=" * 60)
        inputs = await page.query_selector_all("input")
        for i, el in enumerate(inputs):
            attrs = await el.evaluate("""el => ({
                type:        el.type,
                name:        el.name,
                id:          el.id,
                placeholder: el.placeholder,
                className:   el.className.substring(0, 80),
                dataE2e:     el.getAttribute('data-e2e'),
                maxlength:   el.maxLength,
                visible:     el.offsetParent !== null,
            })""")
            print(f"  [{i}] {attrs}")

        # ── Dump all buttons ───────────────────────────────────────────────
        print("\n" + "=" * 60)
        print("BUTTONS FOUND:")
        print("=" * 60)
        buttons = await page.query_selector_all("button, [role='button']")
        for i, el in enumerate(buttons):
            attrs = await el.evaluate("""el => ({
                text:      el.innerText.substring(0, 60).trim(),
                type:      el.type,
                id:        el.id,
                className: el.className.substring(0, 80),
                dataE2e:   el.getAttribute('data-e2e'),
                visible:   el.offsetParent !== null,
            })""")
            print(f"  [{i}] {attrs}")

        # ── Dump all selects (dropdowns) ───────────────────────────────────
        print("\n" + "=" * 60)
        print("SELECTS / COMBOBOXES FOUND:")
        print("=" * 60)
        selects = await page.query_selector_all("select, [role='combobox'], [role='listbox']")
        for i, el in enumerate(selects):
            attrs = await el.evaluate("""el => ({
                tag:     el.tagName,
                name:    el.name,
                id:      el.id,
                role:    el.getAttribute('role'),
                className: el.className.substring(0, 80),
                dataE2e: el.getAttribute('data-e2e'),
                visible: el.offsetParent !== null,
            })""")
            print(f"  [{i}] {attrs}")

        print("\n[*] Done. Closing browser.")
        await browser.close()

asyncio.run(main())
