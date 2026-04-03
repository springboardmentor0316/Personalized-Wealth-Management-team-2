"""Test Recommendations API"""
import requests

BASE = 'http://localhost:8003'

login = requests.post(f'{BASE}/api/auth/login', json={'email':'testuser999@example.com','password':'password123'})
token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test Recommendations
r = requests.get(f'{BASE}/api/recommendations/portfolio', headers=headers)
print(f'Recommendations: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    if data.get('success'):
        recs = data['data'].get('recommendations', [])
        print(f'Total Recommendations: {len(recs)}')
        for rec in recs:
            print(f"  - {rec.get('title')}: {rec.get('description')[:70]}...")
    else:
        print(f"Error: {data}")
else:
    print(f"Error: {r.text[:200]}")
