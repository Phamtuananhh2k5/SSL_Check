from flask import Flask, render_template
from ssl_checker import read_domains, check_ssl
from notifier import read_uptime_data, calculate_uptime_percentage

app = Flask(__name__)

@app.route('/')
def index():
    domains = read_domains('domains.txt')
    results = check_ssl(domains)
    uptime_data = read_uptime_data('uptime_data.json')

    for result in results:
        if 'error' not in result:
            result['uptime_percentage'] = calculate_uptime_percentage(uptime_data, result['domain'])
        else:
            result['uptime_percentage'] = 'N/A'

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)