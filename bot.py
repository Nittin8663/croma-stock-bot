import json
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from notifier import send_alert

# List of realistic user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
]

def load_products():
    with open('products.json') as f:
        return json.load(f)

def make_request(url, retries=3):
    """Make request with retries and random delays"""
    for attempt in range(retries):
        try:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.croma.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'DNT': '1'
            }
            
            # Random delay between 1-3 seconds
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"⚠️ Blocked attempt {attempt + 1}/{retries}. Retrying...")
                time.sleep(5)  # Longer delay if blocked
                continue
            raise
    raise Exception(f"Failed after {retries} attempts")

def check_stock(url, debug=False):
    try:
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug mode
        if debug:
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("⚠️ Debug: Saved page HTML to debug_page.html")

        # 1. Check main availability indicator
        availability = soup.find('div', {'data-testid': 'pdp-stock-status'})
        if availability:
            status_text = availability.get_text().strip().lower()
            if 'in stock' in status_text:
                return True, "✅ IN STOCK"
            return False, f"❌ {availability.get_text().strip().upper()}"

        # 2. Check price block (secondary indicator)
        price = soup.find('span', {'data-testid': 'pdp-offer-price'})
        if price:
            return False, "⚠️ PRICE SHOWN BUT STOCK UNCERTAIN"

        return False, "⚠️ UNABLE TO DETERMINE STOCK STATUS"

    except Exception as e:
        return False, f"🚨 ERROR: {str(e)}"

def monitor_products():
    products = load_products()
    print("\n" + "="*70)
    print(f"🛒 CROMA STOCK MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    while True:
        for product in products:
            print(f"\n🔍 Checking: {product['name']}")
            print(f"🌐 URL: {product['url']}")
            
            is_available, status_msg = check_stock(product['url'])
            print(f"📊 Status: {status_msg}")
            print(f"⏰ Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if is_available:
                print("\n🔥🔥🔥 PRODUCT AVAILABLE! SENDING ALERT...")
                send_alert(product['name'], product['url'])
            
            print("\n" + "-"*70)
            time.sleep(max(product.get('check_interval', 30), random.uniform(25, 35)))

if __name__ == "__main__":
    monitor_products()
