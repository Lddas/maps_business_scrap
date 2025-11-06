#!/usr/bin/env python3
"""
Quick script to check your Google Places API usage
Run this anytime: python check_usage.py
"""
from usage_tracker import UsageTracker

if __name__ == "__main__":
    tracker = UsageTracker()
    tracker.print_stats()

