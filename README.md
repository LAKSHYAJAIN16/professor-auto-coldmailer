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