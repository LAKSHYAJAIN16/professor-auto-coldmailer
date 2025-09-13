import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, List
import time
from urllib.parse import quote, urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # University directory patterns
        self.university_patterns = {
            'stanford': 'https://profiles.stanford.edu/',
            'mit': 'https://www.csail.mit.edu/people',
            'harvard': 'https://seas.harvard.edu/directory',
            'berkeley': 'https://www.eecs.berkeley.edu/people',
            'cmu': 'https://www.cs.cmu.edu/directory',
            'princeton': 'https://www.cs.princeton.edu/people',
            'yale': 'https://cpsc.yale.edu/people',
            'columbia': 'https://www.cs.columbia.edu/people',
            'duke': 'https://www.cs.duke.edu/people',
            'umich': 'https://cse.engin.umich.edu/people',
            'gatech': 'https://www.cc.gatech.edu/people',
            'uw': 'https://www.cs.washington.edu/people',
            'ucla': 'https://www.cs.ucla.edu/people',
            'ucsd': 'https://cse.ucsd.edu/people',
            'usc': 'https://www.cs.usc.edu/people',
            'nyu': 'https://cs.nyu.edu/people',
            'toronto': 'https://www.cs.toronto.edu/people',
            'ubc': 'https://www.cs.ubc.ca/people',
            'alberta': 'https://www.cs.ualberta.ca/people',
            'mcgill': 'https://www.cs.mcgill.ca/people',
            'waterloo': 'https://cs.uwaterloo.ca/people',
            'montreal': 'https://www.iro.umontreal.ca/people',
            'oxford': 'https://www.cs.ox.ac.uk/people',
            'cambridge': 'https://www.cl.cam.ac.uk/people',
            'eth': 'https://www.inf.ethz.ch/people',
            'iit': 'https://www.cse.iitb.ac.in/people',
            'iisc': 'https://www.csa.iisc.ac.in/people'
        }
    
    def extract_university_key(self, affiliation: str) -> str:
        """Extract university key from affiliation string"""
        affiliation_lower = affiliation.lower()
        
        # Direct matches
        for key in self.university_patterns.keys():
            if key in affiliation_lower:
                return key
        
        # Partial matches
        if 'stanford' in affiliation_lower:
            return 'stanford'
        elif 'mit' in affiliation_lower or 'massachusetts' in affiliation_lower:
            return 'mit'
        elif 'harvard' in affiliation_lower:
            return 'harvard'
        elif 'berkeley' in affiliation_lower or 'uc berkeley' in affiliation_lower:
            return 'berkeley'
        elif 'carnegie mellon' in affiliation_lower or 'cmu' in affiliation_lower:
            return 'cmu'
        elif 'princeton' in affiliation_lower:
            return 'princeton'
        elif 'yale' in affiliation_lower:
            return 'yale'
        elif 'columbia' in affiliation_lower:
            return 'columbia'
        elif 'duke' in affiliation_lower:
            return 'duke'
        elif 'michigan' in affiliation_lower or 'umich' in affiliation_lower:
            return 'umich'
        elif 'georgia tech' in affiliation_lower or 'gatech' in affiliation_lower:
            return 'gatech'
        elif 'washington' in affiliation_lower:
            return 'uw'
        elif 'ucla' in affiliation_lower:
            return 'ucla'
        elif 'ucsd' in affiliation_lower:
            return 'ucsd'
        elif 'usc' in affiliation_lower or 'southern california' in affiliation_lower:
            return 'usc'
        elif 'nyu' in affiliation_lower or 'new york' in affiliation_lower:
            return 'nyu'
        elif 'toronto' in affiliation_lower:
            return 'toronto'
        elif 'ubc' in affiliation_lower or 'british columbia' in affiliation_lower:
            return 'ubc'
        elif 'alberta' in affiliation_lower:
            return 'alberta'
        elif 'mcgill' in affiliation_lower:
            return 'mcgill'
        elif 'waterloo' in affiliation_lower:
            return 'waterloo'
        elif 'montreal' in affiliation_lower:
            return 'montreal'
        elif 'oxford' in affiliation_lower:
            return 'oxford'
        elif 'cambridge' in affiliation_lower:
            return 'cambridge'
        elif 'eth' in affiliation_lower or 'zurich' in affiliation_lower:
            return 'eth'
        elif 'iit' in affiliation_lower:
            return 'iit'
        elif 'iisc' in affiliation_lower:
            return 'iisc'
        
        return None
    
    def search_university_directory(self, name: str, university_key: str) -> str:
        """Search university directory for professor email"""
        try:
            if university_key not in self.university_patterns:
                return ""
            
            base_url = self.university_patterns[university_key]
            
            # Try different search approaches
            search_attempts = [
                f"{base_url}?search={quote(name)}",
                f"{base_url}{quote(name.replace(' ', '-').lower())}",
                f"{base_url}{quote(name.replace(' ', '').lower())}",
                base_url  # Browse directory
            ]
            
            for search_url in search_attempts:
                try:
                    logger.info(f"Searching: {search_url}")
                    response = self.session.get(search_url, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for email patterns
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    emails = re.findall(email_pattern, response.text)
                    
                    # Filter for university emails
                    for email in emails:
                        if self._is_university_email(email, university_key):
                            logger.info(f"Found email: {email}")
                            return email
                    
                    # Look for specific professor links
                    name_parts = name.lower().split()
                    for link in soup.find_all('a', href=True):
                        link_text = link.get_text().lower()
                        if all(part in link_text for part in name_parts if len(part) > 2):
                            # Found potential match, try to get email from profile
                            profile_url = urljoin(search_url, link['href'])
                            profile_email = self._scrape_profile_email(profile_url)
                            if profile_email:
                                return profile_email
                    
                    time.sleep(1)  # Be respectful
                    
                except Exception as e:
                    logger.warning(f"Search attempt failed for {search_url}: {e}")
                    continue
            
            return ""
            
        except Exception as e:
            logger.error(f"Error searching university directory: {e}")
            return ""
    
    def _is_university_email(self, email: str, university_key: str) -> bool:
        """Check if email belongs to the university"""
        university_domains = {
            'stanford': ['stanford.edu'],
            'mit': ['mit.edu', 'csail.mit.edu'],
            'harvard': ['harvard.edu'],
            'berkeley': ['berkeley.edu', 'eecs.berkeley.edu'],
            'cmu': ['cmu.edu', 'cs.cmu.edu'],
            'princeton': ['princeton.edu'],
            'yale': ['yale.edu'],
            'columbia': ['columbia.edu'],
            'duke': ['duke.edu'],
            'umich': ['umich.edu'],
            'gatech': ['gatech.edu', 'cc.gatech.edu'],
            'uw': ['uw.edu', 'washington.edu'],
            'ucla': ['ucla.edu'],
            'ucsd': ['ucsd.edu'],
            'usc': ['usc.edu'],
            'nyu': ['nyu.edu'],
            'toronto': ['utoronto.ca'],
            'ubc': ['ubc.ca'],
            'alberta': ['ualberta.ca'],
            'mcgill': ['mcgill.ca'],
            'waterloo': ['uwaterloo.ca'],
            'montreal': ['umontreal.ca'],
            'oxford': ['ox.ac.uk'],
            'cambridge': ['cam.ac.uk'],
            'eth': ['ethz.ch'],
            'iit': ['iit.ac.in'],
            'iisc': ['iisc.ac.in']
        }
        
        if university_key not in university_domains:
            return False
        
        email_domain = email.split('@')[-1].lower()
        return email_domain in university_domains[university_key]
    
    def _scrape_profile_email(self, profile_url: str) -> str:
        """Scrape email from professor's profile page"""
        try:
            response = self.session.get(profile_url, timeout=10)
            response.raise_for_status()
            
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, response.text)
            
            for email in emails:
                if '@' in email and '.' in email:
                    return email
            
            return ""
            
        except Exception as e:
            logger.warning(f"Error scraping profile {profile_url}: {e}")
            return ""
    
    def find_professor_email(self, professor: Dict) -> str:
        """Find email for a professor using web scraping"""
        name = professor.get('name', '').replace('Dr.', '').strip()
        affiliation = professor.get('affiliation', '')
        
        university_key = self.extract_university_key(affiliation)
        
        if not university_key:
            logger.warning(f"Could not identify university for {affiliation}")
            return ""
        
        logger.info(f"Searching for {name} at {university_key}")
        
        # Try different name variations
        name_variations = [
            name,
            name.replace('.', ''),
            name.replace(' ', ''),
            ' '.join(name.split()[::-1])  # Last name first
        ]
        
        for name_var in name_variations:
            email = self.search_university_directory(name_var, university_key)
            if email:
                return email
            time.sleep(2)  # Be respectful between searches
        
        logger.warning(f"Could not find email for {name}")
        return ""

if __name__ == "__main__":
    scraper = EmailScraper()
    
    # Test with a professor
    test_professor = {
        'name': 'Dr. Rich Sutton',
        'affiliation': 'University of Alberta - Computing Science',
        'research_areas': 'Reinforcement Learning',
        'relevance': 'Test'
    }
    
    email = scraper.find_professor_email(test_professor)
    print(f"Found email: {email}")

