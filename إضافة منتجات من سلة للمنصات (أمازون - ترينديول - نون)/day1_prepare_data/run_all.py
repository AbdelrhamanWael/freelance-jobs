"""
run_all.py
==========
تشغيل كامل خطوات اليوم الأول بتسلسل متكامل:
  Step 1: قراءة الملف واكتشاف الترويسة ومطابقة الأعمدة
  Step 2: الفلترة الشرطية وتنظيف الحقول واستبعاد المخفي
  Step 3: التقسيم إلى 3 DataFrames (Amazon, Noon, Trendyol)
"""

import sys
import os
import subprocess
from pathlib import Path

# ضمان دعم الترميز العربي UTF-8
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

base_dir = Path(__file__).resolve().parent.parent

STEPS = [
    ("الخطوة 1: قراءة وفحص ملف سلة", "day1_prepare_data/step1_load_raw.py"),
    ("الخطوة 2: الفلترة الشرطية والتنظيف", "day1_prepare_data/step2_filter_active.py"),
    ("الخطوة 3: التقسيم لمنصات أمازون ونون وترينديول", "day1_prepare_data/step3_split_platforms.py"),
]

def main():
    print("=" * 70)
    print("  بدء تنفيذ خطوات اليوم الأول: سحب وتجهيز وتقسيم منتجات سلة")
    print("=" * 70)

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    for title, script_path in STEPS:
        print(f"\n>>> جاري تشغيل: {title}")
        full_script = base_dir / script_path

        result = subprocess.run(
            [sys.executable, str(full_script)],
            cwd=str(base_dir),
            env=env,
        )

        if result.returncode != 0:
            print(f"\n[X] توقف التنفيذ بسبب خطأ في: {script_path}")
            print("    راجع ملف logs/day1.log لمعرفة سبب الخطأ.")
            sys.exit(result.returncode)

    print("\n" + "=" * 70)
    print("  [✓] اكتملت جميع خطوات اليوم الأول بنجاح تام!")
    print("      جميع الملفات جاهزة ومحفوظة في مجلد: data/clean/")
    print("=" * 70)

if __name__ == "__main__":
    main()
