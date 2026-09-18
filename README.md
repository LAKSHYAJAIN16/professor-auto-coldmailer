# Auto Cold Mailer

> Finds professors, writes them personalized emails, and sends them with your CV attached.

Emailing professors one by one to ask about research opportunities is tedious. This automates the whole loop: find relevant professors, personalize an email template for each, and send it out with your CV/research draft attached.

## Setup
```bash
pip install -r requirements.txt
```

`.env`:
```
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_16_character_app_password
OPENAI_API_KEY=your_openai_api_key
```

`EMAIL_PASSWORD` needs to be a Gmail App Password (Google Account → Security → App passwords, after enabling 2FA), not your login password.

## Usage
```bash
python run_campaign.py "Research Collaboration - Decision Making Games" "Lakshya Research Draft.pdf" 10
```

Finds professors via GPT, personalizes `email_template.txt` per recipient, sends with the PDF attached, and drops CSV reports (`professors_*.csv`, `email_report_*.csv`) plus `coldmailer.log`. Waits 30s between sends to stay under spam-filter/rate limits — test on 2-3 professors before a big run.

## How it's put together
- `simple_coldmailer.py` — `SimpleColdMailer`, orchestrates the whole campaign (`run_campaign.py` is a thin CLI wrapper)
- `gpt_professor_finder.py` — finds professors in a research area via OpenAI
- `email_scraper.py` — scrapes and validates contact info
- `email_personalizer.py` — rewrites the template per recipient, keeping the original tone
- `email_sender.py` — sends over SMTP with the PDF attached
- `scrape.py` — one-off: pulls emails off a given lab/people page (edit `START_URL`/`OUTPUT_FILE`)
- `new_script.py` — one-off: bare-bones sender for a hardcoded name/email list

## Stack
Python, OpenAI API, Selenium + BeautifulSoup for scraping, pandas for reports, Gmail SMTP for sending.

You need an OpenAI API key and a Gmail App Password. You're responsible for following whatever outreach regulations apply to you — this is for sending fewer, better-targeted emails, not spam.
