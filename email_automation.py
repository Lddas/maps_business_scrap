"""
Email Automation - Sends personalized emails to businesses
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import pandas as pd
import time

load_dotenv()


class EmailAutomation:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
    def load_email_template(self, template_path='email_template.txt'):
        """Load email template from file"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Default template
            return """Subject: Professional Website Solution for {business_name}

Hello {business_name} Team,

I hope this email finds you well. I noticed that {business_name} located at {address} doesn't currently have a website presence online.

In today's digital age, having a professional website is crucial for business growth and customer acquisition. We specialize in creating affordable, professional websites tailored for businesses like yours.

Our services include:
- Custom website design
- Mobile-responsive layouts
- SEO optimization
- Easy content management
- Affordable pricing

Would you be interested in learning more about how we can help establish your online presence? I'd be happy to schedule a quick call to discuss your needs.

Best regards,
Website Market Team

---
This email was sent to {business_name} at {address}.
If you'd like to unsubscribe, please reply with "UNSUBSCRIBE".
"""
    
    def personalize_email(self, template, business_info):
        """Personalize email template with business information"""
        email_content = template.format(
            business_name=business_info.get('name', 'Valued Business'),
            address=business_info.get('address', 'your location'),
            phone=business_info.get('phone', 'N/A')
        )
        return email_content
    
    def send_email(self, recipient_email, subject, body):
        """Send a single email"""
        if not self.email_address or not self.email_password:
            print("Email credentials not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in .env file")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent successfully to {recipient_email}")
            return True
        except Exception as e:
            print(f"Error sending email to {recipient_email}: {str(e)}")
            return False
    
    def send_bulk_emails(self, businesses_df, template_path='email_template.txt', delay=5):
        """
        Send emails to all businesses in the DataFrame
        
        Args:
            businesses_df: DataFrame with business information
            template_path: Path to email template file
            delay: Delay between emails in seconds
        """
        if businesses_df is None or businesses_df.empty:
            print("No businesses to email")
            return
        
        template = self.load_email_template(template_path)
        
        # Note: We'll need email addresses. For now, we'll try to extract from business info
        # or you can add email column manually to the Excel file
        
        sent_count = 0
        failed_count = 0
        
        for index, row in businesses_df.iterrows():
            business_info = row.to_dict()
            
            # Try to get email - you may need to add this manually to Excel
            recipient_email = business_info.get('email', '')
            
            if not recipient_email:
                print(f"Skipping {business_info.get('name')} - no email address found")
                print("Tip: Add email addresses to the Excel file and re-run, or use the 'email' column")
                failed_count += 1
                continue
            
            subject = f"Professional Website Solution for {business_info.get('name', 'Your Business')}"
            body = self.personalize_email(template, business_info)
            
            if self.send_email(recipient_email, subject, body):
                sent_count += 1
            else:
                failed_count += 1
            
            # Be respectful - add delay between emails
            if delay > 0:
                time.sleep(delay)
        
        print(f"\nEmail sending complete!")
        print(f"Sent: {sent_count}")
        print(f"Failed: {failed_count}")

