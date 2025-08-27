from pathlib import Path
import yaml
from typing import Dict

# Optional imports: Playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    PLAYWRIGHT_OK = True
except Exception:
    PLAYWRIGHT_OK = False

APP_VERSION = "0.1.0"

DEFAULT_CONFIG = {
    "identity": {
        "first_name": "Name",
        "last_name": "Surname",
        "email": "you@example.com",
        "phone": "+33 6 00 00 00 00",
        "city": "Paris",
        "portfolio_url": "https://your-portfolio.example",
        "linkedin_url": "https://www.linkedin.com/in/your-profile",
    },
    "files": {
        "cv": "./docs/CV.pdf",
        "cover_letter": "./docs/motivation.pdf",
        "flyer": "./docs/flyer.pdf",
    },
    "email": {
        "enabled": True,
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 465,
        "username": "you@example.com",
        "app_password": "app_password_here",
        "from_name": "Name Surname",
        "subject": "Candidature stage — {company}",
        "body_template": (
            "Hello {contact_name_or_team},\n\n"
            "I am reaching out to apply for a development internship. "
            "Please find attached my CV and cover letter.\n\n"
            "Portfolio: {portfolio_url}\nLinkedIn: {linkedin_url}\n\n"
            "Kind regards,\n{first_name} {last_name}\n{phone}\n{email}"
        ),
        "signature": "",
        "attachments": ["cv", "cover_letter", "flyer"],
    },
    "forms": {
        "enabled": True,
        "headless": True,
        "timeout_ms": 20000,
        "max_per_run": 20,
        "min_delay_s": 7,
        "max_delay_s": 20,
        "selectors": {
            "name": ["input[name*='name']", "input[name*='prenom']", "input[name*='nom']", "input[id*='name']", "input[id*='full']"],
            "email": ["input[type='email']", "input[name*='mail']", "input[id*='mail']"],
            "phone": ["input[type='tel']", "input[name*='phone']", "input[id*='phone']"],
            "message": ["textarea[name*='message']", "textarea[id*='message']", "textarea[name*='motivation']", "textarea[id*='motivation']"],
            "cv_upload": ["input[type='file'][name*='cv']", "input[type='file'][id*='cv']", "input[type='file'][name*='resume']", "input[type='file'][id*='resume']", "input[type='file']"],
            "letter_upload": ["input[type='file'][name*='lettre']", "input[type='file'][name*='motivation']", "input[type='file']"],
            "flyer_upload": ["input[type='file']"],
            "submit": ["button[type='submit']", "input[type='submit']", "text=Postuler", "text=Envoyer", "text=Soumettre", "text=Apply", "text=Submit"],
        },
        "message_template": "Hello, I am applying for an internship. Please find attached my CV and cover letter. Thank you!"
    },
    "logging": {
        "output_csv": "./logs/applications_log.csv",
    }
}

def load_or_init_config(path: Path) -> Dict:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(DEFAULT_CONFIG, f, sort_keys=False, allow_unicode=True)
        print(f"[i] Created default config at {path}. Fill in your details and paths.")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)
