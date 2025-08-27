#!/usr/bin/env python3
"""
Auto-Apply to Internships/Stages
-------------------------------------------

What this script does
- Sends tailored emails with your CV, cover letter, and flyer to contacts in a CSV.
- Optionally auto-fills common web application forms using Playwright (Chromium) and uploads your files.
- Keeps an application log (CSV) with status, timestamp, and any error messages.
- Lets you personalize a short intro paragraph per company (from the CSV) that is merged into the email/body text.

IMPORTANT
- Use this responsibly. Respect site Terms of Service and anti-bot rules. Add reasonable delays and limits.
- Many sites use unique form fields/selectors; the provided form-filler covers common patterns but won’t match every site. You can extend the selector lists below per target site.
- For email sending, use an SMTP account and (ideally) an app password (Gmail/Outlook/Yahoo). Avoid sending too many emails at once.

Requirements (install first)
- Python 3.10+
- pip install playwright python-dotenv pyyaml pandas beautifulsoup4 lxml
- playwright install chromium

Files you need to prepare
- config.yaml — paths & account settings (template auto-generated on first run if missing)
- companies.csv — your targets. Columns supported:
    company, contact_email, apply_url, contact_name, intro_note
  (You can leave some empty. At least one of contact_email or apply_url should be present.)
- Your CV file (PDF), your cover letter file (PDF or DOCX), your flyer (PDF). Paths go in config.yaml.

"""

import argparse
from scripts.config_loader import load_or_init_config
from scripts.processor import process_company
from scripts.companies import read_companies
from scripts.utils import random_delay
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Auto-apply to stage offers (emails + forms)")
    parser.add_argument("--config", default="./config/config.yaml", help="Path to config.yaml")
    parser.add_argument("--companies", default="./companies/companies.csv", help="Path to companies.csv")
    parser.add_argument("--mode", choices=["email", "form", "both"], default="both")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually send/submit")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of companies to process")
    args = parser.parse_args()

    cfg = load_or_init_config(Path(args.config))
    companies = read_companies(Path(args.companies))

    if args.limit:
        companies = companies[: args.limit]

    # Respectful pacing
    forms_cfg = cfg.get("forms", {})
    min_delay = forms_cfg.get("min_delay_s", 5)
    max_delay = forms_cfg.get("max_delay_s", 15)

    count = 0
    for comp in companies:
        if not comp.company:
            continue
        if not comp.contact_email and not comp.apply_url:
            print(f"[!] Skipping {comp.company}: no contact_email or apply_url")
            continue
        process_company(cfg, comp, dry_run=args.dry_run, mode=args.mode)
        count += 1
        if args.limit and count >= args.limit:
            break
        # politeness delay between companies
        random_delay(min_delay, max_delay)

    print("\n[i] Done. See log:", cfg["logging"]["output_csv"]) 


if __name__ == "__main__":
    main()
