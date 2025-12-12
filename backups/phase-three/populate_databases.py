import requests
import time

BASE_URL = "http://localhost:8081"

def populate_data():
    print("=== POPULATING DATABASES ===\n")
    
    # Test cases to populate
    test_cases = [
        ("stocks", "AAPL"),
        ("forex", "EUR/USD"),
        ("commodities", "WTI"),
        ("commodities", "GOLD")
    ]
    
    for data_type, symbol in test_cases:
        print(f"Fetching {data_type.upper()} {symbol}...")
        try:
            response = requests.get(f"{BASE_URL}/api/fetch-data?type={data_type}&symbol={symbol}", timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                print(f"✅ {result.get('success', 'Success')}")
            else:
                print(f"❌ {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Rate limiting
        print()

if __name__ == "__main__":
    populate_data()
    print("Database population completed!")