"""
Google Places API Scraper - Finds businesses without websites using the official API
"""
import time
import requests
import os
from dotenv import load_dotenv
from usage_tracker import UsageTracker

load_dotenv()


class GooglePlacesAPIScraper:
    def __init__(self, delay_between_requests=1.0):
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_PLACES_API_KEY not found in .env file. Get one from https://console.cloud.google.com/")
        
        self.base_url = "https://places.googleapis.com/v1"
        self.delay_between_requests = delay_between_requests
        self.businesses = []
        self.usage_tracker = UsageTracker()
        
        # Show initial usage stats
        print("\n" + "=" * 70)
        print("📊 Starting API-based search")
        self.usage_tracker.print_stats()
    
    def search_businesses(self, city, business_type, max_results=50, radius_km=10):
        """
        Search for businesses using Google Places API Text Search
        
        Args:
            city: City name (e.g., "Boston")
            business_type: Type of business (e.g., "garage")
            max_results: Maximum number of businesses to search
        """

        query = f"{business_type} in {city}"
        print(f"\n🔍 Searching for: {query}")
        print(f"📍 Radius: {radius_km} km")
        print(f"📊 Maximum results: {max_results}\n")

        location_bias = self._get_location_bias(city, radius_km)
        
        all_businesses = []
        next_page_token = None
        
        while len(all_businesses) < max_results:
            # Calculate how many more we need
            remaining = max_results - len(all_businesses)
            max_result_count = min(20, remaining)  # API allows max 20 per request
            
            url = f"{self.base_url}/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.googleMapsUri"
            }
            
            data = {
                "textQuery": query,
                "maxResultCount": max_result_count
            }

            if location_bias:
                data["locationBias"] = location_bias
            
            # Add pagination token if we have one
            if next_page_token:
                data["pageToken"] = next_page_token
            
            try:
                response = requests.post(url, headers=headers, json=data)
                
                # Track API request
                self.usage_tracker.track_request(success=response.status_code == 200)
                
                if response.status_code == 200:
                    results = response.json()
                    places = results.get('places', [])
                    
                    for place in places:
                        business = {
                            'name': place.get('displayName', {}).get('text', 'Unknown'),
                            'address': place.get('formattedAddress', 'N/A'),
                            'phone': place.get('nationalPhoneNumber', 'N/A'),
                            'rating': place.get('rating', 0),
                            'reviews_count': place.get('userRatingCount', 0),
                            'google_maps_url': place.get('googleMapsUri', ''),
                            'website': place.get('websiteUri', ''),
                            'place_id': place.get('id', ''),
                            'business_type': business_type  # Store the business type searched
                        }
                        all_businesses.append(business)
                        print(f"  ✓ Found: {business['name']}")
                    
                    # Check if there are more results
                    next_page_token = results.get('nextPageToken')
                    if not next_page_token or len(all_businesses) >= max_results:
                        break
                    
                    # Wait before next request (rate limiting)
                    if len(all_businesses) < max_results:
                        time.sleep(self.delay_between_requests)
                
                elif response.status_code == 403:
                    error_data = response.json()
                    if 'rateLimitExceeded' in str(error_data):
                        print(f"⚠️  Rate limit hit, waiting {self.delay_between_requests * 2} seconds...")
                        time.sleep(self.delay_between_requests * 2)
                        continue
                    else:
                        print(f"❌ API error: {response.text}")
                        break
                else:
                    print(f"❌ API error {response.status_code}: {response.text}")
                    break
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                break
        
        self.businesses = all_businesses[:max_results]
        print(f"\n✅ Found {len(self.businesses)} businesses total")
        return self.businesses
    
    def format_businesses_for_export(self):
        """
        Format businesses for Excel export with requested columns:
        - name
        - business_type
        - phone
        - website (URL or empty)
        - has_website (Yes/No)
        - contacted (No by default)
        - response (empty for manual entry)
        """
        formatted_businesses = []
        for biz in self.businesses:
            website = biz.get('website', '')
            has_website = 'Yes' if website and website != '' else 'No'
            
            formatted_business = {
                'name': biz.get('name', 'Unknown'),
                'business_type': biz.get('business_type', ''),
                'phone': biz.get('phone', 'N/A'),
                'website': website if website else '',
                'has_website': has_website,
                'contacted': 'No',  # Default to No
                'response': ''  # Empty for manual entry
            }
            formatted_businesses.append(formatted_business)
        
        return formatted_businesses
    
    def filter_businesses_without_websites(self):
        """
        Filter businesses that don't have websites
        DEPRECATED: Use format_businesses_for_export() instead
        """
        businesses_without_websites = []
        for biz in self.businesses:
            if not biz.get('website') or biz.get('website') == '':
                businesses_without_websites.append(biz)
        
        return businesses_without_websites
    
    def print_usage_stats(self):
        """Print API usage statistics"""
        self.usage_tracker.print_stats()
    
    def get_usage_stats(self):
        """Get usage statistics as dict"""
        return self.usage_tracker.get_stats()

    def _get_location_bias(self, city, radius_km):
        """Get location bias circle for the city"""
        if not city or radius_km <= 0:
            return None

        try:
            url = f"{self.base_url}/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.location"
            }
            data = {
                "textQuery": city,
                "maxResultCount": 1
            }

            response = requests.post(url, headers=headers, json=data)
            self.usage_tracker.track_request(success=response.status_code == 200)

            if response.status_code == 200:
                results = response.json()
                places = results.get('places', [])
                if places:
                    location = places[0].get('location')
                    if location:
                        lat = location.get('latitude')
                        lng = location.get('longitude')
                        if lat is not None and lng is not None:
                            radius_meters = int(radius_km * 1000)
                            return {
                                "circle": {
                                    "center": {
                                        "latitude": lat,
                                        "longitude": lng
                                    },
                                    "radius": radius_meters
                                }
                            }
        except Exception:
            pass

        print("⚠️  Could not determine city center. Continuing without radius filter.")
        return None

