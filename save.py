import re

from config import TELEGRAF_CONFIG_PATH

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
        return True

    return False

# Saves server address to telegraf.conf
def save_server_addr(server_addr):
    with open(TELEGRAF_CONFIG_PATH, 'r') as file:
        config_data = file.read()
    # RegEx, um die servers-Zeile zu finden
    mqtt_section_match = re.search(r'\[\[inputs\.mqtt_consumer\]\](.*?)(?=\n\[|\Z)', config_data, re.DOTALL)
    
    if mqtt_section_match:
        section_content = mqtt_section_match.group(0)
        # Nur aktive servers-Zeilen bearbeiten (keine auskommentierten)
        active_servers_match = re.search(r'^\s*servers\s*=\s*\[([^\]]+)\]', section_content, re.MULTILINE)
        
        if active_servers_match:
            # Neues Server-Format erstellen
            new_servers_string = f'{server_addr}'
            # Ersetzen der aktiven servers-Zeile
            updated_section = re.sub(r'^\s*servers\s*=\s*\[([^\]]+)\]', f'   servers = {new_servers_string}', section_content, flags=re.MULTILINE)

            # Abschnitt in der Konfiguration aktualisieren
            config_data = config_data.replace(section_content, updated_section)

            # Datei speichern
            with open(TELEGRAF_CONFIG_PATH, 'w') as file:
                file.write(config_data)
                return True

    return False

# Saves QoS to telegraf.conf
def save_qos(qos):
    if qos not in (0, 1, 2):
        return False
    
    with open(TELEGRAF_CONFIG_PATH, "r") as file:
        config_data = file.read()

    # Ersetzt den vorhandenen QoS-Wert durch den neuen Wert
    updated_config_data = re.sub(
        r'(^[ \t]*qos\s*=\s*)(\d+)',  # Findet die `qos =`-Zeile mit dem aktuellen Wert
        rf'\1{qos}',              # Ersetzt den Wert durch `new_qos`, behält das Präfix bei
        config_data,
        flags=re.MULTILINE
    )

    with open(TELEGRAF_CONFIG_PATH, "w") as file:
        file.write(updated_config_data)
    return True