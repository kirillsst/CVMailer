#!/usr/bin/env python3
"""
Auto-Apply to Internships/Stages (≈5 months)
-------------------------------------------

What this script does
- Sends tailored emails with your CV, cover letter, and SIMPLON flyer to contacts in a CSV.
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
- Your CV file (PDF), your cover letter file (PDF or DOCX), your SIMPLON flyer (PDF). Paths go in config.yaml.

Run
- Dry run (no emails sent, no forms submitted):
    python auto_stage_apply.py --dry-run
- Actually send/process:
    python auto_stage_apply.py
- Only email mode:
    python auto_stage_apply.py --mode email
- Only form mode:
    python auto_stage_apply.py --mode form

"""
from __future__ import annotations
import argparse
import csv
import os
import random
import re
import smtplib
import ssl
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional, Dict

import pandas as pd
import yaml
from bs4 import BeautifulSoup

# Optional imports: Playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    PLAYWRIGHT_OK = True
except Exception:
    PLAYWRIGHT_OK = False


APP_VERSION = "0.1.0"

DEFAULT_CONFIG = {
    "identity": {
        "first_name": "Имя",
        "last_name": "Фамилия",
        "email": "you@example.com",
        "phone": "+33 6 00 00 00 00",
        "city": "Paris",
        "portfolio_url": "https://your-portfolio.example",
        "linkedin_url": "https://www.linkedin.com/in/your-profile",
    },
    "files": {
        "cv": "./docs/CV.pdf",
        "cover_letter": "./docs/Lettre_de_motivation.pdf",
        "simplon_flyer": "./docs/SIMPLON_flyer.pdf",
    },
    "email": {
        "enabled": True,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 465,
        "username": "you@example.com",
        "app_password": "app_password_here",
        "from_name": "Имя Фамилия",
        "subject": "Candidature stage (5 mois) — {company}",
        # You can write this in FR/RU/EN. {first_name}, {last_name}, {company}, {contact_name}, {intro_note}
        "body_template": (
            "Bonjour {contact_name_or_team},\n\n"
            "Je me permets de vous contacter pour un stage de 5 mois en développement. "
            "Actuellement chez SIMPLON, je travaille sur {intro_note}. "
            "Vous trouverez ci-joint mon CV, ma lettre de motivation et le flyer SIMPLON.\n\n"
            "Portfolio: {portfolio_url}\nLinkedIn: {linkedin_url}\n\n"
            "Bien cordialement,\n{first_name} {last_name}\n{phone}\n{email}"
        ),
        "signature": "",
        "attachments": ["cv", "cover_letter", "simplon_flyer"],
    },
    "forms": {
        "enabled": True,
        "headless": True,
        "timeout_ms": 20000,
        "max_per_run": 20,
        "min_delay_s": 7,
        "max_delay_s": 20,
        # Heuristic selectors for common fields. Extend per target site if needed.
        "selectors": {
            "name": [
                "input[name*='name']",
                "input[name*='prenom']", "input[name*='nom']",
                "input[id*='name']", "input[id*='full']",
            ],
            "email": ["input[type='email']", "input[name*='mail']", "input[id*='mail']"],
            "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
            "message": [
                "textarea[name*='message']", "textarea[id*='message']",
                "textarea[name*='motivation']", "textarea[id*='motivation']",
            ],
            "cv_upload": [
                "input[type='file'][name*='cv']", "input[type='file'][id*='cv']",
                "input[type='file'][name*='resume']", "input[type='file'][id*='resume']",
                "input[type='file']",
            ],
            "letter_upload": [
                "input[type='file'][name*='lettre']", "input[type='file'][name*='motivation']",
                "input[type='file']",
            ],
            "flyer_upload": ["input[type='file']"],
            "submit": [
                "button[type='submit']", "input[type='submit']",
                "text=Postuler", "text=Envoyer", "text=Soumettre", "text=Apply", "text=Submit",
            ],
        },
        # Default message merged into textarea if present
        "message_template": (
            "Bonjour, je postule pour un stage de 5 mois. "
            "Vous trouverez ci-joint mon CV et ma lettre de motivation. Merci !"
        ),
    },
    "logging": {
        "output_csv": "./logs/applications_log.csv",
    }
}

@dataclass
class Company:
    company: str
    contact_email: Optional[str]
    apply_url: Optional[str]
    contact_name: Optional[str]
    intro_note: Optional[str]


def load_or_init_config(path: Path) -> Dict:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(DEFAULT_CONFIG, f, sort_keys=False, allow_unicode=True)
        print(f"[i] Created default config at {path}. Fill in your details and paths.")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_companies(csv_path: Path) -> List[Company]:
    if not csv_path.exists():
        # Create a starter CSV
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["company", "contact_email", "apply_url", "contact_name", "intro_note"])
            w.writerow(["Exemple SA", "hr@exemple.fr", "", "Mme Dupont", "projet data/JS chez SIMPLON"])
            w.writerow(["Startup XYZ", "", "https://startup.xyz/jobs/stage-dev", "", "applications web responsives"])
        print(f"[i] Created template companies CSV at {csv_path}. Add your targets and rerun.")
    df = pd.read_csv(csv_path).fillna("")
    companies: List[Company] = []
    for _, row in df.iterrows():
        companies.append(Company(
            company=row.get("company", "").strip(),
            contact_email=row.get("contact_email", "").strip() or None,
            apply_url=row.get("apply_url", "").strip() or None,
            contact_name=row.get("contact_name", "").strip() or None,
            intro_note=row.get("intro_note", "").strip() or None,
        ))
    return companies


def build_email(cfg: Dict, comp: Company) -> EmailMessage:
    ident = cfg["identity"]
    email_cfg = cfg["email"]

    msg = EmailMessage()
    msg["From"] = f"{email_cfg.get('from_name') or ident['first_name'] + ' ' + ident['last_name']} <{email_cfg['username']}>"
    msg["To"] = comp.contact_email
    subject = email_cfg.get("subject", "Candidature").format(company=comp.company)
    msg["Subject"] = subject

    contact_name_or_team = comp.contact_name.strip() if comp.contact_name else "l'équipe RH"

    body = email_cfg["body_template"].format(
        first_name=ident["first_name"], last_name=ident["last_name"],
        email=ident["email"], phone=ident["phone"],
        portfolio_url=ident.get("portfolio_url", ""), linkedin_url=ident.get("linkedin_url", ""),
        company=comp.company, contact_name=(comp.contact_name or ""),
        contact_name_or_team=contact_name_or_team,
        intro_note=(comp.intro_note or "mon projet actuel")
    )
    msg.set_content(body)

    # Attach files
    for key in cfg["email"].get("attachments", []):
        fpath = Path(cfg["files"].get(key, "")).expanduser()
        if not fpath.exists():
            print(f"[!] Attachment missing: {fpath}")
            continue
        with open(fpath, "rb") as f:
            data = f.read()
        maintype, subtype = ("application", "octet-stream")
        if fpath.suffix.lower() == ".pdf":
            subtype = "pdf"
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=fpath.name)
    return msg


def send_email(cfg: Dict, msg: EmailMessage):
    email_cfg = cfg["email"]
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(email_cfg["smtp_host"], email_cfg["smtp_port"], context=context) as server:
        server.login(email_cfg["username"], email_cfg["app_password"])
        server.send_message(msg)


def random_delay(min_s: float, max_s: float):
    d = random.uniform(min_s, max_s)
    print(f"[i] Delay {d:.1f}s to be polite...")
    time.sleep(d)


def fill_form_and_submit(cfg: Dict, comp: Company) -> str:
    if not PLAYWRIGHT_OK:
        return "Playwright not installed"
    forms_cfg = cfg["forms"]
    selectors = forms_cfg["selectors"]
    msg_text = forms_cfg["message_template"]
    ident = cfg["identity"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=forms_cfg.get("headless", True))
        page = browser.new_page()
        page.set_default_timeout(forms_cfg.get("timeout_ms", 20000))
        page.goto(comp.apply_url)

        # Try to close cookie banners quickly
        for sel in ["text=Accepter", "text=Tout accepter", "text=OK", "text=D'accord"]:
            try:
                page.locator(sel).first.click(timeout=2000)
            except Exception:
                pass

        # Name
        for sel in selectors["name"]:
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    el.fill(f"{ident['first_name']} {ident['last_name']}")
                    break
            except Exception:
                pass

        # Email
        for sel in selectors["email"]:
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    el.fill(ident["email"])
                    break
            except Exception:
                pass

        # Phone
        for sel in selectors["phone"]:
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    el.fill(ident["phone"])
                    break
            except Exception:
                pass

        # Message
        for sel in selectors["message"]:
            try:
                el = page.locator(sel).first
                if el.count() > 0:
                    body = msg_text
                    if comp.intro_note:
                        body += f"\n\nFocus: {comp.intro_note}"
                    el.fill(body)
                    break
            except Exception:
                pass

        # Uploads
        def try_upload(group_key: str, file_key: str):
            fpath = Path(cfg["files"].get(file_key, "")).expanduser()
            if not fpath.exists():
                return False
            for sel in selectors[group_key]:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        el.set_input_files(str(fpath))
                        return True
                except Exception:
                    pass
            return False

        cv_ok = try_upload("cv_upload", "cv")
        letter_ok = try_upload("letter_upload", "cover_letter")
        flyer_ok = try_upload("flyer_upload", "simplon_flyer")

        # Submit
        submitted = False
        for sel in selectors["submit"]:
            try:
                page.locator(sel).first.click()
                submitted = True
                break
            except Exception:
                pass

        # Heuristic success check
        success_texts = [
            "merci", "thank you", "reçu", "received", "envoyée", "submitted", "bien reçu"
        ]
        outcome = "submitted" if submitted else "clicked_failed"
        try:
            content = page.content().lower()
            if any(t in content for t in success_texts):
                outcome = "success_detected"
        except Exception:
            pass

        browser.close()
        uploads = f"uploads cv={cv_ok}, letter={letter_ok}, flyer={flyer_ok}"
        return f"{outcome}; {uploads}"


def append_log(log_csv: Path, row: Dict):
    log_csv.parent.mkdir(parents=True, exist_ok=True)
    file_exists = log_csv.exists()
    with log_csv.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "timestamp", "company", "channel", "target", "status", "details"
        ])
        if not file_exists:
            w.writeheader()
        w.writerow(row)


def process_company(cfg: Dict, comp: Company, *, dry_run: bool, mode: str) -> None:
    log_csv = Path(cfg["logging"]["output_csv"]).expanduser()
    ts = datetime.now().isoformat(timespec="seconds")

    if mode in ("email", "both") and comp.contact_email:
        try:
            if dry_run:
                status = "dry_run"
            else:
                msg = build_email(cfg, comp)
                send_email(cfg, msg)
                status = "sent"
            append_log(log_csv, {
                "timestamp": ts,
                "company": comp.company,
                "channel": "email",
                "target": comp.contact_email,
                "status": status,
                "details": ""
            })
            print(f"[✓] Email -> {comp.company} <{comp.contact_email}> [{status}]")
        except Exception as e:
            append_log(log_csv, {
                "timestamp": ts,
                "company": comp.company,
                "channel": "email",
                "target": comp.contact_email,
                "status": "error",
                "details": str(e)
            })
            print(f"[x] Email failed for {comp.company}: {e}")

    if mode in ("form", "both") and comp.apply_url and cfg["forms"]["enabled"]:
        try:
            if dry_run:
                status = "dry_run"
                details = ""
            else:
                details = fill_form_and_submit(cfg, comp)
                status = "ok" if details.startswith("success") or details.startswith("submitted") else "check"
            append_log(log_csv, {
                "timestamp": ts,
                "company": comp.company,
                "channel": "form",
                "target": comp.apply_url,
                "status": status,
                "details": details
            })
            print(f"[✓] Form -> {comp.company} [{status}] {details}")
        except Exception as e:
            append_log(log_csv, {
                "timestamp": ts,
                "company": comp.company,
                "channel": "form",
                "target": comp.apply_url,
                "status": "error",
                "details": str(e)
            })
            print(f"[x] Form failed for {comp.company}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Auto-apply to stage offers (emails + forms)")
    parser.add_argument("--config", default="./config.yaml", help="Path to config.yaml")
    parser.add_argument("--companies", default="./companies.csv", help="Path to companies.csv")
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
