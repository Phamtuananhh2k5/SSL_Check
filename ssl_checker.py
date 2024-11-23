import ssl
import socket
from datetime import datetime
import requests

def read_domains(file_path):
    with open(file_path, 'r') as file:
        domains = file.readlines()
    return [domain.strip() for domain in domains]

def get_ssl_expiry_date(domain):
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
    conn.settimeout(3.0)
    conn.connect((domain, 443))
    ssl_info = conn.getpeercert()
    expiry_date = datetime.strptime(ssl_info['notAfter'], '%b %d %H:%M:%S %Y %Z')
    return expiry_date

def check_website_uptime(url):
    try:
        response = requests.get(f"http://{url}", timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def check_ssl(domains):
    results = []
    for domain in domains:
        try:
            expiry_date = get_ssl_expiry_date(domain)
            days_left = (expiry_date - datetime.now()).days
            is_up = check_website_uptime(domain)
            results.append({'domain': domain, 'expiry_date': expiry_date, 'days_left': days_left, 'is_up': is_up})
        except Exception as e:
            results.append({'domain': domain, 'error': str(e), 'is_up': False})
    return results