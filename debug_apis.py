"""Debug API endpoints"""
import requests

BASE = 'http://localhost:8003'

# Login
login = requests.post(f'{BASE}/api/auth/login', json={'email':'testuser999@example.com','password':'password123'})
token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print('=== TESTING API ENDPOINTS ===')

# Test Portfolio
r = requests.get(f'{BASE}/api/investments', headers=headers)
print(f'\n1. Portfolio: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'   Investments count: {len(data)}')
    if data:
        first = data[0]
        print(f'   First: {first.get("symbol")} - {first.get("quantity")} shares')

# Test Analytics
r = requests.get(f'{BASE}/api/analytics/portfolio/performance?timeframe=1M', headers=headers)
print(f'\n2. Analytics Performance: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'   Has data: {data.get("success")}')

# Test Charts
r = requests.get(f'{BASE}/api/charts/asset-allocation', headers=headers)
print(f'\n3. Charts Asset Allocation: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'   Response keys: {list(data.keys())}')
    if 'data' in data:
        print(f'   Data: {data["data"]}')

# Test Recommendations
r = requests.get(f'{BASE}/api/recommendations/portfolio', headers=headers)
print(f'\n4. Recommendations: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    print(f'   Success: {data.get("success")}')
    if data.get('data'):
        recs = data['data'].get('recommendations', [])
        print(f'   Recommendations: {len(recs)}')
