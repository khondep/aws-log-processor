import requests
import json
import time

# Replace with your actual API endpoint
API_ENDPOINT = "https://1b1iwb6x74.execute-api.us-east-1.amazonaws.com/ingest"

def test_json_upload():
    """Test JSON format upload"""
    print("Testing JSON upload...")
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "tenant_id": "acme_corp",
        "log_id": "test_json_001",
        "text": "User 555-0199 accessed the system at 10:30 AM"
    }
    
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_text_upload():
    """Test plain text upload"""
    print("Testing plain text upload...")
    
    headers = {
        'Content-Type': 'text/plain',
        'X-Tenant-ID': 'beta_inc'
    }
    data = "System log: Error 404 at endpoint /api/users. Contact: 555-1234"
    
    response = requests.post(API_ENDPOINT, headers=headers, data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_multiple_tenants():
    """Test tenant isolation with multiple requests"""
    print("Testing multiple tenants...")
    
    tenants = ['company_a', 'company_b', 'company_c']
    
    for i, tenant in enumerate(tenants):
        headers = {'Content-Type': 'application/json'}
        data = {
            "tenant_id": tenant,
            "log_id": f"multi_test_{i}",
            "text": f"Log entry {i} for {tenant}"
        }
        
        response = requests.post(API_ENDPOINT, headers=headers, json=data)
        print(f"Tenant {tenant}: Status {response.status_code}")
    
    print()

def load_test(num_requests=10):
    """Simple load test"""
    print(f"Running load test with {num_requests} requests...")
    
    start_time = time.time()
    success_count = 0
    
    for i in range(num_requests):
        headers = {'Content-Type': 'application/json'}
        data = {
            "tenant_id": f"load_test_tenant",
            "log_id": f"load_test_{i}",
            "text": f"Load test message {i} with some text to process"
        }
        
        try:
            response = requests.post(API_ENDPOINT, headers=headers, json=data, timeout=5)
            if response.status_code == 202:
                success_count += 1
        except Exception as e:
            print(f"Request {i} failed: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Completed {num_requests} requests in {duration:.2f} seconds")
    print(f"Success rate: {success_count}/{num_requests}")
    print(f"Requests per second: {num_requests/duration:.2f}")
    print()

if __name__ == "__main__":
    print("Starting API tests...\n")
    
    # Run tests
    test_json_upload()
    time.sleep(2)
    
    test_text_upload()
    time.sleep(2)
    
    test_multiple_tenants()
    time.sleep(5)  # Wait for processing
    
    # Simple load test
    load_test(20)
    
    print("\nTests complete!")
    print("Wait 30-60 seconds for all messages to process")
    print("Then check DynamoDB table for results")
