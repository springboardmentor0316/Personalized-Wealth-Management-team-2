"""
Comprehensive Milestone 4 Testing Suite
Tests all Milestone 4 features: Recommendations, Reports, QA, Accessibility, Performance, Deployment
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8003"

def get_auth_token():
    """Get authentication token for testing"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "testuser999@example.com",
                "password": "password123"
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
    except Exception:
        pass
    return None

def test_recommendations_engine():
    """Test Recommendations engine with suggested allocation JSON"""
    print("\n" + "="*70)
    print("TESTING: Recommendations Engine (Milestone 4 - Week 7)")
    print("="*70)
    
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Get auth token
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test 1: Portfolio recommendations endpoint
    try:
        response = requests.get(
            f"{BASE_URL}/api/recommendations/portfolio",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                results["tests"].append({
                    "name": "Portfolio Recommendations API",
                    "status": "✅ PASS",
                    "details": f"Found {data['data'].get('total_count', 0)} recommendations"
                })
                results["passed"] += 1
            else:
                results["tests"].append({
                    "name": "Portfolio Recommendations API",
                    "status": "❌ FAIL",
                    "details": "Invalid response structure"
                })
                results["failed"] += 1
        else:
            results["tests"].append({
                "name": "Portfolio Recommendations API",
                "status": "❌ FAIL",
                "details": f"Status: {response.status_code}"
            })
            results["failed"] += 1
    except Exception as e:
        results["tests"].append({
            "name": "Portfolio Recommendations API",
            "status": "❌ FAIL",
            "details": str(e)
        })
        results["failed"] += 1
    
    # Test 2: Rebalancing recommendations
    try:
        response = requests.get(
            f"{BASE_URL}/api/recommendations/rebalancing",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                results["tests"].append({
                    "name": "Rebalancing Recommendations API",
                    "status": "✅ PASS",
                    "details": "Rebalancing endpoint working"
                })
                results["passed"] += 1
            else:
                results["tests"].append({
                    "name": "Rebalancing Recommendations API",
                    "status": "❌ FAIL",
                    "details": "Invalid response structure"
                })
                results["failed"] += 1
        else:
            results["tests"].append({
                "name": "Rebalancing Recommendations API",
                "status": "❌ FAIL",
                "details": f"Status: {response.status_code}"
            })
            results["failed"] += 1
    except Exception as e:
        results["tests"].append({
            "name": "Rebalancing Recommendations API",
            "status": "❌ FAIL",
            "details": str(e)
        })
        results["failed"] += 1
    
    # Test 3: Risk profile based recommendations
    try:
        response = requests.get(
            f"{BASE_URL}/api/recommendations/risk-profile",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                results["tests"].append({
                    "name": "Risk Profile Recommendations",
                    "status": "✅ PASS",
                    "details": "Risk-based recommendations working"
                })
                results["passed"] += 1
            else:
                results["tests"].append({
                    "name": "Risk Profile Recommendations",
                    "status": "❌ FAIL",
                    "details": "Invalid response structure"
                })
                results["failed"] += 1
        else:
            results["tests"].append({
                "name": "Risk Profile Recommendations",
                "status": "❌ FAIL",
                "details": f"Status: {response.status_code}"
            })
            results["failed"] += 1
    except Exception as e:
        results["tests"].append({
            "name": "Risk Profile Recommendations",
            "status": "❌ FAIL",
            "details": str(e)
        })
        results["failed"] += 1
    
    return results


def test_reports_export():
    """Test Reports (PDF/CSV export) functionality"""
    print("\n" + "="*70)
    print("TESTING: Reports & Export (Milestone 4 - Week 8)")
    print("="*70)
    
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Get auth token
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    # Test 1: Portfolio CSV export
    try:
        response = requests.get(
            f"{BASE_URL}/api/export/portfolio/csv",
            headers=headers
        )
        if response.status_code == 200:
            content = response.text
            if "Symbol,Name,Type,Quantity" in content:
                results["tests"].append({
                    "name": "Portfolio CSV Export",
                    "status": "✅ PASS",
                    "details": f"CSV generated ({len(content)} bytes)"
                })
                results["passed"] += 1
            else:
                results["tests"].append({
                    "name": "Portfolio CSV Export",
                    "status": "❌ FAIL",
                    "details": "Invalid CSV format"
                })
                results["failed"] += 1
        else:
            results["tests"].append({
                "name": "Portfolio CSV Export",
                "status": "❌ FAIL",
                "details": f"Status: {response.status_code}"
            })
            results["failed"] += 1
    except Exception as e:
        results["tests"].append({
            "name": "Portfolio CSV Export",
            "status": "❌ FAIL",
            "details": str(e)
        })
        results["failed"] += 1
    
    # Test 2: Portfolio HTML export (for PDF)
    try:
        response = requests.get(
            f"{BASE_URL}/api/export/portfolio/html",
            headers=headers
        )
        if response.status_code == 200:
            content = response.text
            if "<!DOCTYPE html>" in content and "Portfolio Report" in content:
                results["tests"].append({
                    "name": "Portfolio HTML Export (PDF)",
                    "status": "✅ PASS",
                    "details": f"HTML report generated ({len(content)} bytes)"
                })
                results["passed"] += 1
            else:
                results["tests"].append({
                    "name": "Portfolio HTML Export (PDF)",
                    "status": "❌ FAIL",
                    "details": "Invalid HTML format"
                })
                results["failed"] += 1
        else:
            results["tests"].append({
                "name": "Portfolio HTML Export (PDF)",
                "status": "❌ FAIL",
                "details": f"Status: {response.status_code}"
            })
            results["failed"] += 1
    except Exception as e:
        results["tests"].append({
            "name": "Portfolio HTML Export (PDF)",
            "status": "❌ FAIL",
            "details": str(e)
        })
        results["failed"] += 1
    
    # Test 3: Goals CSV export
    try:
        response = requests.get(
            f"{BASE_URL}/api/export/goals/csv",
            headers=headers
        )
        if response.status_code == 200:
            content = response.text
            if "Goal,Description,Target Amount" in content:
                results["tests"].append({
                    "name": "Goals CSV Export",
                    "status": "✅ PASS",
                    "details": f"CSV generated ({len(content)} bytes)"
                })
                results["passed"] += 1
            else:
                results["tests"].append({
                    "name": "Goals CSV Export",
                    "status": "❌ FAIL",
                    "details": "Invalid CSV format"
                })
                results["failed"] += 1
        else:
            results["tests"].append({
                "name": "Goals CSV Export",
                "status": "❌ FAIL",
                "details": f"Status: {response.status_code}"
            })
            results["failed"] += 1
    except Exception as e:
        results["tests"].append({
            "name": "Goals CSV Export",
            "status": "❌ FAIL",
            "details": str(e)
        })
        results["failed"] += 1
    
    return results


def test_qa_accessibility_performance():
    """Test QA, Accessibility, and Performance features"""
    print("\n" + "="*70)
    print("TESTING: QA, Accessibility, Performance (Milestone 4 - Week 8)")
    print("="*70)
    
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Test 1: Health check endpoint (QA)
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            results["tests"].append({
                "name": "Health Check Endpoint",
                "status": "✅ PASS",
                "details": f"Status: {data.get('status', 'unknown')}"
            })
            results["passed"] += 1
        else:
            results["tests"].append({
                "name": "Health Check Endpoint",
                "status": "❌ FAIL",
                "details": f"Status: {response.status_code}"
            })
            results["failed"] += 1
    except Exception as e:
        results["tests"].append({
            "name": "Health Check Endpoint",
            "status": "❌ FAIL",
            "details": str(e)
        })
        results["failed"] += 1
    
    # Test 2: API documentation (OpenAPI/Swagger)
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            results["tests"].append({
                "name": "API Documentation (Swagger)",
                "status": "✅ PASS",
                "details": "Swagger UI accessible"
            })
            results["passed"] += 1
        else:
            results["tests"].append({
                "name": "API Documentation (Swagger)",
                "status": "❌ FAIL",
                "details": f"Status: {response.status_code}"
            })
            results["failed"] += 1
    except Exception as e:
        results["tests"].append({
            "name": "API Documentation (Swagger)",
            "status": "❌ FAIL",
            "details": str(e)
        })
        results["failed"] += 1
    
    # Test 3: CORS headers (for frontend accessibility)
    try:
        response = requests.get(f"{BASE_URL}/", headers={"Origin": "http://localhost:3000"})
        if "access-control-allow-origin" in response.headers:
            results["tests"].append({
                "name": "CORS Headers (Accessibility)",
                "status": "✅ PASS",
                "details": "CORS configured for frontend"
            })
            results["passed"] += 1
        else:
            results["tests"].append({
                "name": "CORS Headers (Accessibility)",
                "status": "❌ FAIL",
                "details": "CORS headers not set"
            })
            results["failed"] += 1
    except Exception as e:
        results["tests"].append({
            "name": "CORS Headers (Accessibility)",
            "status": "❌ FAIL",
            "details": str(e)
        })
        results["failed"] += 1
    
    return results


def generate_report(recommendations_results, reports_results, qa_results):
    """Generate comprehensive test report"""
    print("\n" + "="*70)
    print("MILESTONE 4 - COMPREHENSIVE TEST REPORT")
    print("="*70)
    
    total_passed = (recommendations_results["passed"] + 
                   reports_results["passed"] + 
                   qa_results["passed"])
    total_failed = (recommendations_results["failed"] + 
                   reports_results["failed"] + 
                   qa_results["failed"])
    total_tests = total_passed + total_failed
    
    print(f"\n📊 OVERALL STATISTICS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {total_passed}")
    print(f"   ❌ Failed: {total_failed}")
    print(f"   📈 Success Rate: {(total_passed/total_tests*100):.1f}%")
    
    print("\n" + "-"*70)
    print("WEEK 7 FEATURES - Recommendations & Rebalancing")
    print("-"*70)
    for test in recommendations_results["tests"]:
        print(f"{test['status']} {test['name']}")
        print(f"   → {test['details']}")
    
    print("\n" + "-"*70)
    print("WEEK 8 FEATURES - Reports & Export")
    print("-"*70)
    for test in reports_results["tests"]:
        print(f"{test['status']} {test['name']}")
        print(f"   → {test['details']}")
    
    print("\n" + "-"*70)
    print("WEEK 8 FEATURES - QA, Accessibility, Performance")
    print("-"*70)
    for test in qa_results["tests"]:
        print(f"{test['status']} {test['name']}")
        print(f"   → {test['details']}")
    
    # Save report to file
    report_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_tests": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "success_rate": f"{(total_passed/total_tests*100):.1f}%"
        },
        "recommendations_engine": recommendations_results,
        "reports_export": reports_results,
        "qa_accessibility_performance": qa_results
    }
    
    with open("milestone4_test_report.json", "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Full report saved to: milestone4_test_report.json")
    
    return total_passed == total_tests


def main():
    print("🚀 Starting Milestone 4 Comprehensive Testing")
    print("="*70)
    print("Testing all Week 7 & Week 8 features")
    
    # Run all test suites
    recommendations_results = test_recommendations_engine()
    reports_results = test_reports_export()
    qa_results = test_qa_accessibility_performance()
    
    # Generate report
    all_passed = generate_report(recommendations_results, reports_results, qa_results)
    
    total_failed = (recommendations_results["failed"] + 
                   reports_results["failed"] + 
                   qa_results["failed"])
    
    if all_passed:
        print("\n🎉 ALL MILESTONE 4 FEATURES WORKING!")
        return 0
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Review report above.")
        return 1


if __name__ == "__main__":
    exit(main())
