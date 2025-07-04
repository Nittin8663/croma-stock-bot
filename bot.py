import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from notifier import send_alert

def load_products():
    """Load products from JSON configuration file"""
    with open('products.json') as f:
        return json.load(f)

def check_stock(url, debug=False):
    """
    Check stock status on Croma website
    Returns tuple: (is_available, status_message)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # Fetch page with timeout
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Debug mode - save page HTML
        if debug:
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print("⚠️ Debug: Saved page HTML to debug_page.html")

        # 1. Check main availability indicator
        availability = soup.find('div', {'class': 'pdp-delivery-options'})
        if availability:
            status_text = availability.get_text().lower()
            if 'currently unavailable' in status_text:
                return False, "❌ CURRENTLY UNAVAILABLE"
            if 'available at' in status_text:
                return True, "✅ AVAILABLE AT SELECTED LOCATIONS"

        # 2. Check Add to Cart button state
        add_button = soup.find('button', {'id': 'add-to-cart'})
        if add_button:
            if 'disabled' in add_button.attrs:
                return False, "❌ OUT OF STOCK (BUTTON DISABLED)"
            return True, "✅ IN STOCK (CAN ADD TO CART)"

        # 3. Check stock status message
        stock_message = soup.find('span', {'class': 'stock-message'})
        if stock_message:
            message_text = stock_message.get_text().strip().lower()
            if 'in stock' in message_text:
                return True, f"✅ {stock_message.get_text().strip().upper()}"
            return False, f"❌ {stock_message.get_text().strip().upper()}"

        # 4. Check price block (fallback)
        price_block = soup.find('div', {'class': 'pdp-price'})
        if price_block:
            return False, "⚠️ PRICE SHOWN BUT STOCK UNCERTAIN"

        # 5. Full text fallback check
        page_text = soup.get_text().lower()
        if 'add to cart' in page_text and 'out of stock' not in page_text:
            return True, "✅ LIKELY IN STOCK (TEXT CHECK)"
        if 'out of stock' in page_text:
            return False, "❌ LIKELY OUT OF STOCK (TEXT CHECK)"

        return False, "⚠️ UNABLE TO DETERMINE STOCK STATUS"

    except requests.exceptions.RequestException as e:
        return False, f"🚨 NETWORK ERROR: {str(e)}"
    except Exception as e:
        return False, f"🚨 PARSING ERROR: {str(e)}"

def monitor_products():
    """Main monitoring loop"""
    products = load_products()
    
    print("\n" + "="*70)
    print(f"🛒 CROMA STOCK MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")
    
    while True:
        for product in products:
            print(f"\n🔍 Checking: {product['name']}")
            print(f"🌐 URL: {product['url']}")
            
            # Enable debug=True if you need to analyze the page
            is_available, status_msg = check_stock(product['url'], debug=False)
            
            print(f"📊 Status: {status_msg}")
            print(f"⏰ Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if is_available:
                print("\n🔥🔥🔥 PRODUCT AVAILABLE! SENDING ALERT...")
                send_alert(product['name'], product['url'])
            
            print("\n" + "-"*70)
            time.sleep(product.get('check_interval', 20))

if __name__ == "__main__":
    monitor_products()
