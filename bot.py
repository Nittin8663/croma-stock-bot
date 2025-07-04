import json
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from notifier import send_alert

# Chrome-only user agents (updated July 2025)
CHROME_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36'
]

def load_products():
    with open('products.json') as f:
        return json.load(f)

def make_chrome_request(url, retries=3):
    """Make request with Chrome-specific headers"""
    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': random.choice(CHROME_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Ch-Ua': '"Chromium";v="125", "Google Chrome";v="125"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Random delay with Chrome-like pattern
            time.sleep(random.uniform(1.2, 2.8))
            
            response = requests.get(url, 
                                 headers=headers,
                                 timeout=15,
                                 cookies={'croma_region': 'IN'})  # Simulate location
            
            # Chrome-like status code handling
            if response.status_code == 403:
                raise requests.exceptions.HTTPError("403 Forbidden (Chrome)")
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            if "403" in str(e):
                print(f"⚠️ Chrome blocked (attempt {attempt+1}). Waiting...")
                time.sleep(random.uniform(5, 8))  # Longer Chrome-like delay
                continue
            raise
    raise Exception(f"Chrome failed after {retries} attempts")

def check_stock(url):
    try:
        response = make_chrome_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Chrome-specific element detection
        stock_data = soup.find('div', {'data-testid': 'pdp-stock-status'}) or \
                   soup.find('button', {'data-testid': 'add-to-cart'})
        
        if stock_data:
            text = stock_data.get_text().strip().lower()
            if any(x in text for x in ['in stock', 'add to cart']):
                return True, "✅ CHROME DETECTED: IN STOCK"
            return False, f"❌ CHROME DETECTED: {stock_data.get_text().strip().upper()}"
        
        return False, "⚠️ CHROME: STOCK STATUS UNKNOWN"

    except Exception as e:
        return False, f"🚨 CHROME ERROR: {str(e)}"

def monitor_products():
    products = load_products()
    print("\n" + "="*70)
    print(f"🛒 CHROME STOCK MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    while True:
        for product in products:
            print(f"\n🔍 Chrome Checking: {product['name']}")
            print(f"🌐 URL: {product['url']}")
            
            is_available, status_msg = check_stock(product['url'])
            print(f"📊 Status: {status_msg}")
            print(f"⏰ Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if is_available:
                print("\n🔥 CHROME ALERT: PRODUCT AVAILABLE!")
                send_alert(product['name'], product['url'])
            
            # Chrome-like random delay (25-40s)
            delay = random.uniform(25, 40)
            print(f"⏳ Next check in {delay:.1f}s...")
            time.sleep(delay)

if __name__ == "__main__":
    monitor_products()
