"""
Main script - Orchestrates the entire process
Uses Google Places API for reliable business data collection
"""
import sys
import re
from datetime import datetime
from api_scraper import GooglePlacesAPIScraper
from exporter import DataExporter


def main():
    print("=" * 60)
    print("Website Market - Business Lead Generator")
    print("=" * 60)
    print()
    
    # Step 1: Get city
    city = input("Enter the city name (e.g., Boston): ").strip()
    if not city:
        print("City is required!")
        sys.exit(1)
    
    # Step 2: Get business type
    business_type = input("Enter the business type (e.g., garage): ").strip()
    if not business_type:
        print("Business type is required!")
        sys.exit(1)
 
    # Step 3: Get search radius (km)
    radius_input = input("Search radius in km (default: 10): ").strip()
    try:
        radius_km = float(radius_input) if radius_input else 10.0
        if radius_km <= 0:
            radius_km = 10.0
    except ValueError:
        radius_km = 10.0

    # Step 4: Get max results
    max_results_input = input("How many businesses to fetch? (default: 50): ").strip()
    try:
        max_results = int(max_results_input) if max_results_input else 50
    except ValueError:
        max_results = 50
 
    print(f"\n🚀 Starting API search for {business_type} in {city}...")
    print("📊 Using Google Places API (official and reliable)\n")
 
    # Step 4: Search businesses using API
    scraper = GooglePlacesAPIScraper()
    try:
        businesses = scraper.search_businesses(city, business_type, max_results, radius_km)
        
        # Format businesses for export with requested columns
        formatted_businesses = scraper.format_businesses_for_export()
        
        # Count businesses with/without websites
        with_website = sum(1 for biz in formatted_businesses if biz.get('has_website') == 'Yes')
        without_website = sum(1 for biz in formatted_businesses if biz.get('has_website') == 'No')
        
        print(f"\n{'='*70}")
        print(f"📊 Results Summary:")
        print(f"   • Total businesses found: {len(formatted_businesses)}")
        print(f"   • Businesses WITH websites: {with_website}")
        print(f"   • Businesses WITHOUT websites: {without_website}")
        print(f"{'='*70}\n")
        
        if not formatted_businesses:
            print("⚠️  No businesses found!")
            scraper.print_usage_stats()
            return
        
        # Step 5: Export to Excel
        exporter = DataExporter()
        exporter.create_dataframe(formatted_businesses)

        business_slug = re.sub(r'[^a-zA-Z0-9]+', '_', business_type.strip().lower()).strip('_') or 'business'
        city_slug = re.sub(r'[^a-zA-Z0-9]+', '_', city.strip().lower()).strip('_') or 'city'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads_{business_slug}_{city_slug}_{timestamp}.xlsx"

        excel_file = exporter.export_to_excel(filename)
        
        print(f"\n✅ Success! Data saved to: {excel_file}")
        print(f"\n📋 Excel columns:")
        print(f"   • name - Business name")
        print(f"   • business_type - '{business_type}' (what you searched)")
        print(f"   • phone - Phone number")
        print(f"   • website - Website URL (blank if none)")
        print(f"   • has_website - Yes/No")
        print(f"   • contacted - No (default, change to Yes when you contact them)")
        print(f"   • response - Empty (fill manually with their response)")
        
        # Show API usage stats
        scraper.print_usage_stats()
        
        print("\n📋 Next steps:")
        print("1. Review the Excel file")
        print("2. Contact businesses and mark 'contacted' as Yes")
        print("3. Fill in 'response' column with their answers")
        print("4. Filter by 'has_website' = No to focus on businesses without websites")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        scraper.print_usage_stats()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        scraper.print_usage_stats()
    finally:
        print("\n✅ Done!")


if __name__ == "__main__":
    main()

