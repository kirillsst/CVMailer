# Auto-Apply to Internships/Stages (≈5 months)

## What this script does

* Sends tailored emails with your CV, cover letter, and SIMPLON flyer to contacts in a CSV.
* Optionally auto-fills common web application forms using Playwright (Chromium) and uploads your files.
* Keeps an application log (CSV) with status, timestamp, and any error messages.
* Lets you personalize a short intro paragraph per company (from the CSV) that is merged into the email/body text.

## IMPORTANT

* Use this responsibly. Respect site Terms of Service and anti-bot rules. Add reasonable delays and limits.
* Many sites use unique form fields/selectors; the provided form-filler covers common patterns but won’t match every site. You can extend the selector lists per target site.
* For email sending, use an SMTP account and (ideally) an app password (Gmail/Outlook/Yahoo). Avoid sending too many emails at once.

## Requirements

* Python 3.10+
* Install dependencies:

```bash
pip install playwright python-dotenv pyyaml pandas beautifulsoup4 lxml
playwright install chromium
```

## Required Files

* `config.yaml` — paths & account settings (template auto-generated on first run if missing)
* `companies.csv` — your targets. Supported columns:

```
company, contact_email, apply_url, contact_name, intro_note
```

* You can leave some columns empty. At least one of `contact_email` or `apply_url` should be present.
* Your CV (PDF), cover letter (PDF or DOCX), SIMPLON flyer (PDF). Paths go in `config.yaml`.

## Project Structure

```
Resume_AutoApply/
│
├─ docs/                      # Attachments (CV, cover letter, flyer)
├─ scripts/                   # Python script
│   └─ auto_apply.py
├─ config/                    # Config file
│   └─ config.yaml
├─ logs/                      # Application logs
│   └─ applications_log.csv
├─ companies.csv              # Target companies
├─ README.md                  # Instructions
└─ .gitignore                 # Ignore secrets and logs
```

## Run

* Dry run (no emails sent, no forms submitted):

```bash
python auto_stage_apply.py --dry-run
```

* Actually send/process:

```bash
python auto_stage_apply.py
```

* Only email mode:

```bash
python auto_stage_apply.py --mode email
```

* Only form mode:

```bash
python auto_stage_apply.py --mode form
```
