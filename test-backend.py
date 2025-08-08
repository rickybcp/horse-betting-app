#!/usr/bin/env python3
"""
Simple test script to verify backend API endpoints
Run this after starting the backend server
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"✓ {method} {endpoint}: {response.status_code}")
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    print(f"  Data: {len(result)} items")
                elif isinstance(result, dict):
                    print(f"  Data: {len(result)} keys")
                else:
                    print(f"  Data: {result}")
            except:
                print(f"  Response: {response.text[:100]}...")
        else:
            print(f"  Error: {response.text}")
        
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print(f"✗ {method} {endpoint}: Connection failed (server not running?)")
        return False
    except requests.exceptions.Timeout:
        print(f"✗ {method} {endpoint}: Timeout")
        return False
    except Exception as e:
        print(f"✗ {method} {endpoint}: {str(e)}")
        return False

def main():
    print("Testing Horse Betting Backend API")
    print("=" * 40)
    print()
    
    # Test basic endpoints
    endpoints = [
        ("/users", "GET"),
        ("/races", "GET"),
        ("/bets", "GET"),
        ("/bankers", "GET"),
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint, method in endpoints:
        if test_endpoint(endpoint, method):
            success_count += 1
        print()
    
    # Test adding a user
    print("Testing POST endpoints...")
    user_data = {"name": "Test User"}
    if test_endpoint("/users", "POST", user_data):
        success_count += 1
        total_count += 1
    
    print()
    print("=" * 40)
    print(f"Test Results: {success_count}/{total_count} endpoints working")
    
    if success_count == total_count:
        print("🎉 All tests passed! Backend is ready.")
    else:
        print("⚠️  Some tests failed. Check backend logs.")
    
    print()
    print("Frontend should now be able to connect to:")
    print(f"  {BASE_URL}")

if __name__ == "__main__":
    main() 