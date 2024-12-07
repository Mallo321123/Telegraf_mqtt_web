from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import re
import configparser
from time import time

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('app.conf')

app.secret_key = config["auth"]["secret_key"]

TELEGRAF_CONFIG_PATH = "telegraf.conf"
LOGIN_REQUIRED = config.getboolean("auth", "login_required", fallback=False)
LOGIN_PASSWORD = config.get("auth", "password", fallback="")

LOGIN_ATTEMPTS: dict[str, list] = {}
MAX_ATTEMPTS = int(config.get("auth", "max_attempts", fallback=3))
BLOCK_TIME = int(config.getint("auth", "block_time", fallback=60))

# Checks if an IP is blocked
def is_blocked(ip):
    if ip in LOGIN_ATTEMPTS:
        attempts, last_attempt = LOGIN_ATTEMPTS[ip]
        if attempts >= MAX_ATTEMPTS and (time() - last_attempt < BLOCK_TIME):
            return True
        elif time() - last_attempt >= BLOCK_TIME:
            del LOGIN_ATTEMPTS[ip]  # Reset nach Ablauf der Sperrzeit
    return False

# Registers a login attempt
def register_attempt(ip, success):
    """Registriert einen Login-Versuch."""
    if ip not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[ip] = [0, time()]
    attempts, last_attempt = LOGIN_ATTEMPTS[ip]

    if success:
        del LOGIN_ATTEMPTS[ip]  # Bei Erfolg: Reset
    else:
        LOGIN_ATTEMPTS[ip] = [attempts + 1, time()]  # Erhöht Zähler bei Fehlschlag

# Reads topic list from telegraf.conf
def read_topics():
    with open(TELEGRAF_CONFIG_PATH, "r") as file:
        config_data = file.read()

    # searches for [[inputs.mqtt_consumer]] and extracts topics
    mqtt_consumer_match = re.search(r'\[\[inputs\.mqtt_consumer\]\](.*?)\n\s*topics\s*=\s*\[(.*?)\]', config_data, re.DOTALL)
    
    if mqtt_consumer_match:
        topics_string = mqtt_consumer_match.group(2).strip()
        topics = re.findall(r'"([^"]*)"', topics_string)
        return topics
    return []  # In case no Topics are found

# Saves topics to telegraf.conf
def save_topics(topics):
    with open(TELEGRAF_CONFIG_PATH, 'r') as file:
        config_data = file.read()

    # RegEx to Find topics in telegraf.conf
    topics_match = re.search(r'topics\s*=\s*\[(.*?)\]', config_data, re.DOTALL)
    if topics_match:
        new_topics_string = "\n     ".join([f'"{topic}"' for topic in topics])
        config_data = re.sub(r'topics\s*=\s*\[([^\]]+)\]', f'topics = [\n     {new_topics_string},\n   ]', config_data)

    with open(TELEGRAF_CONFIG_PATH, 'w') as file:
        file.write(config_data)
    
        return {"status": "success", "message": "Topics erfolgreich gespeichert!"}


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
        return jsonify({"error": "Login ist deaktiviert."}), 403

    ip = request.remote_addr
    if is_blocked(ip):
        return render_template("login.html", error="Zu viele Fehlversuche. Versuchen Sie es später erneut.")

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
    
    return jsonify({"topics": topics})

@app.route('/api/save-config', methods=['POST'])
def save_config():
    if LOGIN_REQUIRED and not session.get("logged_in"):
        return jsonify({"error": "Nicht autorisiert."}), 403
    
    data = request.get_json()
    topics = data.get('topics', [])
    
    return jsonify(save_topics(topics))


app.run(config["web"]["host"], int(config["web"]["port"]))