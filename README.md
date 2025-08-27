# Auto-Apply to Internships/Stages

## What this project does

* Sends tailored emails with your CV and cover letter to contacts listed in a CSV.
* Optionally auto-fills common web application forms using Playwright (Chromium).
* Keeps an application log (CSV) with status, timestamp, and any error messages.
* Allows you to personalize a short intro paragraph per company (from the CSV) that is merged into the email/body text.

## IMPORTANT

* Use responsibly: respect site Terms of Service and anti-bot rules.
* Many sites use unique form fields; the included form-filler covers common patterns but may not match every site. Extend selectors per target site if needed.
* For email sending, use an SMTP account with an app password (Gmail/Outlook/Yahoo). Avoid sending too many emails at once.

## Requirements

* Python 3.10+
* Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Project Structure

```
Resume_AutoApply/
│
├─ docs/                       # Your CV, cover letter, and any additional attachments
├─ scripts/                     # Python scripts (modularized)
│   ├─ __main__.py              # Main entry point (run this file)
│   ├─ config_loader.py         # Load and initialize config.yaml
│   ├─ companies.py             # Read and process companies.csv
│   ├─ email_utils.py           # Build and send emails
│   ├─ processor.py             # Core logic for processing each company: sends emails, fills forms, logs results
│   ├─ forms.py                 # Fill web forms via Playwright
│   ├─ logger.py                # Append to application log CSV
│   └─ utils.py                 # Helper functions (delays, etc.)
├─ config/                     # Configuration files
│   └─ config.yaml              # Set paths, email credentials, and settings
├─ logs/                       # Stores application logs
├─ companies.csv               # List of target companies
├─ README.md                   # Project instructions
└─ requirements.txt            # Python dependencies
```

## Usage

* **Dry run (no emails sent, no forms submitted):**

```bash
python -m scripts --dry-run
```

* **Actual sending and/or form submission:**

```bash
python -m scripts --mode both
```

* **Only email mode:**

```bash
python -m scripts --mode email
```

* **Only form mode:**

```bash
python -m scripts --mode form
```

### Mode explanation

* `email`: Sends emails only to the contacts listed in `companies.csv`.
* `form`: Submits forms on websites specified in `companies.csv` only.
* `both`: Executes both email sending and form submission for each company.

## Configuration

* `config/config.yaml` contains:

  * Paths to CV, cover letter, and attachments.
  * SMTP settings (host, port, username, app password).
  * Email templates and form selectors.
* `companies.csv` contains the target companies and optional intro notes.

## Logs

* Stored in `logs/applications_log.csv`.
* Automatically records timestamp, company, channel (email/form), target, status, and details.

## Notes

* Use an **app password** for your email provider (required for Gmail/Outlook 2FA). Instructions: [https://support.google.com/accounts/answer/185833?hl=en](https://support.google.com/accounts/answer/185833?hl=en)
* Customize email body and form message templates in `config.yaml`.
* Keep configs and logs outside version control if they contain sensitive data.
