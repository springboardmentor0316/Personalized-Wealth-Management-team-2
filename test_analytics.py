"""Test Analytics API"""
import requests

BASE = 'http://localhost:8003'

login = requests.post(f'{BASE}/api/auth/login', json={'email':'testuser999@example.com','password':'password123'})
token = login.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test Analytics Performance
r = requests.get(f'{BASE}/api/analytics/portfolio/performance?timeframe=1M', headers=headers)
print(f'Analytics Performance: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    if data.get('success'):
        metrics = data.get('data', {}).get('metrics', {})
        print(f"  Total Return: {metrics.get('total_return', 0)*100:.2f}%")
        print(f"  Annualized Return: {metrics.get('annualized_return', 0)*100:.2f}%")
        print(f"  Volatility: {metrics.get('volatility', 0)*100:.2f}%")
        print(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"  Current Value: {metrics.get('current_value', 0)}")
        print(f"  Cost Basis: {metrics.get('cost_basis', 0)}")
    else:
        print(f"  Error: {data}")
else:
    print(f"  Error: {r.text[:200]}")
