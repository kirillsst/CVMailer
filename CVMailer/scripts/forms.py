from playwright.sync_api import sync_playwright
from typing import Dict
from pathlib import Path
from scripts.companies import Company

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
