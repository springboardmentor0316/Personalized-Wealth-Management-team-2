#!/usr/bin/env python3

import requests
import json

def test_login():
    """Test the login endpoint"""
    url = "http://localhost:8001/api/auth/login"
    
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(url, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"🔑 Access Token: {data['access_token'][:50]}...")
            print(f"👤 User: {data['user']['full_name']} ({data['user']['email']})")
            return data['access_token']
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_analytics_endpoint(token):
    """Test an analytics endpoint with authentication"""
    url = "http://localhost:8001/api/analytics/portfolio/performance?timeframe=1M"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics endpoint working!")
            print(f"📊 Data keys: {list(data.keys())}")
        else:
            print(f"❌ Analytics endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Testing authentication and API endpoints...")
    print()
    
    # Test login
    token = test_login()
    
    if token:
        print()
        # Test analytics endpoint
        test_analytics_endpoint(token)
    
    print()
    print("🎉 Test completed!")
