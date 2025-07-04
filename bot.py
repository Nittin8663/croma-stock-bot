import json
import time
import requests
from bs4 import BeautifulSoup
from notifier import send_alert

def load_products():
    with open('products.json') as f:
        return json.load(f)

def check_stock(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Adjust this selector for Croma's website
        stock_element = soup.find('span', {'class': 'stock-status'})
        
        if stock_element:
            status = stock_element.text.strip().lower()
            if "in stock" in status:
                return True, "✅ IN STOCK"
            elif "out of stock" in status:
                return False, "❌ OUT OF STOCK"
        return False, "⚠️ STOCK STATUS UNKNOWN"
    except Exception as e:
        return False, f"🚨 ERROR: {str(e)}"

def monitor_products():
    products = load_products()
    print("\n🛒 Croma Stock Monitor Started\n")
    print("-" * 50)
    
    while True:
        for product in products:
            print(f"\nChecking: {product['name']}")
            print(f"URL: {product['url']}")
            
            is_available, status_msg = check_stock(product['url'])
            print(f"Status: {status_msg}")
            print(f"Last Check: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if is_available:
                print("\n🔥 PRODUCT AVAILABLE! SENDING ALERT...")
                send_alert(product['name'], product['url'])
            
            print("-" * 50)
            time.sleep(product.get('check_interval', 20))

if __name__ == "__main__":
    monitor_products()
