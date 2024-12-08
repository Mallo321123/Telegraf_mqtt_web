from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from time import time

from read import read_topics, read_server_addr, read_qos
from save import save_topics, save_server_addr, save_qos
from config import config, LOGIN_ATTEMPTS, MAX_ATTEMPTS, BLOCK_TIME, LOGIN_REQUIRED, LOGIN_PASSWORD

app = Flask(__name__)
app.secret_key = config["auth"]["secret_key"]

# Checks if an IP is blocked
def is_blocked(ip):
    if ip in LOGIN_ATTEMPTS:
        attempts, last_attempt = LOGIN_ATTEMPTS[ip]
        if attempts >= MAX_ATTEMPTS and (time() - last_attempt < BLOCK_TIME):
            return True
        elif time() - last_attempt >= BLOCK_TIME:
            del LOGIN_ATTEMPTS[ip]  # Reset after block time
    return False

# Registers a login attempt
def register_attempt(ip, success):
    """Registriert einen Login-Versuch."""
    if ip not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[ip] = [0, time()]
    attempts, last_attempt = LOGIN_ATTEMPTS[ip]

    if success:
        del LOGIN_ATTEMPTS[ip]  # Deletes entry if successful
    else:
        LOGIN_ATTEMPTS[ip] = [attempts + 1, time()]  # Increases counter if failed


# Middleware for login check
@app.before_request
def require_login():
    if LOGIN_REQUIRED and 'logged_in' not in session and request.endpoint not in ('login', 'static'):
        return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not LOGIN_REQUIRED:
        return jsonify({"error": "Login is deactivated."}), 403

    ip = request.remote_addr
    if is_blocked(ip):
        return render_template("login.html", error="To many Failed login attempts. Please try again later.")

    if request.method == 'POST':
        password = request.form.get("password", "")
        if password == LOGIN_PASSWORD:
            session["logged_in"] = True
            register_attempt(ip, success=True)
            return redirect(url_for("index"))
        else:
            register_attempt(ip, success=False)
            return render_template("login.html", error="Falsches Passwort.")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route('/api/config', methods=['GET'])
def get_config():
    if LOGIN_REQUIRED and not session.get("logged_in"):
        return jsonify({"error": "Nicht autorisiert."}), 403
    
    topics = read_topics()
    server_addr = read_server_addr()
    qos = read_qos()
    
    return jsonify({"topics": topics, "server_addr": server_addr, "qos": qos})

@app.route('/api/save-config', methods=['POST'])
def save_config():
    if LOGIN_REQUIRED and not session.get("logged_in"):
        return jsonify({"error": "Not authorized."}), 403
    
    data = request.get_json()
    
    topics = data.get('topics', [])
    server_addr = data.get('server_addr', [])
    qos = data.get('qos', None)
    
    if topics:
        if not save_topics(topics):
            return jsonify({"error": "Failed to save topics."}), 500
    
    if server_addr:
        if not save_server_addr(server_addr):
            return jsonify({"error": "Failed to save Server adress."}), 500
        
    if qos:
        if not save_qos(qos):
            return jsonify({"error": "Failed to save qos value."}), 500
    
    return jsonify({"status": "success", "message": "config saved succesfully!"})


app.run(config["web"]["host"], int(config["web"]["port"]))