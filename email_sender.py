import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
import logging
from typing import List, Dict, Optional
from config import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, SUBJECT_PREFIX
import pandas as pd
from datetime import datetime
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.email_address = EMAIL_ADDRESS
        self.email_password = EMAIL_PASSWORD
        self.sent_emails = []
        self.failed_emails = []
        self.delay_between_emails = 30  # seconds to avoid spam filters
        
    def validate_credentials(self) -> bool:
        """Validate SMTP credentials"""
        if not all([self.email_address, self.email_password, self.smtp_server]):
            logger.error("Email credentials not configured. Please check your .env file.")
            return False
        
        # Check if using Gmail and validate App Password format
        if '@gmail.com' in self.email_address.lower():
            if not self._validate_gmail_app_password():
                return False
        
        return True
    
    def _validate_gmail_app_password(self) -> bool:
        """Validate Gmail App Password format"""
        # Gmail App Passwords are 16 characters with spaces
        # Format: "abcd efgh ijkl mnop"
        if len(self.email_password.replace(' ', '')) != 16:
            logger.error("Invalid Gmail App Password format. Should be 16 characters like: 'abcd efgh ijkl mnop'")
            logger.error("Get your App Password from: Google Account → Security → App passwords")
            return False
        
        if not re.match(r'^[a-z]{4}\s[a-z]{4}\s[a-z]{4}\s[a-z]{4}$', self.email_password.lower()):
            logger.error("Invalid Gmail App Password format. Should be lowercase letters with spaces.")
            return False
        
        logger.info("Gmail App Password format validated successfully")
        return True
    
    def test_connection(self) -> bool:
        """Test SMTP connection with detailed error handling"""
        try:
            logger.info("Testing SMTP connection...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.quit()
            logger.info("SMTP connection successful")
            return True
        except smtplib.SMTPAuthenticationError as e:
            error_msg = str(e)
            if "OAuth" in error_msg:
                logger.error("OAuth authentication error. Use Gmail App Password instead of OAuth.")
                logger.error("Get App Password: Google Account → Security → App passwords")
            elif "Username and Password not accepted" in error_msg:
                logger.error("Authentication failed. Check your email and App Password.")
                logger.error("Make sure you're using the App Password, not your regular Gmail password.")
            else:
                logger.error(f"Authentication error: {error_msg}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def send_single_email(self, recipient_email: str, subject: str, body: str, 
                         professor_info: Dict = None, attachment_path: str = None) -> Dict:
        """
        Send a single email
        
        Args:
            recipient_email: Email address of the recipient
            subject: Email subject line
            body: Email body content
            professor_info: Dictionary containing professor information
            attachment_path: Path to attachment file (optional)
            
        Returns:
            Dictionary with send status and details
        """
        if not self.validate_credentials():
            return {
                'success': False,
                'error': 'Email credentials not configured',
                'recipient': recipient_email
            }
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment if provided
            if attachment_path and os.path.exists(attachment_path):
                try:
                    with open(attachment_path, "rb") as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                    
                    encoders.encode_base64(part)
                    filename = os.path.basename(attachment_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {filename}',
                    )
                    msg.attach(part)
                    logger.info(f"Added attachment: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to add attachment {attachment_path}: {e}")
            elif attachment_path and not os.path.exists(attachment_path):
                logger.warning(f"Attachment file not found: {attachment_path}")
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, recipient_email, text)
            server.quit()
            
            result = {
                'success': True,
                'recipient': recipient_email,
                'subject': subject,
                'timestamp': datetime.now().isoformat(),
                'professor_info': professor_info or {}
            }
            
            self.sent_emails.append(result)
            logger.info(f"Email sent successfully to {recipient_email}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to send email to {recipient_email}: {error_msg}")
            
            result = {
                'success': False,
                'recipient': recipient_email,
                'error': error_msg,
                'timestamp': datetime.now().isoformat(),
                'professor_info': professor_info or {}
            }
            
            self.failed_emails.append(result)
            return result
    
    def send_bulk_emails(self, emails_data: List[Dict], delay: int = None, attachment_path: str = None) -> Dict:
        """
        Send multiple emails with delay between sends
        
        Args:
            emails_data: List of dictionaries containing email information
            delay: Delay between emails in seconds (default: self.delay_between_emails)
            attachment_path: Path to attachment file to include with all emails (optional)
            
        Returns:
            Dictionary with summary of sending results
        """
        if not emails_data:
            return {'success': False, 'error': 'No emails to send'}
        
        delay = delay or self.delay_between_emails
        total_emails = len(emails_data)
        successful_sends = 0
        failed_sends = 0
        
        logger.info(f"Starting bulk email sending for {total_emails} emails")
        
        for i, email_data in enumerate(emails_data, 1):
            recipient_email = email_data.get('email')
            subject = email_data.get('subject')
            body = email_data.get('body')
            professor_info = email_data.get('professor_info', {})
            
            if not all([recipient_email, subject, body]):
                logger.warning(f"Skipping email {i}: Missing required fields")
                failed_sends += 1
                continue
            
            logger.info(f"Sending email {i}/{total_emails} to {recipient_email}")
            
            result = self.send_single_email(recipient_email, subject, body, professor_info, attachment_path)
            
            if result['success']:
                successful_sends += 1
            else:
                failed_sends += 1
            
            # Add delay between emails to avoid spam filters
            if i < total_emails:  # Don't delay after the last email
                logger.info(f"Waiting {delay} seconds before next email...")
                time.sleep(delay)
        
        summary = {
            'total_emails': total_emails,
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'success_rate': (successful_sends / total_emails) * 100 if total_emails > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Bulk email sending completed: {successful_sends}/{total_emails} successful")
        return summary
    
    def create_email_data(self, professors: List[Dict], personalized_emails: List[str], 
                         base_subject: str) -> List[Dict]:
        """
        Create email data structure for bulk sending
        
        Args:
            professors: List of professor information dictionaries
            personalized_emails: List of personalized email bodies
            base_subject: Base subject line for emails
            
        Returns:
            List of email data dictionaries
        """
        if len(professors) != len(personalized_emails):
            raise ValueError("Number of professors must match number of personalized emails")
        
        emails_data = []
        
        for professor, email_body in zip(professors, personalized_emails):
            # Create personalized subject
            subject = self._create_personalized_subject(base_subject, professor)
            
            email_data = {
                'email': professor['email'],
                'subject': subject,
                'body': email_body,
                'professor_info': professor
            }
            emails_data.append(email_data)
        
        return emails_data
    
    def _create_personalized_subject(self, base_subject: str, professor_info: Dict) -> str:
        """Create a personalized subject line"""
        name = professor_info.get('name', '')
        affiliation = professor_info.get('affiliation', '')
        
        # Extract last name for personalization
        last_name = name.split()[-1] if name else 'Professor'
        
        # Personalize subject if it contains placeholders
        subject = base_subject
        if '[LAST_NAME]' in subject:
            subject = subject.replace('[LAST_NAME]', last_name)
        if '[AFFILIATION]' in subject:
            subject = subject.replace('[AFFILIATION]', affiliation)
        
        # Add prefix if not already present
        if not subject.startswith(SUBJECT_PREFIX):
            subject = f"{SUBJECT_PREFIX} {subject}"
        
        return subject
    
    def save_sending_report(self, filename: str = None) -> str:
        """Save detailed report of email sending results"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_report_{timestamp}.csv"
        
        # Combine sent and failed emails
        all_results = []
        
        for result in self.sent_emails:
            all_results.append({
                'Status': 'Success',
                'Email': result['recipient'],
                'Subject': result['subject'],
                'Timestamp': result['timestamp'],
                'Professor Name': result.get('professor_info', {}).get('name', ''),
                'Affiliation': result.get('professor_info', {}).get('affiliation', ''),
                'Error': ''
            })
        
        for result in self.failed_emails:
            all_results.append({
                'Status': 'Failed',
                'Email': result['recipient'],
                'Subject': result.get('subject', ''),
                'Timestamp': result['timestamp'],
                'Professor Name': result.get('professor_info', {}).get('name', ''),
                'Affiliation': result.get('professor_info', {}).get('affiliation', ''),
                'Error': result.get('error', '')
            })
        
        if all_results:
            df = pd.DataFrame(all_results)
            df.to_csv(filename, index=False)
            logger.info(f"Email sending report saved to {filename}")
            return filename
        else:
            logger.warning("No email results to save")
            return ""
    
    def get_sending_statistics(self) -> Dict:
        """Get statistics about email sending"""
        total_attempted = len(self.sent_emails) + len(self.failed_emails)
        successful = len(self.sent_emails)
        failed = len(self.failed_emails)
        
        return {
            'total_attempted': total_attempted,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_attempted * 100) if total_attempted > 0 else 0,
            'last_sent': self.sent_emails[-1]['timestamp'] if self.sent_emails else None,
            'last_failed': self.failed_emails[-1]['timestamp'] if self.failed_emails else None
        }
    
    def resend_failed_emails(self, delay: int = None) -> Dict:
        """Resend emails that previously failed"""
        if not self.failed_emails:
            logger.info("No failed emails to resend")
            return {'success': True, 'message': 'No failed emails to resend'}
        
        logger.info(f"Resending {len(self.failed_emails)} failed emails")
        
        # Extract email data from failed emails
        emails_to_resend = []
        for failed_email in self.failed_emails:
            if 'professor_info' in failed_email:
                professor_info = failed_email['professor_info']
                emails_to_resend.append({
                    'email': failed_email['recipient'],
                    'subject': failed_email.get('subject', ''),
                    'body': '',  # This would need to be reconstructed
                    'professor_info': professor_info
                })
        
        # Clear failed emails list
        self.failed_emails = []
        
        # Resend emails
        return self.send_bulk_emails(emails_to_resend, delay)

if __name__ == "__main__":
    # Example usage
    sender = EmailSender()
    
    # Test connection
    if sender.test_connection():
        print("SMTP connection successful!")
        
        # Example email data
        test_email_data = [
            {
                'email': 'lakshya16jain@gmail.com',
                'subject': 'Test Email',
                'body': 'This is a test email.',
                'professor_info': {'name': 'Test Professor', 'affiliation': 'Test University'}
            }
        ]
        
        # Send test email (commented out to avoid actually sending)
        result = sender.send_bulk_emails(test_email_data)
        print(f"Email sending result: {result}")
        
    else:
        print("SMTP connection failed. Please check your credentials.")
