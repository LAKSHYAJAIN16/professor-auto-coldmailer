#!/usr/bin/env python3
"""
Quick Campaign Runner - Command Line Interface

Usage:
    python run_campaign.py "Email Title" "PDF_Path" [num_professors]

Example:
    python run_campaign.py "Research Collaboration - Decision Making Games" "Lakshya Research Draft.pdf" 15
"""

import sys
import os
from simple_coldmailer import SimpleColdMailer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_campaign.py \"Email Title\" \"PDF_Path\" [num_professors]")
        print("Example: python run_campaign.py \"Research Collaboration\" \"research.pdf\" 10")
        return
    
    email_title = sys.argv[1]
    pdf_path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].strip() else None
    num_professors = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].strip().isdigit() else 10
    
    # Check if PDF exists
    if pdf_path and not os.path.exists(pdf_path):
        print(f"Warning: PDF file '{pdf_path}' not found. Proceeding without attachment.")
        pdf_path = None
    
    print(f"Starting campaign:")
    print(f"  Title: {email_title}")
    print(f"  PDF: {pdf_path if pdf_path else 'None'}")
    print(f"  Target: {num_professors} professors")
    print()
    
    try:
        cold_mailer = SimpleColdMailer()
        results = cold_mailer.run_campaign(email_title, pdf_path, num_professors)
        
        if results:
            print(f"\n🎯 FINAL SUMMARY:")
            print(f"   ✅ Found {results['professors_found']} professors")
            print(f"   📧 Sent {results['emails_sent']} emails")
            print(f"   📊 Success rate: {results['success_rate']:.1f}%")
            print(f"   📁 Professors file: {results['professors_file']}")
            print(f"   📋 Report file: {results['report_file']}")
            
    except KeyboardInterrupt:
        print("\n\n❌ Campaign interrupted by user.")
    except Exception as e:
        logger.error(f"Campaign failed: {e}")
        print(f"\n❌ Campaign failed: {e}")

if __name__ == "__main__":
    main()
