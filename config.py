import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Search Configuration
MAX_PROFESSORS = 100
SEARCH_DELAY = 2  # seconds between requests to avoid rate limiting
HEADLESS_BROWSER = True

# Academic Database URLs
SCHOLAR_URL = "https://scholar.google.com"
ORCID_URL = "https://orcid.org"
RESEARCHGATE_URL = "https://www.researchgate.net"

# Email Template Configuration
SUBJECT_PREFIX = "[Research Collaboration]"
