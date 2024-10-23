from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from pathlib import Path
import time

app = Flask(__name__)
avail = False

def check_dir():
    home_dir = Path.home()
    upload_folder = home_dir / 'weshare' / 'uploads'
    upload_folder.mkdir(parents=True, exist_ok=True)
    return upload_folder

upload_folder = check_dir()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/local')
def local():
    return render_template('local.html')

@app.route('/hosting')
def hosting():
    return render_template('hosting.html')

@app.route('/local/send', methods=['GET', 'POST'])
def send():
    global avail

    if request.method == 'GET':
        return render_template('send.html')
    elif request.method == 'POST':
        if 'file' not in request.files or request.files['file'].filename == '':
            return redirect(url_for('send', error='No file part or no file selected'))
        
        file = request.files['file']
        original_filename, file_extension = os.path.splitext(file.filename)
        timestamp = time.strftime("%d%m%y_%H%M%S")
        new_filename = f"{original_filename}_{timestamp}{file_extension}"
        filepath = os.path.join(upload_folder, new_filename)
        file.save(filepath)

        avail = True
        return redirect(url_for('hosting'))

@app.route('/local/send/status')
def send_status():
    if avail:
        return '', 200
    else:
        return '', 400

@app.route('/uploads')
def download_file():
    files = os.listdir(upload_folder)
    if files:
        filename = files[0]
        return send_from_directory(upload_folder, filename, as_attachment=True)
    else:
        return "No file available for download", 404

@app.route('/local/receive')
def receive():
    receiver_ip = '192.168.31.170'
    return render_template('receive.html', receiver_ip=receiver_ip)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
