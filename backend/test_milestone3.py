#!/usr/bin/env python3
"""
Quick test script for Milestone 3 features
"""
import asyncio
import sys
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_api_connection():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        return response.status_code == 200
    except:
        return False

def test_market_apis():
    """Test market data APIs"""
    print("📊 Testing Market APIs...")
    
    # Test 1: Update market prices
    try:
        response = requests.post(f"{BASE_URL}/market/update?symbols=AAPL,MSFT")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Market update successful: {data['updated_count']} prices updated")
        else:
            print(f"❌ Market update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market update error: {e}")
        return False
    
    # Test 2: Get latest prices
    try:
        response = requests.get(f"{BASE_URL}/market/prices?symbols=AAPL,MSFT")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get prices successful: {len(data)} prices returned")
        else:
            print(f"❌ Get prices failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get prices error: {e}")
        return False
    
    # Test 3: Get available symbols
    try:
        response = requests.get(f"{BASE_URL}/market/symbols")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get symbols successful: {len(data['symbols'])} symbols available")
        else:
            print(f"❌ Get symbols failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get symbols error: {e}")
        return False
    
    return True

def test_simulation_apis():
    """Test simulation APIs"""
    print("\n🧮 Testing Simulation APIs...")
    
    # Test 1: Basic simulation
    try:
        simulation_data = {
            "initial_amount": 100000,
            "monthly_investment": 5000,
            "annual_rate": 0.08,
            "years": 10
        }
        response = requests.post(f"{BASE_URL}/simulate/", json=simulation_data)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                result = data['data']
                print(f"✅ Basic simulation successful: Future value = ${result['total_future_value']:,.2f}")
            else:
                print(f"❌ Basic simulation failed: {data['message']}")
                return False
        else:
            print(f"❌ Basic simulation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Basic simulation error: {e}")
        return False
    
    # Test 2: What-if scenarios
    try:
        scenarios_data = {
            "initial_amount": 100000,
            "monthly_investment": 5000,
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
                print(f"✅ What-if scenarios successful: {len(result['scenarios'])} scenarios compared")
                if result['best_scenario']:
                    print(f"   Best scenario: {result['best_scenario']['scenario_name']}")
            else:
                print(f"❌ What-if scenarios failed: {data['message']}")
                return False
        else:
            print(f"❌ What-if scenarios failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ What-if scenarios error: {e}")
        return False
    
    # Test 3: Goal projection
    try:
        goal_data = {
            "target_amount": 1000000,
            "current_amount": 100000,
            "monthly_contribution": 10000,
            "annual_rate": 0.08
        }
        response = requests.post(f"{BASE_URL}/simulate/goal-projection", json=goal_data)
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                result = data['data']
                if result['achievable']:
                    print(f"✅ Goal projection successful: Achievable in {result['years_needed']} years")
                else:
                    print(f"✅ Goal projection successful: Not achievable with current parameters")
            else:
                print(f"❌ Goal projection failed: {data['message']}")
                return False
        else:
            print(f"❌ Goal projection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Goal projection error: {e}")
        return False
    
    return True

def test_task_apis():
    """Test task management APIs"""
    print("\n📋 Testing Task APIs...")
    
    # Test 1: Get Celery status
    try:
        response = requests.get(f"{BASE_URL}/tasks/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Celery status: {data['celery_status']}")
        else:
            print(f"❌ Celery status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Celery status error: {e}")
        return False
    
    # Test 2: Trigger market update task
    try:
        response = requests.post(f"{BASE_URL}/tasks/market-update?symbols=TSLA")
        if response.status_code == 200:
            data = response.json()
            task_id = data['task_id']
            print(f"✅ Market update task triggered: {task_id}")
            
            # Wait a bit and check result
            time.sleep(3)
            result_response = requests.get(f"{BASE_URL}/tasks/{task_id}")
            if result_response.status_code == 200:
                result_data = result_response.json()
                print(f"✅ Task status: {result_data['status']}")
            else:
                print(f"❌ Task result check failed: {result_response.status_code}")
        else:
            print(f"❌ Market update task failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Market update task error: {e}")
        return False
    
    return True

def main():
    """Main test runner"""
    print("🚀 Milestone 3 Test Suite")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test API connection
    if not test_api_connection():
        print("❌ API server is not running. Please start the FastAPI server first.")
        print("   Run: python main.py")
        sys.exit(1)
    
    print("✅ API server is running")
    
    # Run all tests
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
        print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} test groups passed")
    
    if passed == total:
        print("🎉 All tests passed! Milestone 3 is working correctly.")
        print("\n🌐 Available endpoints:")
        print(f"   • API Docs: {BASE_URL}/docs")
        print(f"   • Market APIs: {BASE_URL}/market/prices")
        print(f"   • Simulation APIs: {BASE_URL}/simulate/")
        print(f"   • Task Status: {BASE_URL}/tasks/status")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
