import re

from config import TELEGRAF_CONFIG_PATH

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

# reads server address from telegraf.conf
def read_server_addr():
    with open(TELEGRAF_CONFIG_PATH, "r") as file:
        config_data = file.read()

    # searches for [[inputs.mqtt_consumer]] and extracts topics
    mqtt_consumer_match = re.search(r'\[\[inputs\.mqtt_consumer\]\](.*?)\n\s*servers\s*=\s*\[(.*?)\]', config_data, re.DOTALL)
    
    if mqtt_consumer_match:
        servers_string = mqtt_consumer_match.group(2).strip()
        servers = re.findall(r'"([^"]*)"', servers_string)
        return servers
    return []  # In case no Topics are found

# reads QoS from telegraf.conf
def read_qos():
    with open(TELEGRAF_CONFIG_PATH, "r") as file:
        config_data = file.read()
        
    mqtt_consumer_match = mqtt_consumer_match = re.search(r'\[\[inputs\.mqtt_consumer\]\](.*?)^[ \t]*qos\s*=\s*(\d+)', config_data, re.MULTILINE | re.DOTALL)

    if mqtt_consumer_match:
        return mqtt_consumer_match.group(2)
    return []