"""
مشغل الربط المباشر مع متصفح Google Chrome (بدون طلب OTP)
=============================================================================
يقوم بإعادة تشغيل Google Chrome مع تفعيل منفذ الربط البرمجي (9222)
باستخدام نفس البروفايل الفعلي (Profile 1) واستعادة نفس الصفحات المسجلة
ثم يتصل بالمتصفح ويفحص المنتجات والمخزون ومطابقتها مع سلة دون الحاجة لأي OTP.
"""

import sys
import os
import time
import socket
import subprocess
from pathlib import Path

# ضمان طباعة اللغة العربية على سطر أوامر ويندوز بدون مشاكل
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from amazon_salla_validator.reporter import safe_print
from check_live_amazon_inventory import LiveInventoryAuditor


CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
TARGET_ACCOUNT_SWITCHER_URL = (
    "https://sellercentral.amazon.com/account-switcher/default/merchantMarketplace?returnTo=%2Fhome"
)


def is_port_open(host: str = "127.0.0.1", port: int = 9222) -> bool:
    """فحص هل منفذ الربط 9222 مفتوح."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False


def launch_chrome_with_debugging():
    """إعادة تشغيل كروم مع تفعيل Port 9222 ونفس البروفايل واستعادة الجلسة."""
    safe_print("=" * 80)
    safe_print("    أداة الربط المباشر بمتصفح Chrome لفحص المخزون (بدون طلب OTP)")
    safe_print("=" * 80)
    safe_print("")

    if is_port_open():
        safe_print("✓ تم رصد متصفح Chrome مفتوح بالفعل على منفذ الربط 9222!")
        safe_print("  جاري الاتصال بجلستك الحالية مباشرة...\n")
        return True

    safe_print("(!) جاري تحضير المتصفح للربط المباشر بجلستك المفتوحة حالياً:")
    safe_print("    1. إغلاق نوافذ Chrome الحالية لحفظ الجلسة.")
    safe_print("    2. إعادة فتح Chrome بنفس البروفايل (Profile 1) واستعادة نفس التبويبات.")
    safe_print("    3. تفعيل منفذ التحكم البرمجي 9222.")
    safe_print("    --> لن يتم طلب أي كلمة مرور أو رمز OTP إطلاقاً!\n")

    # إغلاق أي عمليات كروم حالية لتحرير ملفات البروفايل
    safe_print("[1/3] إغلاق كروم الحالي...")
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True, text=True)
    time.sleep(2)

    # تشغيل كروم بالمنفذ 9222 وبروفايل المستخدم Profile 1
    safe_print("[2/3] فتح كروم مع استعادة صفحاتك وحسابك...")
    cmd = [
        CHROME_PATH,
        "--remote-debugging-port=9222",
        '--profile-directory=Profile 1',
        "--restore-last-session",
        TARGET_ACCOUNT_SWITCHER_URL
    ]
    subprocess.Popen(cmd)

    # انتظار فتح المنفذ
    safe_print("[3/3] انتظار جاهزية المتصفح للربط...")
    for _ in range(15):
        time.sleep(1)
        if is_port_open():
            safe_print("✓ تم فتح منفذ الربط 9222 بنجاح!\n")
            return True

    safe_print("⚠ لم يستجب المنفذ في الوقت المحدد، سيتم المحاولة مع الجلسة المتاحة...")
    return False


def main():
    launch_chrome_with_debugging()

    excel_file = BASE_DIR / "data" / "clean" / "amazon_ready.csv"
    if not excel_file.exists():
        excel_file = BASE_DIR / "data" / "exports" / "amazon_upload_ready.xlsx"

    auditor = LiveInventoryAuditor(
        excel_path=excel_file,
        profile_dir=Path.home() / ".amazon_chrome_profile",
        output_dir=BASE_DIR / "inventory_audit_reports",
        headless=False,
        max_pages=15,
        page_size=50
    )

    safe_print("بدء عملية الفحص الشامل ومطابقة المخزون والتأكد من تصفير الكميات (0)...")
    auditor.run_audit()


if __name__ == "__main__":
    main()
