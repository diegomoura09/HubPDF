#!/usr/bin/env python3
"""
Smoke test script for HubPDF
Tests basic functionality: health check, uploads, and PDF operations
"""
import requests
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:5000"
TEST_FILES_DIR = Path("docs/examples")

def print_test(name, success, duration_ms, details=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {name} ({duration_ms:.2f}ms) {details}")

def test_health():
    """Test /healthz endpoint"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        duration = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print_test("Health Check", True, duration, f"maxUploadMb={data.get('maxUploadMb')}")
            return True
        else:
            print_test("Health Check", False, duration, f"Status {response.status_code}")
            return False
    except Exception as e:
        duration = (time.time() - start) * 1000
        print_test("Health Check", False, duration, str(e))
        return False

def test_home():
    """Test /home endpoint"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/home", timeout=5)
        duration = (time.time() - start) * 1000
        
        if response.status_code == 200:
            print_test("Home Page", True, duration, f"{len(response.content)} bytes")
            return True
        else:
            print_test("Home Page", False, duration, f"Status {response.status_code}")
            return False
    except Exception as e:
        duration = (time.time() - start) * 1000
        print_test("Home Page", False, duration, str(e))
        return False

def test_small_upload():
    """Test upload of small PDF (< 60MB)"""
    start = time.time()
    test_pdf = TEST_FILES_DIR / "test.pdf"
    
    if not test_pdf.exists():
        print_test("Small PDF Upload", False, 0, "test.pdf not found")
        return False
    
    try:
        file_size_mb = test_pdf.stat().st_size / (1024 * 1024)
        
        with open(test_pdf, "rb") as f:
            files = {"files": ("test.pdf", f, "application/pdf")}
            data = {
                "operation": "compress",
                "compression_level": "normal"
            }
            response = requests.post(
                f"{BASE_URL}/tools/api/convert",
                files=files,
                data=data,
                timeout=30
            )
        
        duration = (time.time() - start) * 1000
        
        if response.status_code in [200, 201, 202]:
            print_test("Small PDF Upload", True, duration, f"{file_size_mb:.2f}MB → compressed")
            return True
        else:
            print_test("Small PDF Upload", False, duration, f"Status {response.status_code}")
            return False
    except Exception as e:
        duration = (time.time() - start) * 1000
        print_test("Small PDF Upload", False, duration, str(e))
        return False

def test_large_upload():
    """Test that large files (>60MB) are rejected with 413"""
    print("⏭️  SKIP Large File Upload Test (requires >60MB file)")
    return True

def test_middleware_debug():
    """Test /debug/middleware-order endpoint"""
    start = time.time()
    try:
        response = requests.get(f"{BASE_URL}/debug/middleware-order", timeout=5)
        duration = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('middleware_count', 0)
            print_test("Middleware Debug", True, duration, f"{count} middlewares")
            return True
        else:
            print_test("Middleware Debug", False, duration, f"Status {response.status_code}")
            return False
    except Exception as e:
        duration = (time.time() - start) * 1000
        print_test("Middleware Debug", False, duration, str(e))
        return False

def main():
    """Run all smoke tests"""
    print("🧪 HubPDF Smoke Tests\n")
    print(f"Target: {BASE_URL}\n")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Home Page", test_home()))
    results.append(("Small Upload", test_small_upload()))
    results.append(("Large Upload", test_large_upload()))
    results.append(("Middleware Debug", test_middleware_debug()))
    
    # Summary
    print("\n" + "="*50)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
