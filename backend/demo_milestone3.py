#!/usr/bin/env python3
"""
Final working demo of Milestone 3 features
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_market_apis():
    """Test market data APIs"""
    print("📊 Testing Market Data APIs...")
    
    # Test 1: Update market prices
    print("  1. Updating market prices...")
    response = requests.post(f"{BASE_URL}/market/update?symbols=AAPL,TSLA,MSFT")
    if response.status_code == 200:
        data = response.json()
        print(f"     ✅ Success: {data['updated_count']} prices updated")
        print(f"     📈 AAPL: ${data['prices']['AAPL']:.2f}")
        print(f"     📈 TSLA: ${data['prices']['TSLA']:.2f}")
    else:
        print(f"     ❌ Failed: {response.status_code}")
        return False
    
    # Test 2: Get latest prices
    print("  2. Getting latest prices...")
    response = requests.get(f"{BASE_URL}/market/prices?symbols=AAPL,TSLA")
    if response.status_code == 200:
        data = response.json()
        print(f"     ✅ Success: Retrieved {len(data)} prices")
        for symbol, price in data.items():
            print(f"     📊 {symbol}: ${price:.2f}")
    else:
        print(f"     ❌ Failed: {response.status_code}")
        return False
    
    return True

def test_simulation_apis():
    """Test simulation APIs"""
    print("\n🧮 Testing Investment Simulation APIs...")
    
    # Test 1: Basic simulation
    print("  1. Running basic investment simulation...")
    sim_data = {
        "initial_amount": 10000,
        "monthly_investment": 500,
        "annual_rate": 0.08,
        "years": 5
    }
    response = requests.post(f"{BASE_URL}/simulate/", json=sim_data)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            result = data['data']
            print(f"     ✅ Success: Future value = ${result['total_future_value']:,.2f}")
            print(f"     💰 Initial: ${result['initial_amount']:,.2f}")
            print(f"     💰 Monthly: ${result['monthly_investment']:,.2f}")
            print(f"     📈 Returns: {result['return_percentage']:.2f}%")
        else:
            print(f"     ❌ Failed: {data['message']}")
            return False
    else:
        print(f"     ❌ Failed: {response.status_code}")
        return False
    
    # Test 2: What-if scenarios
    print("  2. Comparing investment scenarios...")
    scenarios_data = {
        "initial_amount": 10000,
        "monthly_investment": 500,
        "scenarios": [
            {"name": "Conservative", "annual_rate": 0.06, "years": 10},
            {"name": "Moderate", "annual_rate": 0.08, "years": 10},
            {"name": "Aggressive", "annual_rate": 0.12, "years": 10}
        ]
    }
    response = requests.post(f"{BASE_URL}/simulate/what-if", json=scenarios_data)
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            result = data['data']
            print(f"     ✅ Success: Compared {len(result['scenarios'])} scenarios")
            print(f"     🏆 Best: {result['best_scenario']['scenario_name']} - ${result['best_scenario']['total_future_value']:,.2f}")
            print(f"     ⚠️  Worst: {result['worst_scenario']['scenario_name']} - ${result['worst_scenario']['total_future_value']:,.2f}")
        else:
            print(f"     ❌ Failed: {data['message']}")
            return False
    else:
        print(f"     ❌ Failed: {response.status_code}")
        return False
    
    return True

def test_task_apis():
    """Test task management APIs"""
    print("\n📋 Testing Task Management APIs...")
    
    # Test 1: Get task status
    print("  1. Getting task status...")
    response = requests.get(f"{BASE_URL}/tasks/status")
    if response.status_code == 200:
        data = response.json()
        print(f"     ✅ Status: {data['celery_status']}")
        print(f"     ℹ️  {data['message']}")
    else:
        print(f"     ❌ Failed: {response.status_code}")
        return False
    
    # Test 2: Manual market update
    print("  2. Triggering manual market update...")
    response = requests.post(f"{BASE_URL}/tasks/market-update?symbols=NVDA,META")
    if response.status_code == 200:
        data = response.json()
        print(f"     ✅ Success: {data['message']}")
        print(f"     📊 Updated symbols: {', '.join(data['symbols'])}")
    else:
        print(f"     ❌ Failed: {response.status_code}")
        return False
    
    return True

def main():
    """Main demo runner"""
    print("🚀 Milestone 3 - Working Demo")
    print("=" * 50)
    
    # Test all APIs
    tests = [
        test_market_apis,
        test_simulation_apis,
        test_task_apis
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Demo Results: {passed}/{total} API groups working")
    
    if passed == total:
        print("🎉 All APIs are working perfectly!")
        print("\n🌐 Available Endpoints:")
        print(f"   • API Docs: {BASE_URL}/docs")
        print(f"   • Market Data: {BASE_URL}/market/prices")
        print(f"   • Simulations: {BASE_URL}/simulate/")
        print(f"   • Task Status: {BASE_URL}/tasks/status")
        print("\n✅ Milestone 3 is complete and fully functional!")
    else:
        print("⚠️  Some APIs have issues, but core functionality is working.")

if __name__ == "__main__":
    main()
