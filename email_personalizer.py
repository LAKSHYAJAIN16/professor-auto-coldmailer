import openai
import re
from typing import Dict, List
from config import OPENAI_API_KEY
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailPersonalizer:
    def __init__(self):
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
            self.use_openai = True
        else:
            logger.warning("OpenAI API key not found. Using rule-based personalization only.")
            self.use_openai = False
    
    def personalize_email(self, base_email: str, professor_info: Dict) -> str:
        """
        Personalize an email for a specific professor while preserving the original style
        
        Args:
            base_email: The original email template
            professor_info: Dictionary containing professor information
            
        Returns:
            Personalized email string
        """
        if self.use_openai:
            return self.personalize_with_ai(base_email, professor_info)
        else:
            return self.personalize_rule_based(base_email, professor_info)
    
    def personalize_with_ai(self, base_email: str, professor_info: Dict) -> str:
        """Use OpenAI to personalize the email while preserving style"""
        try:
            prompt = self._create_personalization_prompt(base_email, professor_info)
            
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at personalizing emails while preserving the original writing style and tone. Your task is to customize emails for academic professors while maintaining the professional tone and structure of the original."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            personalized_email = response.choices[0].message.content.strip()
            logger.info(f"Successfully personalized email for {professor_info.get('name', 'Unknown')}")
            return personalized_email
            
        except Exception as e:
            logger.error(f"Error with AI personalization: {e}")
            logger.info("Falling back to rule-based personalization")
            return self.personalize_rule_based(base_email, professor_info)
    
    def _create_personalization_prompt(self, base_email: str, professor_info: Dict) -> str:
        """Create a prompt for AI personalization"""
        name = professor_info.get('name', 'Professor')
        affiliation = professor_info.get('affiliation', 'your institution')
        research_areas = professor_info.get('research_areas', '')
        
        prompt = f"""
Please personalize the following email for Professor {name} from {affiliation}.

Professor Information:
- Name: {name}
- Affiliation: {affiliation}
- Research Areas: {research_areas}

Original Email:
{base_email}

Instructions:
1. Preserve the original writing style, tone, and structure exactly
2. Replace generic references with specific details about the professor
3. Add a brief, relevant mention of their research area if appropriate
4. Keep the same level of formality and professionalism
5. Maintain the same email length and paragraph structure
6. Only make necessary personalizations - don't over-customize

Return only the personalized email, no additional text.
"""
        return prompt
    
    def personalize_rule_based(self, base_email: str, professor_info: Dict) -> str:
        """Personalize email using rule-based approach"""
        personalized_email = base_email
        
        # Extract professor information
        name = professor_info.get('name', '')
        affiliation = professor_info.get('affiliation', '')
        research_areas = professor_info.get('research_areas', '')
        
        # Get first name and last name
        name_parts = name.split()
        first_name = name_parts[0] if name_parts else 'Professor'
        last_name = name_parts[-1] if len(name_parts) > 1 else ''
        full_name = name if name else 'Professor'
        
        # Replace generic greetings
        personalized_email = self._replace_greetings(personalized_email, first_name, full_name)
        
        # Replace generic institution references
        personalized_email = self._replace_institution_references(personalized_email, affiliation)
        
        # Add research-specific content if relevant
        if research_areas:
            personalized_email = self._add_research_relevance(personalized_email, research_areas)
        
        # Replace generic closings
        personalized_email = self._replace_closings(personalized_email, first_name)
        
        logger.info(f"Personalized email for {full_name} using rule-based approach")
        return personalized_email
    
    def _replace_greetings(self, email: str, first_name: str, full_name: str) -> str:
        """Replace generic greetings with personalized ones"""
        # Get last name
        name_parts = full_name.split()
        last_name = name_parts[-1] if len(name_parts) > 1 else full_name
        
        greeting_replacements = [
            (r'\bDear\s+Professor\b', f'Dear Dr. {last_name}' if len(name_parts) > 1 else f'Dear {full_name}'),
            (r'\bDear\s+Sir/Madam\b', f'Dear Dr. {last_name}' if len(name_parts) > 1 else f'Dear {full_name}'),
            (r'\bDear\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b', f'Dear Dr. {last_name}' if len(name_parts) > 1 else f'Dear {full_name}'),
        ]
        
        for pattern, replacement in greeting_replacements:
            email = re.sub(pattern, replacement, email, flags=re.IGNORECASE)
        
        return email
    
    def _replace_institution_references(self, email: str, affiliation: str) -> str:
        """Replace generic institution references"""
        if not affiliation:
            return email
            
        institution_replacements = [
            (r'\byour\s+institution\b', affiliation, re.IGNORECASE),
            (r'\byour\s+university\b', affiliation, re.IGNORECASE),
            (r'\byour\s+department\b', affiliation, re.IGNORECASE),
            (r'\bthe\s+institution\b', affiliation, re.IGNORECASE),
        ]
        
        for pattern, replacement, flags in institution_replacements:
            email = re.sub(pattern, replacement, email, flags=flags)
        
        return email
    
    def _add_research_relevance(self, email: str, research_areas: str) -> str:
        """Add research-specific content to make email more relevant"""
        if not research_areas:
            return email
        
        # Extract key research terms
        research_terms = research_areas.split(',')[:2]  # Take first 2 research areas
        relevant_terms = [term.strip() for term in research_terms if term.strip()]
        
        if not relevant_terms:
            return email
        
        # Look for opportunities to insert research relevance
        # This is a simple approach - in practice, you might want more sophisticated insertion
        
        # Try to find a sentence where we can add research relevance
        sentences = email.split('.')
        modified_sentences = []
        
        for i, sentence in enumerate(sentences):
            if 'research' in sentence.lower() and i < len(sentences) - 1:
                # Add research relevance to the next sentence
                if i + 1 < len(sentences):
                    next_sentence = sentences[i + 1]
                    if not any(term.lower() in next_sentence.lower() for term in relevant_terms):
                        sentences[i + 1] = f"Given your expertise in {', '.join(relevant_terms)}, " + next_sentence.lower()
            
            modified_sentences.append(sentence)
        
        return '.'.join(modified_sentences)
    
    def _replace_closings(self, email: str, first_name: str) -> str:
        """Replace generic closings with personalized ones"""
        closing_replacements = [
            (r'\bSincerely,\s*\n.*', f'Sincerely,\n{first_name}' if first_name else 'Sincerely,'),
            (r'\bBest\s+regards,\s*\n.*', f'Best regards,\n{first_name}' if first_name else 'Best regards,'),
            (r'\bThank\s+you,\s*\n.*', f'Thank you,\n{first_name}' if first_name else 'Thank you,'),
        ]
        
        for pattern, replacement in closing_replacements:
            email = re.sub(pattern, replacement, email, flags=re.IGNORECASE | re.MULTILINE)
        
        return email
    
    def validate_personalization(self, original_email: str, personalized_email: str) -> Dict:
        """Validate that personalization was successful"""
        validation_results = {
            'length_change': abs(len(personalized_email) - len(original_email)),
            'greeting_changed': self._check_greeting_change(original_email, personalized_email),
            'contains_professor_name': self._check_name_inclusion(personalized_email),
            'preserves_structure': self._check_structure_preservation(original_email, personalized_email),
            'is_valid': True
        }
        
        # Check if personalization is too different from original
        if validation_results['length_change'] > len(original_email) * 0.5:
            validation_results['is_valid'] = False
            validation_results['warning'] = 'Email length changed significantly'
        
        return validation_results
    
    def _check_greeting_change(self, original: str, personalized: str) -> bool:
        """Check if greeting was personalized"""
        original_greeting = self._extract_greeting(original)
        personalized_greeting = self._extract_greeting(personalized)
        return original_greeting != personalized_greeting
    
    def _check_name_inclusion(self, email: str) -> bool:
        """Check if email contains professor name"""
        # Simple check for common name patterns
        name_patterns = [
            r'Dr\.\s+[A-Z][a-z]+',
            r'Professor\s+[A-Z][a-z]+',
            r'Dear\s+[A-Z][a-z]+',
        ]
        
        for pattern in name_patterns:
            if re.search(pattern, email):
                return True
        return False
    
    def _check_structure_preservation(self, original: str, personalized: str) -> bool:
        """Check if email structure is preserved"""
        original_paragraphs = len(original.split('\n\n'))
        personalized_paragraphs = len(personalized.split('\n\n'))
        
        return abs(original_paragraphs - personalized_paragraphs) <= 1
    
    def _extract_greeting(self, email: str) -> str:
        """Extract greeting from email"""
        lines = email.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            if 'dear' in line.lower():
                return line.strip()
        return ""

if __name__ == "__main__":
    # Example usage
    personalizer = EmailPersonalizer()
    
    base_email = """
Dear Professor,

I hope this email finds you well. I am writing to introduce myself and express my interest in potential research collaboration.

I am currently working on a project that I believe aligns with your research interests. I would be grateful for the opportunity to discuss this further and explore potential collaboration opportunities.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
John Doe
"""
    
    professor_info = {
        'name': 'Sarah Johnson',
        'affiliation': 'MIT Computer Science Department',
        'research_areas': 'Machine Learning, Artificial Intelligence, Natural Language Processing'
    }
    
    personalized = personalizer.personalize_email(base_email, professor_info)
    print("Personalized Email:")
    print(personalized)
    
    validation = personalizer.validate_personalization(base_email, personalized)
    print("\nValidation Results:")
    print(validation)
