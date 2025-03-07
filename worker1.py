from flask import Flask, request, jsonify
import hashlib
import requests
import socket

app = Flask(__name__)

HIBP_API_URL = "https://api.pwnedpasswords.com/range/"

def check_password_pwned(password):
    """
    Mengecek apakah password pernah bocor menggunakan HIBP API.
    """
    sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1_hash[:5], sha1_hash[5:]

    try:
        response = requests.get(HIBP_API_URL + prefix, timeout=5)
        if response.status_code == 200:
            hashes = response.text.splitlines()
            for h in hashes:
                if suffix in h:
                    return True
    except requests.exceptions.RequestException:
        pass
    return False

@app.route('/check_password', methods=['POST'])
def check_password():
    data = request.json
    passwords = data['passwords']

    worker_name = socket.gethostname()

    results = []
    for password in passwords:
        pwned = check_password_pwned(password)
        results.append({"password": password, "pwned": pwned})

    return jsonify({
        "worker": worker_name,
        "passwords_checked": len(passwords),
        "results": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
