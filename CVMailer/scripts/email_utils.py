import smtplib, ssl
from email.message import EmailMessage
from pathlib import Path
from typing import Dict
from scripts.companies import Company

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
