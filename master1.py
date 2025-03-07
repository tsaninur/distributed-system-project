from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# Daftar worker
workers = ["http://192.168.92.177:5000", "http://192.168.92.176:5001"]

def check_worker_availability(worker_url):
    """
    Memeriksa ketersediaan worker.
    """
    try:
        response = requests.get(f"{worker_url}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def distribute_lines(passwords):
    """
    Mengirim password ke worker untuk diperiksa.
    """
    available_workers = [worker for worker in workers if check_worker_availability(worker)]
    
    if not available_workers:
        print("Tidak ada worker yang tersedia.")
        return [], []

    chunk_size = len(passwords) // len(available_workers)
    chunks = [passwords[i:i + chunk_size] for i in range(0, len(passwords), chunk_size)]
    results = []
    logs = []

    for i, chunk in enumerate(chunks):
        worker_url = available_workers[i % len(available_workers)]
        try:
            response = requests.post(f"{worker_url}/check_password", json={"passwords": chunk}, timeout=5)
            worker_result = response.json()

            logs.append({
                "worker": worker_result['worker'],
                "passwords_checked": worker_result['passwords_checked'],
                "results": worker_result['results']
            })

            results.extend(worker_result['results'])
        except requests.exceptions.RequestException:
            print(f"Worker {worker_url} tidak merespons.")

    return results, logs

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Tidak ada file yang diunggah."})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Nama file tidak valid."})
    
    passwords = file.read().decode('utf-8').splitlines()
    
    results, logs = distribute_lines(passwords)
    
    return jsonify({
        "status": "success",
        "results": results,
        "logs": logs
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
