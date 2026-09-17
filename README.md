# Auto Cold Mailer

I built this because emailing professors one by one to ask about research opportunities is tedious and I wanted to automate the boring parts: finding relevant professors, writing a personalized email to each one, and actually sending it with my CV/research draft attached.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_16_character_app_password
OPENAI_API_KEY=your_openai_api_key
```

The password has to be a Gmail App Password, not your normal login password — turn on 2FA, then go to Google Account → Security → App passwords and generate one for "Mail".

## Running a campaign

```bash
python run_campaign.py "Email Title" "PDF_File.pdf" [number_of_professors]
```

For example:
```bash
python run_campaign.py "Research Collaboration - Decision Making Games" "Lakshya Research Draft.pdf" 10
```

Under the hood it: asks GPT to find professors relevant to your research area, loads your email from `email_template.txt`, uses AI to personalize each copy while keeping your voice/style intact, sends them out with the PDF attached, and drops CSV reports (`professors_[timestamp].csv`, `email_report_[timestamp].csv`) plus a `coldmailer.log` so you can see what happened.

It waits 30 seconds between sends to stay under the radar of spam filters and Gmail's sending limits — worth testing on a small batch (like 2-3 professors) before running it on a big list.

## How it's put together

- `simple_coldmailer.py` — the `SimpleColdMailer` class, orchestrates the whole campaign end to end. `run_campaign.py` is just a thin CLI wrapper around it.
- `gpt_professor_finder.py` — calls the OpenAI API to find professors in a given research area.
- `email_scraper.py` — scrapes and validates professor contact info.
- `email_personalizer.py` — uses AI to rewrite the template per recipient without losing the original tone.
- `email_sender.py` — sends the personalized email over SMTP with the PDF attached.

There are also a couple of one-off scripts I hacked together for specific outreach runs, not part of the main pipeline:
- `scrape.py` — walks a given lab/people page and pulls out `mailto:` and in-page email addresses into a JSON file. You edit `START_URL` / `OUTPUT_FILE` at the top before running it.
- `new_script.py` — a bare-bones sender with a hardcoded list of name/email pairs, for quick manually-curated batches when I didn't want to go through the full pipeline.

## Stack

Python, OpenAI API for the discovery/personalization steps, Selenium + BeautifulSoup + Requests for scraping, pandas for the CSV reports, and Gmail SMTP for actually sending mail.

A couple of things to keep in mind: you need an OpenAI API key and a Gmail account with an App Password set up, and you're responsible for following whatever email/outreach regulations apply to you — this is a tool for sending fewer, better-targeted emails, not for spamming everyone in a department.
