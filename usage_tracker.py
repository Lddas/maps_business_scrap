"""
Usage Tracker for Google Places API
Tracks API requests and calculates remaining credits
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class UsageTracker:
    def __init__(self, usage_file=".api_usage.json"):
        self.usage_file = Path(usage_file)
        self.monthly_credit = 200.00  # $200 free credit per month
        self.cost_per_request = 0.032  # $32 per 1000 requests = $0.032 per request
        
        # Load existing usage data
        self.usage_data = self._load_usage()
        self._reset_if_new_month()
    
    def _load_usage(self):
        """Load usage data from file"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Initialize new usage data
        return {
            'month': datetime.now().strftime('%Y-%m'),
            'requests': 0,
            'requests_history': []
        }
    
    def _reset_if_new_month(self):
        """Reset usage if it's a new month"""
        current_month = datetime.now().strftime('%Y-%m')
        if self.usage_data.get('month') != current_month:
            self.usage_data = {
                'month': current_month,
                'requests': 0,
                'requests_history': []
            }
            self._save_usage()
    
    def _save_usage(self):
        """Save usage data to file"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage_data, f, indent=2)
    
    def track_request(self, success=True):
        """Track an API request"""
        self.usage_data['requests'] += 1
        self.usage_data['requests_history'].append({
            'timestamp': datetime.now().isoformat(),
            'success': success
        })
        self._save_usage()
    
    def get_stats(self):
        """Get current usage statistics"""
        requests = self.usage_data['requests']
        cost = requests * self.cost_per_request
        remaining_credit = max(0, self.monthly_credit - cost)
        after_credit_cost = max(0, cost - self.monthly_credit)
        
        return {
            'month': self.usage_data['month'],
            'requests': requests,
            'cost': cost,
            'remaining_credit': remaining_credit,
            'after_credit_cost': after_credit_cost,
            'is_free': cost <= self.monthly_credit
        }
    
    def print_stats(self):
        """Print formatted usage statistics"""
        stats = self.get_stats()
        
        print("\n" + "=" * 70)
        print("📊 API Usage Statistics")
        print("=" * 70)
        print(f"Month: {stats['month']}")
        print(f"Total Requests: {stats['requests']:,}")
        print(f"Cost: ${stats['cost']:.2f}")
        
        if stats['is_free']:
            print(f"✅ Remaining Free Credit: ${stats['remaining_credit']:.2f}")
            print(f"   (You're still within the $200/month free tier!)")
        else:
            print(f"⚠️  Cost after $200 credit: ${stats['after_credit_cost']:.2f}")
            print(f"   (You've used up your free credit for this month)")
        
        # Calculate how many more requests are free
        if stats['is_free']:
            remaining_free_requests = int(stats['remaining_credit'] / self.cost_per_request)
            print(f"\n💡 You can make ~{remaining_free_requests:,} more requests this month for FREE")
        else:
            print(f"\n⚠️  Each additional request costs ${self.cost_per_request:.4f}")
        
        print("=" * 70 + "\n")
    
    def get_remaining_free_requests(self):
        """Get how many more requests are free this month"""
        stats = self.get_stats()
        if stats['is_free']:
            return int(stats['remaining_credit'] / self.cost_per_request)
        return 0

