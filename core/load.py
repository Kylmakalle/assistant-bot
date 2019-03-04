from core import misc


def load_modules():
    misc.loader.load_packages(f"modules.{item}" for item in [
        'base',  # User management and base Middlewares
        'captcha_button',  # Captcha for new joined users
        'voteban',  # Voteban in chats
        'nsfw',  # Checking media for nsfw
        'tail',  # Handle all unhandled actions
    ])
