"""Test Charts and Analytics data"""
import requests

BASE = 'http://localhost:8003'

# Login
login = requests.post(f'{BASE}/api/auth/login', 
                     json={'email':'testuser999@example.com','password':'password123'})
token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test Portfolio
r = requests.get(f'{BASE}/api/investments', headers=headers)
print(f'Portfolio: {r.status_code} - {len(r.json())} investments')

# Test Charts - Asset Allocation
r = requests.get(f'{BASE}/api/charts/asset-allocation', headers=headers)
print(f'Asset Allocation: {r.status_code}')
if r.status_code == 200:
    print('  Response:', r.json())

# Test Analytics
r = requests.get(f'{BASE}/api/analytics/portfolio-summary', headers=headers)
print(f'Analytics Summary: {r.status_code}')
if r.status_code == 200:
    print('  Response:', r.json())

# Test Recommendations
r = requests.get(f'{BASE}/api/recommendations/portfolio', headers=headers)
print(f'Recommendations: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'  Total recommendations: {len(data)}')
