import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_email_config():
    with open('email_config.json') as f:
        return json.load(f)

def send_alert(product_name, product_url):
    config = load_email_config()
    
    msg = MIMEMultipart()
    msg['From'] = config['email']
    msg['To'] = ", ".join(config['recipients'])
    msg['Subject'] = f"Stock Alert: {product_name}"
    
    body = f"{product_name} is available!\n\nURL: {product_url}"
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['email'], config['password'])
            server.send_message(msg)
        print("Alert sent!")
    except Exception as e:
        print(f"Email failed: {e}")
