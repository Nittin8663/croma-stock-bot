import json
import time
import requests
from bs4 import BeautifulSoup
from notifier import send_alert
from datetime import datetime

def load_products():
    with open('products.json') as f:
        return json.load(f)

def check_stock(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple ways to detect stock status
        stock_element = soup.find('button', {'id': 'addToCart'}) or \
                       soup.find('span', {'class': 'stock'}) or \
                       soup.find('div', {'class': 'availability'})
        
        if stock_element:
            status_text = stock_element.text.strip().lower()
            if any(word in status_text for word in ['add to cart', 'in stock', 'available']):
                return True, "✅ IN STOCK - BUY NOW!"
            elif any(word in status_text for word in ['out of stock', 'sold out', 'unavailable']):
                return False, "❌ OUT OF STOCK"
        
        # Price is sometimes a good indicator
        price_element = soup.find('span', {'class': 'amount'})
        if price_element:
            return False, "⚠️ PRICE SHOWN BUT STOCK UNCERTAIN"
            
        return False, "⚠️ STOCK STATUS UNKNOWN - CHECK MANUALLY"
        
    except requests.exceptions.RequestException as e:
        return False, f"🚨 NETWORK ERROR: {str(e)}"
    except Exception as e:
        return False, f"🚨 PARSING ERROR: {str(e)}"

def monitor_products():
    products = load_products()
    print("\n" + "="*60)
    print(f"🛒 CROMA STOCK MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
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
            
            print("\n" + "-"*60)
            time.sleep(product.get('check_interval', 20))

if __name__ == "__main__":
    monitor_products()
