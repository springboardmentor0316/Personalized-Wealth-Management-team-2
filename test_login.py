#!/usr/bin/env python3
import requests
import json

test_data = {
    "email": "testuser999@example.com",
    "password": "password123"
}

try:
    print("Testing login...")
    print(f"Request data: {json.dumps(test_data, indent=2)}")
    
    response = requests.post(
        "http://localhost:8001/api/auth/login",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
