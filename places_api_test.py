"""
Google Places API - Simple website checker
This is the PROPER way to check if a business has a website - much more reliable than scraping!
"""
import requests
import json
import os
from dotenv import load_dotenv
import re
import urllib.parse
import time
from usage_tracker import UsageTracker

load_dotenv()


class GooglePlacesAPI:
    def __init__(self, delay_between_requests=1.0, track_usage=True):
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_PLACES_API_KEY not found in .env file. Get one from https://console.cloud.google.com/")
        
        self.base_url = "https://places.googleapis.com/v1"
        self.delay_between_requests = delay_between_requests  # Delay in seconds to avoid rate limits
        self.track_usage = track_usage
        self.usage_tracker = UsageTracker() if track_usage else None
        
        # Show initial usage stats
        if self.usage_tracker:
            self.usage_tracker.print_stats()
    
    def extract_place_id_from_url(self, maps_url):
        """Extract place_id from Google Maps URL"""
        # The NEW Places API uses place IDs in format: ChIJ... or /g/11...
        # Look for the !16s pattern which contains the place ID
        # Format: !16s%2Fg%2F11qpddhs0r (URL encoded: /g/11qpddhs0r)
        
        import urllib.parse
        
        # Pattern 1: Look for !16s followed by encoded place ID
        pattern1 = r'!16s([^?]+)'
        match = re.search(pattern1, maps_url)
        if match:
            place_id_encoded = match.group(1)
            place_id = urllib.parse.unquote(place_id_encoded)
            # Remove leading / if present
            if place_id.startswith('/'):
                place_id = place_id[1:]
            return place_id
        
        # Pattern 2: Look for place_id parameter
        pattern2 = r'place_id=([^&]+)'
        match = re.search(pattern2, maps_url)
        if match:
            return urllib.parse.unquote(match.group(1))
        
        # Pattern 3: Extract from !3m6!1s... format (old format)
        pattern3 = r'!3m6!1s([^!]+)!'
        match = re.search(pattern3, maps_url)
        if match:
            place_id = match.group(1)
            # This is the old format, we'll need to convert it
            # For now, return it and try to use it
            return place_id
        
        return None
    
    def check_website(self, maps_url):
        """
        Check if a business has a website using Google Places API
        
        Returns:
            dict with 'has_website' (bool), 'website_url' (str or None), 'name' (str)
        """
        # Extract business name from URL to search for it
        place_name_match = re.search(r'/place/([^/@]+)', maps_url)
        if place_name_match:
            place_name = place_name_match.group(1).replace('+', ' ').replace('%7C', '|').replace('%26', '&')
            # Clean up the name
            place_name = urllib.parse.unquote(place_name)
            print(f"DEBUG: Searching for: {place_name}")
        else:
            return {
                'has_website': False,
                'website_url': None,
                'name': None,
                'error': 'Could not extract place name from URL'
            }
        
        # Use Text Search to find the place
        url = f"{self.base_url}/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.websiteUri"
        }
        data = {
            "textQuery": place_name,
            "maxResultCount": 1
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            print(f"DEBUG: API call to: {url}")
            print(f"DEBUG: Response status: {response.status_code}")
            
            # Track the API request
            if self.usage_tracker:
                self.usage_tracker.track_request(success=response.status_code == 200)
            
            # Handle rate limiting - retry after delay
            if response.status_code == 403:
                error_data = response.json()
                if 'API_KEY_SERVICE_BLOCKED' in str(error_data) or 'rateLimitExceeded' in str(error_data):
                    print(f"DEBUG: Rate limit hit, waiting {self.delay_between_requests * 2} seconds...")
                    time.sleep(self.delay_between_requests * 2)
                    # Retry once
                    response = requests.post(url, headers=headers, json=data)
                    print(f"DEBUG: Retry response status: {response.status_code}")
                    # Track retry
                    if self.usage_tracker:
                        self.usage_tracker.track_request(success=response.status_code == 200)
            
            if response.status_code == 200:
                results = response.json()
                if results.get('places') and len(results['places']) > 0:
                    place = results['places'][0]
                    website_uri = place.get('websiteUri')
                    name = place.get('displayName', {}).get('text', 'Unknown')
                    
                    return {
                        'has_website': website_uri is not None and website_uri != '',
                        'website_url': website_uri,
                        'name': name,
                        'place_id': place.get('id')
                    }
                else:
                    return {
                        'has_website': False,
                        'website_url': None,
                        'name': None,
                        'error': 'Place not found in search results'
                    }
            else:
                return {
                    'has_website': False,
                    'website_url': None,
                    'name': None,
                    'error': f"API error: {response.status_code} - {response.text}"
                }
        except Exception as e:
            return {
                'has_website': False,
                'website_url': None,
                'name': None,
                'error': str(e)
            }
    
    def search_place_id(self, query):
        """Search for place_id using Text Search API"""
        url = f"{self.base_url}/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName"
        }
        data = {
            "textQuery": query
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            # Track API request
            if self.usage_tracker:
                self.usage_tracker.track_request(success=response.status_code == 200)
            
            if response.status_code == 200:
                results = response.json()
                if results.get('places') and len(results['places']) > 0:
                    return results['places'][0]['id']
        except Exception as e:
            print(f"Error searching place: {e}")
        
        return None


def main():
    print("=" * 60)
    print("Google Places API - Website Checker")
    print("=" * 60)
    print()
    
    # Test URLs
    test_urls = [
        "https://www.google.com/maps/place/Monkey+Garage+Bali/@-8.6887578,115.198473,9331m/data=!3m1!1e3!4m10!1m2!2m1!1sgarage+bali!3m6!1s0x2dd241626ecd4139:0x4b436138894a4e17!8m2!3d-8.6887578!4d115.2365818!15sCgtnYXJhZ2UgYmFsaZIBEGF1dG9fcmVwYWlyX3Nob3DgAQA!16s%2Fg%2F11qpddhs0r?entry=ttu&g_ep=EgoyMDI1MTEwMi4wIKXMDSoASAFQAw%3D%3D",
        "https://www.google.com/maps/place/Bikini+Garage+%7C+Luxury+Car+Rental+Bali+%7C+Sewa+Mobil+Mewah+Bali/@-8.6726786,115.1464309,9331m/data=!3m1!1e3!4m10!1m2!2m1!1sgarage+bali!3m6!1s0x2dd247d000fa1343:0xc7a3e454edcf1946!8m2!3d-8.6726786!4d115.1845397!15sCgtnYXJhZ2UgYmFsaVoNIgtnYXJhZ2UgYmFsaZIBEWNhcl9yZW50YWxfYWdlbmN54AEA!16s%2Fg%2F11txh7_lpt?entry=ttu&g_ep=EgoyMDI1MTEwMi4wIKXMDSoASAFQAw%3D%3D",
        "https://www.google.com/maps/place/Brodking+Scooter+Garage+%26+Cafe/@-8.8034939,115.1171391,9328m/data=!3m1!1e3!4m10!1m2!2m1!1sgarage+bali!3m6!1s0x2dd244c4e22580bb:0xae97fbe9210941a4!8m2!3d-8.8034939!4d115.1552479!15sCgtnYXJhZ2UgYmFsaZIBE3Njb290ZXJfcmVwYWlyX3Nob3DgAQA!16s%2Fg%2F11hbrwplfg?entry=ttu&g_ep=EgoyMDI1MTEwMi4wIKXMDSoASAFQAw%3D%3D",
    ]
    
    try:
        api = GooglePlacesAPI()
        
        print("Testing with Google Places API...\n")
        
        for i, url in enumerate(test_urls, 1):
            print(f"[{i}/{len(test_urls)}] Checking: {url[:60]}...")
            result = api.check_website(url)
            
            if result.get('error'):
                print(f"  ❌ Error: {result['error']}")
            else:
                name = result.get('name', 'Unknown')
                has_website = result.get('has_website', False)
                website_url = result.get('website_url')
                
                print(f"  Name: {name}")
                if has_website:
                    print(f"  ✅ HAS WEBSITE: {website_url}")
                else:
                    print(f"  ✅ NO WEBSITE")
            print()
            
            # Add delay between requests to avoid rate limits (except for last one)
            if i < len(test_urls):
                time.sleep(api.delay_between_requests)
        
        # Show final usage stats
        if api.usage_tracker:
            api.usage_tracker.print_stats()
        
        print("=" * 60)
        print("✅ API method is much more reliable than scraping!")
        
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\n📋 Setup Instructions:")
        print("1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project (or use existing)")
        print("3. Enable 'Places API (New)'")
        print("4. Create API Key (Credentials > Create Credentials > API Key)")
        print("5. Add to .env file: GOOGLE_PLACES_API_KEY=your_key_here")
        print("\n💰 Cost: $200 free credit/month, then ~$0.017 per request")
        print("   (Very cheap - 1,000 checks = ~$17/month)")


if __name__ == "__main__":
    main()
