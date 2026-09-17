# Auto Cold Mailer

Automated academic email outreach system that finds professors, personalizes emails, and sends them with PDF attachments.

## Quick Start

### 1. Setup
```bash
pip install -r requirements.txt
```

### 2. Configure Email
Create a `.env` file with your Gmail credentials:
```
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_16_character_app_password
OPENAI_API_KEY=your_openai_api_key
```

### 3. Run Campaign
```bash
python run_campaign.py "Email Title" "PDF_File.pdf" [number_of_professors]
```

**Example:**
```bash
python run_campaign.py "Research Collaboration - Decision Making Games" "Lakshya Research Draft.pdf" 10
```

## What It Does

1. **Finds Professors**: Uses GPT to find relevant professors in your research area
2. **Loads Email Template**: Automatically loads from `email_template.txt`
3. **Personalizes Emails**: Uses AI to personalize each email while preserving your style
4. **Sends Emails**: Automatically sends personalized emails with PDF attachment
5. **Creates Reports**: Generates CSV files with professor list and email results

## Files Created

- `professors_[timestamp].csv` - List of found professors
- `email_report_[timestamp].csv` - Email sending results
- `coldmailer.log` - System logs

## Core Modules

- `simple_coldmailer.py` - `SimpleColdMailer` class that orchestrates a campaign end-to-end; used by `run_campaign.py`
- `gpt_professor_finder.py` - Uses the OpenAI API to find professors relevant to a research area
- `email_scraper.py` - Scrapes/validates professor contact info
- `email_personalizer.py` - Uses AI to personalize the email body per recipient while preserving the template's style
- `email_sender.py` - Sends the personalized emails over SMTP with the PDF attached

## Tech Stack

- Python 3.8+
- OpenAI API (professor discovery and email personalization)
- Selenium + BeautifulSoup + Requests (scraping)
- pandas (CSV reports)
- Gmail SMTP for sending

## Ad-hoc Scripts

A couple of one-off, hand-edited scripts also live in the repo root for specific outreach runs rather than the general pipeline:

- `scrape.py` - Standalone scraper that walks a given lab/people page (e.g. a university lab site) collecting `mailto:` and in-page email addresses into a JSON file (`qed_contacts.json` by default). Edit `START_URL`/`OUTPUT_FILE` at the top before running.
- `new_script.py` - A minimal, self-contained sender with a hardcoded list of professor name/email pairs; sends a plain SMTP email with a PDF attachment to each. Meant for quick, manually-curated batches outside the main `run_campaign.py` flow.

## Requirements

- Gmail account with App Password
- OpenAI API key
- Python 3.8+

## Email Template

Edit `email_template.txt` with your email content. The system will personalize it for each professor.

## Gmail App Password Setup

1. Enable 2-Factor Authentication on Gmail
2. Go to Google Account → Security → App passwords
3. Generate password for "Mail"
4. Use this password in your `.env` file

## Important Notes

- Uses 30-second delays between emails to avoid spam filters
- Respects Gmail sending limits
- Always test with small batches first
- Ensure compliance with email regulations