import os
import pathlib


def get_value(key, default=None, converter=None):
    value = os.environ.get(key, default) or default
    if converter:
        return converter(value)
    return str(value)


# About
author = "Kylmakalle"
git_repository = "https://github.com/Kylmakalle/assistant-bot"

# Paths
work_dir = pathlib.Path(__file__).parent.parent
locales_dir = work_dir / 'locales'

# Telegram
bot_token = get_value('BOT_TOKEN', '')
skip_updates = get_value('SKIP_UPDATES', False, bool)

# Webhook
use_webhook = get_value('WEBHOOK', False, bool)
webhook_url = get_value('WEBHOOK_URL', None)
webhook_server = {
    'host': get_value('WEBHOOK_HOST', '0.0.0.0'),
    'port': get_value('WEBHOOK_PORT', 80, int),
    'webhook_path': get_value('WEBHOOK_PATH', '/webhook')
}

# Database
mongodb = {
    'host': get_value('MONGODB_HOST', 'mongodb'),
    'maxPoolSize': get_value('MONGODB_MAX_POOL_SIZE', 1000, int),
    'retryWrites': get_value('MONGODB_RETRY_WRITES', True, bool)
}

# Captcha Button
kick_delay = get_value('KICK_DELAY', 30, int)

# Metrics
mixpanel_key = get_value('MIXPANEL_KEY', '')

log_channel = get_value('LOG_CHANNEL', 0, int)
