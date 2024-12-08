import configparser

config = configparser.ConfigParser()
config.read('app.conf')

TELEGRAF_CONFIG_PATH = "telegraf.conf"
LOGIN_REQUIRED = config.getboolean("auth", "login_required", fallback=False)
LOGIN_PASSWORD = config.get("auth", "password", fallback="")

LOGIN_ATTEMPTS: dict[str, list] = {}
MAX_ATTEMPTS = int(config.get("auth", "max_attempts", fallback=3))
BLOCK_TIME = int(config.getint("auth", "block_time", fallback=60))