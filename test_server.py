"""
Simple script to test if the FastAPI server is responding.
"""
import requests
import sys

def test_server():
    base_url = "http://localhost:8080"
    
    endpoints = [
        "/",
        "/health",
        "/simple-test",
        "/api/v1/test",
    ]
    
    print("Testing FastAPI server...")
    print("="*60)
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            print(f"\nTesting: {url}")
            response = requests.get(url, timeout=5)
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text[:100]}")
        except requests.exceptions.ConnectionError as e:
            print(f"  ERROR: Connection refused - Server might not be running")
            print(f"  Details: {e}")
        except requests.exceptions.Timeout as e:
            print(f"  ERROR: Request timed out")
            print(f"  Details: {e}")
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")
    
    print("\n" + "="*60)
    print("Test complete!")

if __name__ == "__main__":
    test_server()

