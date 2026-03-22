#!/usr/bin/env python3
"""Test OpenGrok connection."""
import sys
import httpx

def test_connection(base_url: str, token: str = None):
    """Test OpenGrok API connection."""
    print(f"Testing: {base_url}")
    
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print(f"Using token: {token[:10]}...")
    
    # Test different endpoints
    endpoints = [
        "/api/v1/projects",
        "/source/api/v1/projects",
        "/api/v1/search?def=test&maxresults=1",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url.rstrip('/')}{endpoint}"
        try:
            resp = httpx.get(url, headers=headers, timeout=5.0)
            print(f"✓ {endpoint}: {resp.status_code}")
            if resp.status_code == 200:
                print(f"  Response: {resp.text[:200]}")
        except Exception as e:
            print(f"✗ {endpoint}: {e}")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    token = sys.argv[2] if len(sys.argv) > 2 else None
    test_connection(base_url, token)
