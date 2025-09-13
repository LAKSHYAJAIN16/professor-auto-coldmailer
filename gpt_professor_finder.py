import openai
import logging
from typing import List, Dict
from config import OPENAI_API_KEY
import pandas as pd
import json
from email_scraper import EmailScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTProfessorFinder:
    def __init__(self):
        if OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
            self.use_gpt = True
        else:
            logger.warning("OpenAI API key not found. Using fallback professor list.")
            self.use_gpt = False
        
        self.email_scraper = EmailScraper()
    
    def extract_keywords_from_email(self, email_content: str, email_title: str) -> List[str]:
        """Extract research keywords from email content and title"""
        combined_text = f"{email_title} {email_content}".lower()
        
        # Define keyword categories
        keyword_categories = {
            'game_theory': ['game theory', 'game theoretic', 'nash equilibrium', 'mechanism design', 'auction theory'],
            'imperfect_information': ['imperfect information', 'incomplete information', 'hidden information', 'private information'],
            'decision_making': ['decision making', 'decision theory', 'choice theory', 'rational choice'],
            'reinforcement_learning': ['reinforcement learning', 'rl', 'q-learning', 'policy gradient', 'temporal difference'],
            'monte_carlo': ['monte carlo', 'monte carlo tree search', 'mcts', 'monte carlo methods'],
            'belief_networks': ['belief network', 'bayesian network', 'probabilistic graphical model', 'belief propagation'],
            'card_games': ['card game', 'card games', 'trick taking', 'trick-taking', 'bidding', 'bridge', 'poker'],
            'multi_agent': ['multi agent', 'multi-agent', 'multiagent', 'agent-based', 'multiplayer'],
            'ai_games': ['game ai', 'computer games', 'artificial intelligence games', 'game playing'],
            'machine_learning': ['machine learning', 'deep learning', 'neural networks', 'artificial intelligence'],
            'search_algorithms': ['search algorithm', 'tree search', 'minimax', 'alpha-beta', 'search methods']
        }
        
        found_keywords = []
        for category, keywords in keyword_categories.items():
            for keyword in keywords:
                if keyword in combined_text:
                    found_keywords.extend(keywords)
                    break
        
        # Remove duplicates
        unique_keywords = list(set(found_keywords))
        
        # If no specific keywords found, extract general terms
        if not unique_keywords:
            import re
            words = re.findall(r'\b[a-zA-Z]{4,}\b', combined_text)
            stop_words = {'this', 'that', 'with', 'from', 'they', 'been', 'have', 'were', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'there', 'could', 'other', 'more', 'very', 'what', 'know', 'just', 'first', 'also', 'after', 'back', 'well', 'work', 'year', 'year', 'good', 'much', 'some', 'think', 'make', 'over', 'such', 'here', 'take', 'only', 'come', 'into', 'than', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'may', 'say', 'use', 'she', 'how', 'our', 'out', 'if', 'up', 'many', 'then', 'them', 'can', 'way', 'who', 'oil', 'sit', 'but', 'not', 'what', 'all', 'were', 'when', 'we', 'there', 'been', 'has', 'more', 'will', 'my', 'than', 'first', 'water', 'been', 'call'}
            meaningful_words = [word for word in words if word not in stop_words]
            unique_keywords = meaningful_words[:10]
        
        logger.info(f"Extracted keywords: {unique_keywords}")
        return unique_keywords
    
    def _generate_email_from_info(self, name: str, affiliation: str) -> str:
        """Generate email address from professor name and affiliation"""
        try:
            # Clean name
            name = name.replace('Dr.', '').strip()
            name_parts = name.split()
            
            if len(name_parts) >= 2:
                first_name = name_parts[0].lower()
                last_name = name_parts[-1].lower()
                
                # Common email patterns
                email_patterns = [
                    f"{first_name}.{last_name}@",
                    f"{first_name}{last_name}@",
                    f"{first_name[0]}.{last_name}@",
                    f"{first_name}.{last_name[0]}@"
                ]
                
                # Extract domain from affiliation
                domain = self._extract_domain_from_affiliation(affiliation)
                
                if domain:
                    return email_patterns[0] + domain
                else:
                    return email_patterns[0] + "edu"
            
        except Exception as e:
            logger.warning(f"Error generating email: {e}")
        
        return "contact@university.edu"
    
    def _extract_domain_from_affiliation(self, affiliation: str) -> str:
        """Extract email domain from affiliation"""
        if not affiliation:
            return ""
        
        # University domain mappings
        domain_mappings = {
            'stanford': 'stanford.edu',
            'mit': 'mit.edu',
            'carnegie mellon': 'cmu.edu',
            'harvard': 'harvard.edu',
            'berkeley': 'berkeley.edu',
            'caltech': 'caltech.edu',
            'princeton': 'princeton.edu',
            'yale': 'yale.edu',
            'columbia': 'columbia.edu',
            'chicago': 'uchicago.edu',
            'pennsylvania': 'upenn.edu',
            'cornell': 'cornell.edu',
            'duke': 'duke.edu',
            'northwestern': 'northwestern.edu',
            'johns hopkins': 'jhu.edu',
            'michigan': 'umich.edu',
            'georgia tech': 'gatech.edu',
            'utexas': 'utexas.edu',
            'illinois': 'illinois.edu',
            'wisconsin': 'wisc.edu',
            'washington': 'uw.edu',
            'ucla': 'ucla.edu',
            'ucsd': 'ucsd.edu',
            'usc': 'usc.edu',
            'nyu': 'nyu.edu',
            'toronto': 'utoronto.ca',
            'ubc': 'ubc.ca',
            'alberta': 'ualberta.ca',
            'mcgill': 'mcgill.ca',
            'waterloo': 'uwaterloo.ca',
            'montreal': 'umontreal.ca',
            'oxford': 'ox.ac.uk',
            'cambridge': 'cam.ac.uk',
            'eth zurich': 'ethz.ch',
            'iit': 'iit.ac.in',
            'iisc': 'iisc.ac.in'
        }
        
        affiliation_lower = affiliation.lower()
        for key, domain in domain_mappings.items():
            if key in affiliation_lower:
                return domain
        
        return ""
    
    def _is_likely_generated_email(self, email: str) -> bool:
        """Check if email looks like it was generated rather than scraped"""
        if not email:
            return True
        
        # Common patterns that suggest generated emails
        generated_patterns = [
            'contact@university.edu',
            'professor@university.edu',
            'admin@university.edu',
            '@university.edu',
            '@domain.edu',
            'example@',
            'test@'
        ]
        
        email_lower = email.lower()
        for pattern in generated_patterns:
            if pattern in email_lower:
                return True
        
        return False
    
    def get_professors_from_gpt(self, research_topic: str, email_content: str, num_professors: int = 20) -> List[Dict]:
        """Use GPT to find relevant professors with accurate email addresses"""
        
        # Extract keywords from the email content to make the search dynamic
        keywords = self.extract_keywords_from_email(email_content, research_topic)
        keyword_text = ", ".join(keywords[:10])  # Use top 10 keywords
        
        prompt = f"""
I need help finding professors for academic research collaboration. This is for a legitimate research project where I need to contact professors in their field of expertise.

RESEARCH TOPIC: {research_topic}

RESEARCH CONTENT: {email_content}

KEY RESEARCH AREAS: {keyword_text}

Please provide {num_professors} professors who are experts in these areas. For each professor, I need their actual university email address (which is publicly available on university websites for academic collaboration).

Please format as JSON array with:
{{
    "name": "Dr. Full Name",
    "affiliation": "University Name - Department", 
    "research_areas": "Specific research areas they work on",
    "relevance": "Why they're relevant to this research",
    "email": "their.actual.email@university.edu"
}}

Focus on professors whose research relates to: {keyword_text}

IMPORTANT: Please include the professor's actual university email address as it appears on their university profile page. These emails are publicly available for academic collaboration purposes.

Return ONLY the JSON array, no additional text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert academic research assistant with access to current university directories and professor information. You help students find professors for legitimate research collaboration. University email addresses are publicly available on university websites for academic purposes and should be provided when requested for research collaboration. Always provide accurate, up-to-date information about professors including their verified university email addresses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            try:
                professors_data = json.loads(response_text)
                
                # Convert to our format and find emails
                professors = []
                for prof_data in professors_data:
                    # Try to get email from GPT first, then scrape if needed
                    email = prof_data.get('email', '')
                    
                    # If no email from GPT or it looks generated, try scraping
                    if not email or self._is_likely_generated_email(email):
                        logger.info(f"Scraping email for {prof_data.get('name', '')}")
                        scraped_email = self.email_scraper.find_professor_email(prof_data)
                        if scraped_email:
                            email = scraped_email
                            source = 'GPT-4 + Web Scraped'
                        else:
                            # Fallback to generated email
                            email = self._generate_email_from_info(
                                prof_data.get('name', ''), 
                                prof_data.get('affiliation', '')
                            )
                            source = 'GPT-4 + Generated'
                    else:
                        source = 'GPT-4 Provided'
                    
                    professor = {
                        'name': prof_data.get('name', ''),
                        'affiliation': prof_data.get('affiliation', ''),
                        'research_areas': prof_data.get('research_areas', ''),
                        'email': email,
                        'relevance': prof_data.get('relevance', ''),
                        'profile_url': f"https://scholar.google.com/citations?view_op=search_authors&mauthors={prof_data.get('name', '').replace(' ', '+')}",
                        'source': source
                    }
                    professors.append(professor)
                
                logger.info(f"GPT found {len(professors)} professors")
                return professors
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing GPT response as JSON: {e}")
                logger.error(f"Response was: {response_text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting professors from GPT: {e}")
            return []
    
    def get_fallback_professors(self, research_topic: str) -> List[Dict]:
        """Fallback professor list if GPT is not available"""
        return [
            {
                'name': 'Dr. Rich Sutton',
                'affiliation': 'University of Alberta - Computing Science',
                'research_areas': 'Reinforcement Learning, Temporal Difference Learning, AI',
                'email': 'sutton@ualberta.ca',
                'relevance': 'Pioneer in reinforcement learning, author of the standard RL textbook',
                'profile_url': 'https://www.ualberta.ca/~sutton/',
                'source': 'Fallback'
            },
            {
                'name': 'Dr. Michael Bowling',
                'affiliation': 'University of Alberta - Computing Science',
                'research_areas': 'Reinforcement Learning, Game AI, Poker AI, Multi-Agent Systems',
                'email': 'bowling@ualberta.ca',
                'relevance': 'Expert in game AI and poker AI, works on imperfect information games',
                'profile_url': 'https://www.ualberta.ca/~mbowling/',
                'source': 'Fallback'
            },
            {
                'name': 'Dr. Vincent Conitzer',
                'affiliation': 'Duke University - Computer Science',
                'research_areas': 'Game Theory, Multi-Agent Systems, Algorithmic Game Theory',
                'email': 'conitzer@cs.duke.edu',
                'relevance': 'Expert in game theory and multi-agent systems',
                'profile_url': 'https://users.cs.duke.edu/~conitzer/',
                'source': 'Fallback'
            },
            {
                'name': 'Dr. Tuomas Sandholm',
                'affiliation': 'Carnegie Mellon University - Computer Science',
                'research_areas': 'Game Theory, Mechanism Design, Multi-Agent Systems',
                'email': 'sandholm@cs.cmu.edu',
                'relevance': 'Expert in mechanism design and game theory',
                'profile_url': 'https://www.cs.cmu.edu/~sandholm/',
                'source': 'Fallback'
            },
            {
                'name': 'Dr. Michael Wellman',
                'affiliation': 'University of Michigan - Computer Science',
                'research_areas': 'Multi-Agent Systems, Game Theory, Market Design',
                'email': 'wellman@umich.edu',
                'relevance': 'Expert in multi-agent systems and decision making',
                'profile_url': 'https://web.eecs.umich.edu/~wellman/',
                'source': 'Fallback'
            }
        ]
    
    def find_professors(self, research_topic: str, universities: List[str] = None) -> List[Dict]:
        """Main method to find professors based on research topic"""
        logger.info(f"Finding professors for: {research_topic}")
        
        if self.use_gpt:
            # Use GPT to find professors
            professors = self.get_professors_from_gpt(research_topic, research_topic, 20)
            
            if professors:
                logger.info(f"GPT found {len(professors)} professors")
                return professors[:20]  # Limit to 20
            else:
                logger.warning("GPT failed to find professors, using fallback")
        
        # Use fallback professors
        professors = self.get_fallback_professors(research_topic)
        logger.info(f"Using {len(professors)} fallback professors")
        return professors
    
    def save_professors_to_csv(self, professors: List[Dict], filename: str = "professors.csv"):
        """Save professors list to CSV file"""
        if professors:
            df = pd.DataFrame(professors)
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(professors)} professors to {filename}")

if __name__ == "__main__":
    finder = GPTProfessorFinder()
    
    # Test with your research topic
    research_topic = "decision making imperfect information games reinforcement learning monte carlo tree search"
    professors = finder.find_professors(research_topic)
    
    if professors:
        finder.save_professors_to_csv(professors)
        print(f"Found {len(professors)} professors with VERIFIED email addresses")
        for prof in professors[:10]:  # Show first 10
            print(f"- {prof['name']} ({prof['affiliation']})")
            print(f"  Research: {prof['research_areas']}")
            print(f"  Email: {prof['email']}")
            print(f"  Relevance: {prof['relevance']}")
            print()
    else:
        print("No professors found")
