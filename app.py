from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from time import time
import toml

#from read import read_topics, read_server_addr, read_qos, read_connection_timeout
#from save import save_topics, save_server_addr, save_qos, save_connection_timeout
from config import config, LOGIN_ATTEMPTS, MAX_ATTEMPTS, BLOCK_TIME, LOGIN_REQUIRED, LOGIN_PASSWORD, TELEGRAF_CONFIG, TELEGRAF_CONFIG_PATH

app = Flask(__name__)
app.secret_key = config["auth"]["secret_key"]

def update_toml(input_data):
    for section, section_data in input_data.items():
        if section in TELEGRAF_CONFIG:
            for key, value in section_data.items():
                if isinstance(value, dict):
                    if key in TELEGRAF_CONFIG[section]:
                        update_toml(TELEGRAF_CONFIG[section], {key: value})
                else:
                    TELEGRAF_CONFIG[section][key] = value
    return TELEGRAF_CONFIG

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
    
    conf = TELEGRAF_CONFIG["inputs"]["mqtt_consumer"]
    
    return jsonify(conf)

@app.route('/api/save-config', methods=['POST'])
def save_config():
    if LOGIN_REQUIRED and not session.get("logged_in"):
        return jsonify({"error": "Not authorized."}), 403
    
    data = request.get_json()
    new_config = update_toml(data)
    
    with open(TELEGRAF_CONFIG_PATH, 'w') as f:
        toml.dump(new_config, f)
    
    return jsonify({"status": "success", "message": "config saved succesfully!"})


app.run(config["web"]["host"], int(config["web"]["port"]))