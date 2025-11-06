"""
Debug script - Test with hardcoded businesses to debug website detection
"""
import sys
from scraper import GoogleMapsScraper
from exporter import DataExporter

# Hardcoded garage businesses in Bali for testing
HARDCODED_BALI_GARAGES = [
    # Monkey Garage Bali - should NOT have website
    "https://www.google.com/maps/place/Monkey+Garage+Bali/@-8.6887578,115.198473,9331m/data=!3m1!1e3!4m10!1m2!2m1!1sgarage+bali!3m6!1s0x2dd241626ecd4139:0x4b436138894a4e17!8m2!3d-8.6887578!4d115.2365818!15sCgtnYXJhZ2UgYmFsaZIBEGF1dG9fcmVwYWlyX3Nob3DgAQA!16s%2Fg%2F11qpddhs0r?entry=ttu&g_ep=EgoyMDI1MTEwMi4wIKXMDSoASAFQAw%3D%3D",
    # Bikini Garage - should have website
    "https://www.google.com/maps/place/Bikini+Garage+%7C+Luxury+Car+Rental+Bali+%7C+Sewa+Mobil+Mewah+Bali/@-8.6726786,115.1464309,9331m/data=!3m1!1e3!4m10!1m2!2m1!1sgarage+bali!3m6!1s0x2dd247d000fa1343:0xc7a3e454edcf1946!8m2!3d-8.6726786!4d115.1845397!15sCgtnYXJhZ2UgYmFsaVoNIgtnYXJhZ2UgYmFsaZIBEWNhcl9yZW50YWxfYWdlbmN54AEA!16s%2Fg%2F11txh7_lpt?entry=ttu&g_ep=EgoyMDI1MTEwMi4wIKXMDSoASAFQAw%3D%3D",
    # Brodking Scooter Garage - should check if it has website
    "https://www.google.com/maps/place/Brodking+Scooter+Garage+%26+Cafe/@-8.8034939,115.1171391,9328m/data=!3m1!1e3!4m10!1m2!2m1!1sgarage+bali!3m6!1s0x2dd244c4e22580bb:0xae97fbe9210941a4!8m2!3d-8.8034939!4d115.1552479!15sCgtnYXJhZ2UgYmFsaZIBE3Njb290ZXJfcmVwYWlyX3Nob3DgAQA!16s%2Fg%2F11hbrwplfg?entry=ttu&g_ep=EgoyMDI1MTEwMi4wIKXMDSoASAFQAw%3D%3D",
]


def main():
    print("=" * 60)
    print("DEBUG MODE - Testing with hardcoded Bali garages")
    print("=" * 60)
    print(f"\nTesting {len(HARDCODED_BALI_GARAGES)} businesses...")
    print("Checking each one individually for website presence.\n")
    
    scraper = GoogleMapsScraper(headless=False)
    try:
        scraper.setup_driver()
        
        businesses = []
        for i, url in enumerate(HARDCODED_BALI_GARAGES, 1):
            print(f"\n[{i}/{len(HARDCODED_BALI_GARAGES)}] Checking: {url[:70]}...")
            
            # Use return_all=True to get all businesses, even with websites
            business_info = scraper.extract_business_info(url, return_all=True)
            
            if business_info:
                businesses.append(business_info)
                name = business_info.get('name', 'Unknown')
                website = business_info.get('website', '')
                
                print(f"  ✅ Found: {name}")
                if website:
                    print(f"     ⚠️  HAS WEBSITE: {website}")
                else:
                    print(f"     ✅ NO WEBSITE")
                print(f"     Address: {business_info.get('address', 'N/A')}")
                print(f"     Phone: {business_info.get('phone', 'N/A')}")
            else:
                print(f"  ⚠️  Could not extract business info")
                businesses.append({
                    'name': 'FAILED TO EXTRACT',
                    'address': '',
                    'phone': '',
                    'website': '',
                    'rating': '',
                    'reviews_count': '',
                    'google_maps_url': url,
                    'error': 'Could not extract business information'
                })
        
        print(f"\n\n{'='*60}")
        print(f"RESULTS: Found {len(businesses)} businesses")
        print(f"{'='*60}\n")
        
        # Filter businesses without websites
        businesses_without_websites = [b for b in businesses if not b.get('website') or b.get('website') == '']
        businesses_with_websites = [b for b in businesses if b.get('website') and b.get('website') != '']
        
        print(f"✅ Businesses WITHOUT websites: {len(businesses_without_websites)}")
        for biz in businesses_without_websites:
            print(f"   - {biz.get('name', 'Unknown')}")
        
        print(f"\n⚠️  Businesses WITH websites: {len(businesses_with_websites)}")
        for biz in businesses_with_websites:
            print(f"   - {biz.get('name', 'Unknown')}: {biz.get('website', '')}")
        
        # Export ALL businesses to Excel for review
        exporter = DataExporter()
        exporter.create_dataframe(businesses)
        excel_file = exporter.export_to_excel("debug_bali_garages.xlsx")
        print(f"\n✅ All businesses exported to: {excel_file}")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()
        print("\nDone!")


if __name__ == "__main__":
    main()
