# Website Market - Business Lead Generator

A tool to find businesses without websites and automatically reach out to them via email.

## Features

- 🔍 **Google Places API Integration** - Official, reliable, and accurate business data
- 📊 **Automatic Usage Tracking** - Monitor your API credits and costs in real-time
- 🎯 Filter businesses that don't have websites listed
- 📈 Export data to Excel/CSV
- 📧 Automated email sending with personalization

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials:
```
# Google Places API Key (REQUIRED)
GOOGLE_PLACES_API_KEY=your_api_key_here

# Email credentials (for email automation)
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Google Places API Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing
3. Enable "Places API (New)"
4. Create API Key (Credentials > Create Credentials > API Key)
5. Add API restriction: "Restriction d'API" → Select "Places API (New)"
6. Add the key to your `.env` file

**Note:** For Gmail, you'll need to generate an "App Password" in your Google Account settings.

## Usage

Run the main script:
```bash
python main.py
```

The script will:
1. Show your current API usage statistics
2. Ask you for a city (e.g., "Boston")
3. Ask you for a business type (e.g., "garage")
4. Search businesses using Google Places API (official, reliable)
5. Filter businesses without websites
6. Export results to `businesses_without_websites.xlsx`
7. Show final API usage statistics
8. Optionally send automated emails

## Email Automation

### Step 1: Customize Email Template
Edit `email_template.txt` to customize your email message. Use placeholders:
- `{business_name}` - Business name
- `{address}` - Business address
- `{phone}` - Phone number

### Step 2: Add Email Addresses
After scraping, open the generated Excel file and add an `email` column with email addresses for each business.

### Step 3: Configure Email Settings
Create a `.env` file (copy from `.env.example`) with your email credentials:
```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**For Gmail:**
1. Enable 2-Step Verification in your Google Account
2. Go to: Google Account > Security > 2-Step Verification > App passwords
3. Generate an app password and use it as `EMAIL_PASSWORD`

### Step 4: Send Emails
Option A: Use the main script (will prompt you)
```bash
python main.py
```

Option B: Use the standalone email script
```bash
python send_emails.py businesses_without_websites.xlsx
```

## Workflow Example

1. **Scrape businesses:**
   ```bash
   python main.py
   # Enter: Boston
   # Enter: garage
   # Enter: 50 (or press Enter for default)
   ```

2. **Review the Excel file** (`businesses_without_websites_YYYYMMDD_HHMMSS.xlsx`)

3. **Add email addresses** manually to the Excel file (add `email` column)

4. **Customize email template** in `email_template.txt`

5. **Send emails:**
   ```bash
   python send_emails.py businesses_without_websites_YYYYMMDD_HHMMSS.xlsx
   ```

## Check API Usage

Run anytime to see your current API usage:
```bash
python check_usage.py
```

## Notes

- Uses official Google Places API - reliable and legal
- Automatically tracks API usage and costs
- Shows remaining free credits ($200/month free tier)
- Email sending includes a 5-second delay between emails by default
- Rate limiting handled automatically (1 second delay between requests)

## 💰 Costs & Limitations

**API Pricing:**
- **$200 free credit/month** from Google Cloud Platform
- **$32 per 1,000 requests** (Text Search API)
- **First ~6,250 businesses/month = FREE**

**Examples:**
- 1,000 businesses = $32/month → **FREE** (covered by credit)
- 5,000 businesses = $160/month → **FREE** (covered by credit)
- 10,000 businesses = $320/month → $120/month (after credit)

**Email:**
- Gmail SMTP free (500 emails/day limit)

**See `COSTS_AND_LIMITATIONS.md` for detailed pricing and alternatives.**

