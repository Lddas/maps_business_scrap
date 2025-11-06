# Email Finding Guide

## The Challenge

**Google Places API doesn't provide email addresses**, and we're specifically looking for businesses **WITHOUT websites**. This creates a challenge because:

1. ❌ No email in Google Places API data
2. ❌ No website to scrape for contact info
3. ❌ Limited automated options

## Solutions

### Option 1: Manual Entry (Recommended for small lists)
**Best for:** < 50 businesses
- Open the Excel file
- Research each business manually
- Add emails one by one
- Most reliable but time-consuming

### Option 2: Email Finding Services

#### Hunter.io (Recommended)
- **Free tier:** 25 searches/month
- **Paid:** $49/month for 1,000 searches
- **How it works:** Searches websites and databases for email addresses
- **Limitation:** Still needs domain/website to search

**Setup:**
1. Sign up at https://hunter.io
2. Get API key
3. Add to `.env`: `HUNTER_API_KEY=your_key`

#### Clearbit
- **Free tier:** Limited
- **Paid:** $99/month+
- **Good for:** Finding emails by company name + location

#### RocketReach
- **Free tier:** 10 searches/month
- **Paid:** $39/month for 1,000 searches
- **Good for:** LinkedIn-based email finding

### Option 3: Alternative Data Sources

#### LinkedIn
- Search for business pages
- Look for contact information
- Find employees and their emails
- Manual but often effective

#### Phone Number Lookup
- Some businesses list phone numbers
- Use reverse phone lookup services
- May find associated email addresses

#### Social Media
- Check Facebook, Instagram, Twitter
- Businesses sometimes list contact emails
- Manual search required

### Option 4: Hybrid Approach

**For businesses WITH websites (if you want those too):**
1. Don't filter out businesses with websites initially
2. Use Hunter.io to find emails from their websites
3. Then filter by your criteria

**For businesses WITHOUT websites:**
1. Use LinkedIn to find contacts
2. Use Clearbit/RocketReach name+location search
3. Call businesses directly
4. Manual entry

## Workflow Recommendations

### Small Scale (< 50 businesses)
1. Export to Excel
2. Manual research and entry
3. Most reliable method

### Medium Scale (50-500 businesses)
1. Use Hunter.io API (if businesses have websites)
2. Use LinkedIn Sales Navigator
3. Manual entry for remaining

### Large Scale (500+ businesses)
1. Use paid email finding services
2. Consider outsourcing to virtual assistants
3. Use automation tools (Hunter.io, Clearbit, etc.)

## Current Implementation

The `email_finder.py` module includes:
- ✅ Hunter.io integration (if API key provided)
- ✅ Domain-based email search
- ✅ Batch processing

**To use Hunter.io:**
1. Sign up at https://hunter.io
2. Get your API key
3. Add to `.env`: `HUNTER_API_KEY=your_key_here`
4. Run the script - it will automatically use Hunter.io

## Best Practices

1. **Verify emails** before sending (use email verification services)
2. **Respect privacy** - follow GDPR, CAN-SPAM laws
3. **Personalize emails** - don't send generic bulk emails
4. **Track results** - see which emails actually work
5. **Update regularly** - email addresses change

## Legal Considerations

- ⚠️ **GDPR** (Europe): Requires consent for marketing emails
- ⚠️ **CAN-SPAM** (USA): Requires opt-out option
- ⚠️ **Check local laws** before bulk emailing
- ⚠️ **Use opt-in lists** when possible

## Cost Comparison

| Service | Free Tier | Paid Tier | Best For |
|---------|-----------|-----------|----------|
| Hunter.io | 25/month | $49/month (1K) | Domain-based search |
| Clearbit | Limited | $99/month+ | Company name search |
| RocketReach | 10/month | $39/month (1K) | LinkedIn-based |
| Manual | Unlimited | Your time | Small lists |

## Next Steps

1. **For now:** Manual entry is most reliable
2. **For automation:** Sign up for Hunter.io (free tier to start)
3. **For large scale:** Consider paid services or outsourcing

The current script will ask if you want to try finding emails. If you have Hunter.io set up, it will attempt to find emails. Otherwise, it will guide you to manual entry or other services.

