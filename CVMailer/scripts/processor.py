from datetime import *
from scripts.email_utils import build_email, send_email
from scripts.logger import append_log
from scripts.forms import fill_form_and_submit
from typing import Dict
from pathlib import Path
from scripts.companies import Company

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