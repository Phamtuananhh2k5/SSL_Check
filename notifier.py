import smtplib
from email.mime.text import MIMEText
import requests
import time
import json
from datetime import datetime, timedelta

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

def send_email(smtp_server, port, login, password, to_email, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = login
    msg['To'] = to_email

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(login, password)
        server.sendmail(login, to_email, msg.as_string())

def check_website_uptime(url):
    try:
        response = requests.get(f"http://{url}", timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def read_domains(file_path):
    with open(file_path, 'r') as file:
        domains = file.readlines()
    return [domain.strip() for domain in domains]

def read_uptime_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def write_uptime_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def calculate_uptime_percentage(uptime_data, domain, days=30):
    now = datetime.now()
    start_date = now - timedelta(days=days)
    total_checks = 0
    up_checks = 0

    for timestamp, status in uptime_data.get(domain, {}).items():
        check_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        if check_time >= start_date:
            total_checks += 1
            if status == "UP":
                up_checks += 1

    if total_checks == 0:
        return 0
    return (up_checks / total_checks) * 100

def monitor_websites(file_path, uptime_file, interval, token, chat_id, smtp_server, port, login, password, to_email):
    websites = read_domains(file_path)
    uptime_data = read_uptime_data(uptime_file)

    while True:
        for website in websites:
            is_up = check_website_uptime(website)
            status = "UP" if is_up else "DOWN"
            message = f"Website {website} is {status}"
            print(message)
            send_telegram_message(token, chat_id, message)
            send_email(smtp_server, port, login, password, to_email, f"Website {website} Status", message)

            # Update uptime data
            if website not in uptime_data:
                uptime_data[website] = {}
            uptime_data[website][datetime.now().strftime('%Y-%m-%d %H:%M:%S')] = status

        write_uptime_data(uptime_file, uptime_data)
        time.sleep(interval)

# Example usage
if __name__ == "__main__":
    file_path = "domains.txt"
    uptime_file = "uptime_data.json"
    interval = 30  # seconds
    token = "7880529455:AAFXem5y6kuG-uBc-87PjwXwwga3STxPEAI"
    chat_id = "your_telegram_chat_id"
    smtp_server = "smtp.phamanh.io.vn"
    port = 587
    login = "me@phamanh.io.vn"
    password = "Hoilamgi@1"
    to_email = "recipient@example.com"

    monitor_websites(file_path, uptime_file, interval, token, chat_id, smtp_server, port, login, password, to_email)