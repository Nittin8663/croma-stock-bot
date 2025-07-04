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
        
        # Adjust this selector for Croma's current website
        stock_status = soup.find('span', {'class': 'stock'})
        return stock_status and "in stock" in stock_status.text.lower()
    except Exception as e:
        print(f"Error checking stock: {e}")
        return False

def monitor_products():
    products = load_products()
    
    while True:
        for product in products:
            print(f"Checking {product['name']}...")
            if check_stock(product['url']):
                print(f"{product['name']} is in stock!")
                send_alert(product['name'], product['url'])
            time.sleep(product.get('check_interval', 20))

if __name__ == "__main__":
    monitor_products()
