#!/usr/bin/env python3
"""
Root execution script for Salla vs Amazon Product Data Accuracy Validator.
=========================================================================
Usage:
    python run_amazon_validation.py
    python run_amazon_validation.py --limit 5
    python run_amazon_validation.py --excel "data/raw/salla_products_export.xlsx" --marketplace SA
"""

import sys
from pathlib import Path

# Ensure UTF-8 output in Windows PowerShell / Command Prompt
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from amazon_salla_validator.cli import main

if __name__ == "__main__":
    main()
