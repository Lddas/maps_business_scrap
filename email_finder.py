"""
Email Finder - Finds email addresses for businesses
Uses multiple strategies to find business emails
"""
import re
import requests
import os
from dotenv import load_dotenv
from typing import Optional, Dict

load_dotenv()


class EmailFinder:
    def __init__(self):
        # Hunter.io API key (optional - add to .env)
        self.hunter_api_key = os.getenv('HUNTER_API_KEY')
        self.use_hunter = bool(self.hunter_api_key)
        
        if not self.use_hunter:
            print("⚠️  Hunter.io API key not found. Email finding will use pattern-based methods only.")
            print("   To enable better email finding, add HUNTER_API_KEY to your .env file")
            print("   Sign up at: https://hunter.io/api")
    
    def find_email(self, business_name: str, domain: Optional[str] = None, 
                   location: Optional[str] = None) -> Optional[str]:
        """
        Try to find email address for a business
        
        Args:
            business_name: Name of the business
            domain: Website domain (if available)
            location: Location/city (for better search)
        
        Returns:
            Email address if found, None otherwise
        """
        # Strategy 1: Use Hunter.io API if available
        if self.use_hunter and domain:
            email = self._find_with_hunter(domain, business_name)
            if email:
                return email
        
        # Strategy 2: Use Hunter.io domain search (without specific person)
        if self.use_hunter and domain:
            email = self._find_domain_emails(domain)
            if email:
                return email
        
        # Strategy 3: Try to construct common email patterns (not verified)
        # Note: We don't verify these, so we return None
        # If you want to try pattern matching, you can uncomment:
        # if domain:
        #     email = self._try_common_patterns(domain, business_name)
        #     if email:
        #         return email
        
        return None
    
    def _find_with_hunter(self, domain: str, business_name: str) -> Optional[str]:
        """Find email using Hunter.io API"""
        if not self.hunter_api_key:
            return None
        
        try:
            # Try to find emails for the domain
            url = f"https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': self.hunter_api_key,
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get('emails'):
                    # Return the first email found
                    return data['data']['emails'][0]['value']
        except Exception as e:
            print(f"  ⚠️  Hunter.io error: {e}")
        
        return None
    
    def _find_domain_emails(self, domain: str) -> Optional[str]:
        """Find any email from the domain using Hunter.io"""
        if not self.hunter_api_key:
            return None
        
        try:
            url = f"https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': self.hunter_api_key,
                'limit': 5
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and data['data'].get('emails'):
                    # Prefer info@, contact@, hello@, then any email
                    preferred_patterns = ['info', 'contact', 'hello', 'support', 'sales']
                    emails = data['data']['emails']
                    
                    for pattern in preferred_patterns:
                        for email_data in emails:
                            email = email_data['value']
                            if pattern in email.lower():
                                return email
                    
                    # Return first email if no preferred found
                    return emails[0]['value']
        except Exception as e:
            pass
        
        return None
    
    def _try_common_patterns(self, domain: str, business_name: str) -> Optional[str]:
        """Try common email patterns"""
        # Remove common suffixes and clean business name
        name_clean = business_name.lower()
        name_clean = re.sub(r'\s+(inc|llc|ltd|corp|corporate|company|co)\.?$', '', name_clean)
        name_clean = re.sub(r'[^a-z0-9\s]', '', name_clean)
        words = name_clean.split()
        
        if not words:
            return None
        
        # Common patterns to try
        patterns = [
            f"info@{domain}",
            f"contact@{domain}",
            f"hello@{domain}",
            f"sales@{domain}",
            f"{words[0]}@{domain}",  # First word
            f"{''.join(words[:2])}@{domain}",  # First two words combined
        ]
        
        # Note: We don't actually verify these emails exist
        # This is just pattern guessing - not reliable
        # Return None to indicate we can't verify
        return None
    
    def find_emails_batch(self, businesses: list) -> list:
        """
        Find emails for a list of businesses
        Adds 'email' field to each business dict
        
        Args:
            businesses: List of business dicts with 'name', 'website' (optional), 'address'
        
        Returns:
            Updated list with 'email' field added
        """
        print(f"\n🔍 Searching for email addresses...")
        print(f"   Processing {len(businesses)} businesses...\n")
        
        found_count = 0
        for i, business in enumerate(businesses, 1):
            business_name = business.get('name', '')
            website = business.get('website', '')
            
            # Extract domain from website if available
            domain = None
            if website:
                domain = self._extract_domain(website)
            
            # Extract domain from Google Maps URL if no website
            if not domain:
                google_url = business.get('google_maps_url', '')
                # Try to find domain in address or other fields
                # This is a fallback - not ideal but might help
                pass
            
            email = None
            if domain:
                email = self.find_email(business_name, domain)
            
            business['email'] = email if email else ''
            
            if email:
                found_count += 1
                print(f"  [{i}/{len(businesses)}] ✓ {business_name}: {email}")
            else:
                print(f"  [{i}/{len(businesses)}] ✗ {business_name}: Not found")
        
        print(f"\n✅ Found {found_count}/{len(businesses)} email addresses")
        return businesses
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        if not url:
            return None
        
        # Remove protocol
        domain = re.sub(r'^https?://', '', url)
        # Remove www.
        domain = re.sub(r'^www\.', '', domain)
        # Remove path and query
        domain = domain.split('/')[0]
        domain = domain.split('?')[0]
        
        return domain if domain else None


# Alternative: Manual email finding helper
def prompt_for_emails(businesses: list) -> list:
    """
    Helper function to manually add emails
    Can be used if automatic finding doesn't work well
    """
    print("\n" + "=" * 70)
    print("📧 Manual Email Entry")
    print("=" * 70)
    print("\nYou can manually add emails to the Excel file after export.")
    print("Or use an email finding service like:")
    print("  • Hunter.io (https://hunter.io)")
    print("  • Clearbit (https://clearbit.com)")
    print("  • RocketReach (https://rocketreach.co)")
    print()
    
    # Just add empty email field for now
    for business in businesses:
        if 'email' not in business:
            business['email'] = ''
    
    return businesses

