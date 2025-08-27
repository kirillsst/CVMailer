# Config Folder

This folder contains configuration files for the Auto-Apply script.

## Files
- `config.yaml` — Main configuration file.
  - Contains paths to your CV, cover letter, and SIMPLON flyer.
  - Contains email account settings (SMTP host, port, username, app password).
  - Contains settings for form automation (selectors, delays, timeouts).

## Notes
- Edit `config.yaml` to update your personal information, file paths, or email credentials.
- Keep this file secure, especially if it contains passwords or app keys.
- **App Password**:
  - For Gmail, you need an app-specific password instead of your main password if using 2FA.
  - You can create it following this guide: [Google App Passwords](https://support.google.com/accounts/answer/185833?hl=en)
  - Insert the generated 16-character app password in `config.yaml` under `app_password`.
