"""
Calculate costs for Google Places API usage
"""
def calculate_api_costs(num_businesses):
    """
    Calculate the cost of checking websites for businesses using Google Places API
    
    Pricing: $32 per 1,000 requests (Text Search API)
    Monthly credit: $200 free
    
    Returns: (monthly_cost, after_credit_cost, requests_per_month)
    """
    cost_per_1000 = 32.00
    monthly_credit = 200.00
    
    # Each business check = 1 API request
    requests = num_businesses
    
    # Calculate cost
    monthly_cost = (requests / 1000) * cost_per_1000
    after_credit = max(0, monthly_cost - monthly_credit)
    
    return monthly_cost, after_credit, requests


def print_cost_table():
    """Print a cost table for different volumes"""
    print("=" * 70)
    print("Google Places API Cost Calculator")
    print("=" * 70)
    print("\nPricing: $32 per 1,000 requests (Text Search API)")
    print("Monthly Credit: $200 FREE from Google Cloud Platform")
    print("\n" + "-" * 70)
    print(f"{'Businesses/Month':<20} {'Cost (before credit)':<25} {'Cost (after $200 credit)':<25}")
    print("-" * 70)
    
    test_amounts = [100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
    
    for num in test_amounts:
        cost, after_credit, _ = calculate_api_costs(num)
        cost_str = f"${cost:.2f}"
        after_str = f"${after_credit:.2f}" if after_credit > 0 else "FREE ($200 credit covers it)"
        print(f"{num:<20} {cost_str:<25} {after_str:<25}")
    
    print("\n" + "=" * 70)
    print("\n💡 Tips to reduce costs:")
    print("  1. Use the $200 free credit effectively (covers ~6,250 checks/month)")
    print("  2. Add delays between requests to avoid rate limits")
    print("  3. Only check businesses you're actually going to contact")
    print("  4. Cache results (don't re-check the same business)")
    print("  5. Set up billing alerts in Google Cloud Console")
    print("\n📊 Cost per business: $0.032 (3.2 cents)")
    print("   With $200 credit: FREE for first ~6,250 businesses/month")


if __name__ == "__main__":
    print_cost_table()
    
    print("\n" + "=" * 70)
    print("\nEnter number of businesses to calculate cost:")
    try:
        num = int(input("> "))
        cost, after_credit, requests = calculate_api_costs(num)
        print(f"\n📊 Results for {num:,} businesses:")
        print(f"   • API Requests: {requests:,}")
        print(f"   • Monthly Cost: ${cost:.2f}")
        print(f"   • After $200 Credit: ${after_credit:.2f}" if after_credit > 0 else f"   • After $200 Credit: FREE (credit covers ${cost:.2f})")
        print(f"   • Cost per business: ${cost/num:.4f}")
    except ValueError:
        print("Invalid input. Please enter a number.")

