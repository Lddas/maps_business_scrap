"""
Standalone email automation script
Use this after adding email addresses to the Excel file
"""
import pandas as pd
from email_automation import EmailAutomation
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python send_emails.py <excel_file>")
        print("Example: python send_emails.py businesses_without_websites.xlsx")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    
    try:
        # Load Excel file
        df = pd.read_excel(excel_file, engine='openpyxl')
        print(f"Loaded {len(df)} businesses from {excel_file}")
        
        # Check if email column exists
        if 'email' not in df.columns:
            print("\n❌ Error: No 'email' column found in the Excel file!")
            print("Please add an 'email' column with email addresses.")
            sys.exit(1)
        
        # Count businesses with emails
        businesses_with_emails = df[df['email'].notna() & (df['email'] != '')]
        print(f"Found {len(businesses_with_emails)} businesses with email addresses")
        
        if len(businesses_with_emails) == 0:
            print("No email addresses found!")
            sys.exit(1)
        
        # Ask for confirmation
        confirm = input(f"\nSend emails to {len(businesses_with_emails)} businesses? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("Cancelled.")
            sys.exit(0)
        
        # Send emails
        email_automation = EmailAutomation()
        email_automation.send_bulk_emails(businesses_with_emails)
        
    except FileNotFoundError:
        print(f"❌ Error: File '{excel_file}' not found!")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

