from flask import Flask, render_template, request, redirect, url_for, jsonify , send_file
import os
import socket
from pathlib import Path
import http.server
import socketserver
import threading
import requests
from bs4 import BeautifulSoup
import time

filename = ''
local_ip = '192.168.31.170'

def get_localip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    return local_ip

def check_dir():
    home_dir = Path.home()
    app_dir = home_dir / 'weshare'
    upload_folder = app_dir / 'uploads' 
    app_dir.mkdir(parents=True, exist_ok=True)
    upload_folder.mkdir(parents=True, exist_ok=True)
    return upload_folder

def start_http_server(upload_folder):
    os.chdir(str(upload_folder))
    handler = http.server.SimpleHTTPRequestHandler
    port = 8080
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()

app = Flask(__name__)
upload_folder = check_dir()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/local')
def local():
    return render_template('local.html')

@app.route('/local/send', methods=['GET', 'POST'])
def send():
    global filename
    if request.method == 'GET':
        return render_template('send.html')
    elif request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('send', error='No file part'))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('send', error='No selected file'))
        if file:
            filename = os.path.join(upload_folder, file.filename)
            file.save(filename)
            threading.Thread(target=start_http_server, args=(upload_folder,), daemon=True).start()
            return render_template('hosting.html')
    return redirect(url_for('send', error='Invalid request'))

@app.route('/local/receive')
def receive():
    def check_and_download_file():
        while True:
            try:
                response = requests.get(f'http://{local_ip}:8080', timeout=1)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    file_link = soup.find('a')
                    if file_link:
                        file_name = file_link.text
                        file_url = f'http://{local_ip}:8080/{file_name}'
                        download_response = requests.get(file_url)
                        if download_response.status_code == 200:
                            return file_url
            except requests.exceptions.RequestException:
                pass
            time.sleep(3)

    file_url = check_and_download_file()
    if file_url:
        return send_file(file_url, as_attachment=True)
    else:
        return render_template('receive.html')


if __name__ == '__main__':
    local_ip = get_localip()
    app.run(debug=True, host='0.0.0.0')
