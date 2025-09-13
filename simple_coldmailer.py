#!/usr/bin/env python3
"""
Simple Auto Cold Mailer - Streamlined version

Just input:
1. Email title
2. PDF file path

System automatically:
- Loads email content from email_template.txt
- Extracts keywords from title + email content
- Finds relevant professors dynamically
- Personalizes emails with AI
- Sends emails with PDF attachment
- Creates CSV reports
"""

import os
import sys
from typing import List, Dict
from gpt_professor_finder import GPTProfessorFinder
from email_personalizer import EmailPersonalizer
from email_sender import EmailSender
from config import MAX_PROFESSORS
import pandas as pd
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('coldmailer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SimpleColdMailer:
    def __init__(self):
        self.professor_finder = GPTProfessorFinder()
        self.email_personalizer = EmailPersonalizer()
        self.email_sender = EmailSender()
        
    def run_campaign(self, email_title: str, pdf_path: str = None, num_professors: int = 10):
        """Run complete campaign with minimal input"""
        
        print("\n" + "="*60)
        print("🚀 SIMPLE AUTO COLD MAILER")
        print("="*60)
        print(f"📧 Title: {email_title}")
        print(f"📎 PDF: {pdf_path if pdf_path else 'None'}")
        print(f"👥 Target: {num_professors} professors")
        print("="*60)
        
        # Step 1: Load email template
        print("\n📝 Loading email template...")
        try:
            with open('email_template.txt', 'r', encoding='utf-8') as f:
                email_content = f.read().strip()
            print("✅ Email template loaded")
        except FileNotFoundError:
            print("❌ email_template.txt not found!")
            return
        except Exception as e:
            print(f"❌ Error loading template: {e}")
            return
        
        # Step 2: Extract keywords from title + email content
        print("\n🔍 Analyzing email content...")
        combined_text = f"{email_title} {email_content}"
        keywords = self.professor_finder.extract_keywords_from_email(combined_text, email_title)
        research_keywords = ' '.join(keywords[:10])
        print(f"✅ Extracted keywords: {research_keywords}")
        
        # Step 3: Find professors using GPT
        print(f"\n👥 Finding {num_professors} professors using GPT...")
        professors = self.professor_finder.find_professors(
            research_topic=research_keywords
        )
        
        # Limit to requested number
        professors = professors[:num_professors]
        
        if not professors:
            print("❌ No professors found!")
            return
        
        print(f"✅ Found {len(professors)} professors")
        
        # Step 4: Save professors CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        professors_filename = f"professors_{timestamp}.csv"
        self.professor_finder.save_professors_to_csv(professors, professors_filename)
        print(f"💾 Saved professors to: {professors_filename}")
        
        # Step 5: Personalize emails
        print(f"\n🤖 Personalizing {len(professors)} emails...")
        personalized_emails = []
        
        for i, professor in enumerate(professors, 1):
            print(f"   Personalizing {i}/{len(professors)} for {professor['name']}")
            try:
                personalized_email = self.email_personalizer.personalize_email(
                    email_content, professor
                )
                personalized_emails.append(personalized_email)
            except Exception as e:
                logger.warning(f"Failed to personalize for {professor['name']}: {e}")
                personalized_emails.append(email_content)  # Use original as fallback
        
        print("✅ All emails personalized")
        
        # Step 6: Test email connection
        print(f"\n🔗 Testing email connection...")
        if not self.email_sender.test_connection():
            print("❌ Email connection failed. Check your .env file")
            return
        print("✅ Email connection successful")
        
        # Step 7: Create email data
        emails_data = self.email_sender.create_email_data(
            professors, personalized_emails, email_title
        )
        
        # Step 8: Send emails
        print(f"\n📤 Sending {len(emails_data)} emails...")
        print("⏰ This will take time due to delays between emails...")
        
        sending_results = self.email_sender.send_bulk_emails(
            emails_data, attachment_path=pdf_path
        )
        
        # Step 9: Save reports
        report_filename = self.email_sender.save_sending_report()
        
        # Step 10: Show results
        print(f"\n🎉 CAMPAIGN COMPLETED!")
        print("="*60)
        print(f"📊 RESULTS:")
        print(f"   Total emails: {sending_results['total_emails']}")
        print(f"   Successfully sent: {sending_results['successful_sends']}")
        print(f"   Failed: {sending_results['failed_sends']}")
        print(f"   Success rate: {sending_results['success_rate']:.1f}%")
        
        print(f"\n📋 FILES CREATED:")
        print(f"   Professors: {professors_filename}")
        if report_filename:
            print(f"   Email report: {report_filename}")
        print(f"   Log file: coldmailer.log")
        
        print("\n✅ Campaign completed successfully!")
        
        return {
            'professors_found': len(professors),
            'emails_sent': sending_results['successful_sends'],
            'success_rate': sending_results['success_rate'],
            'professors_file': professors_filename,
            'report_file': report_filename
        }

def main():
    """Main function - simple input interface"""
    
    print("🎓 SIMPLE AUTO COLD MAILER")
    print("Just enter the email title and PDF file path!")
    print()
    
    # Get email title
    email_title = input("📧 Email Title: ").strip()
    if not email_title:
        print("❌ Title cannot be empty!")
        return
    
    # Get PDF file path
    pdf_path = input("📎 PDF File Path (or press Enter to skip): ").strip()
    if pdf_path and not os.path.exists(pdf_path):
        print(f"⚠️  Warning: {pdf_path} not found. Proceeding without attachment.")
        pdf_path = None
    
    # Get number of professors (optional)
    num_professors_input = input("👥 Number of professors (default 10): ").strip()
    try:
        num_professors = int(num_professors_input) if num_professors_input else 10
        num_professors = max(1, min(num_professors, MAX_PROFESSORS))
    except ValueError:
        num_professors = 10
    
    # Run campaign
    try:
        cold_mailer = SimpleColdMailer()
        results = cold_mailer.run_campaign(email_title, pdf_path, num_professors)
        
        if results:
            print(f"\n🎯 SUMMARY:")
            print(f"   Found {results['professors_found']} professors")
            print(f"   Sent {results['emails_sent']} emails ({results['success_rate']:.1f}% success)")
            
    except KeyboardInterrupt:
        print("\n\n❌ Campaign interrupted by user.")
    except Exception as e:
        logger.error(f"Campaign failed: {e}")
        print(f"\n❌ Campaign failed: {e}")
        print("Check coldmailer.log for details.")

if __name__ == "__main__":
    main()
