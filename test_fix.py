"""
Test the URL fix for xosodaiphat provider.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modules.result.providers.xosodaiphat_provider import XosodaiphatProvider

def test_build_url():
    print("Testing URL building...")
    
    # Test MT URLs (should fallback to main page if weekday URLs fail)
    test_cases = [
        ("MT", "2026-04-06"),  # Sunday
        ("MT", "2026-04-07"),  # Monday
        ("MN", "2026-04-06"),
        ("MB", "2026-04-06"),
    ]
    
    for region, date in test_cases:
        try:
            url = XosodaiphatProvider.build_url(region, date)
            print(f"  {region} {date}: {url}")
        except Exception as e:
            print(f"  {region} {date}: ERROR - {e}")

def test_fetch():
    print("\nTesting fetch (this will make actual HTTP requests)...")
    
    # Only test one to avoid too many requests
    try:
        result = XosodaiphatProvider.fetch_raw_html("MN", "2026-04-06")
        print(f"  MN fetch: SUCCESS, got {len(result['html'])} chars")
        print(f"  Source URL: {result['source_url']}")
    except Exception as e:
        print(f"  MN fetch: ERROR - {e}")

if __name__ == "__main__":
    test_build_url()
    test_fetch()