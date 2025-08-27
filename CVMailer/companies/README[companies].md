# companies.csv — Guide

This CSV file stores the list of companies you want to apply to.  
Each row corresponds to one company or contact.

## Required Columns

| Column Name      | Description                                                                                           | Example                          |
|------------------|-------------------------------------------------------------------------------------------------------|----------------------------------|
| `company`         | Name of the company or organization.                                                                  | ACME Corp                         |
| `contact_email`   | Email address to send the application to. Leave empty if you only want to apply via the web form.      | jobs@acme.com                     |
| `apply_url`       | URL of the web application form. Leave empty if you only send an email.                                | https://acme.com/careers/apply    |
| `contact_name`    | Name of the person/team. Used for personalization in emails (`{contact_name_or_team}`).                | John Smith                        |
| `intro_note`      | A short, personalized note about why you're interested in this company (merged into email templates).  | Interested in your AI projects    |

At least **one of** `contact_email` or `apply_url` must be provided for the script to process the entry.

## Example CSV

```csv
company,contact_email,apply_url,contact_name,intro_note
ACME Corp,jobs@acme.com,https://acme.com/careers/apply,John Smith,Interested in your AI projects
BetaSoft,,https://betasoft.com/apply,Careers Team,Love your work in cloud computing
GammaTech,hr@gammatech.com,,,Looking for an internship in web development
