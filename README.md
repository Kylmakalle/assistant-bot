# Assistant bot

Helper bot for russian Telegram chats [/hw/](https://t.me/ru2chhw) & [/mobi/](https://t.me/ru2chmobi)

# Run
```bash
cp example.env .env
# Edit env file with bot token
docker-compose -f docker-compose.local.yml up -d
```

# Tech Info
Bot uses aiogram framework. Bot has public and private modules cause bot owner requires some additional stuff to run the bot.
Repo have averything that requires to run/contribute public bot version

You can also set additional env-file options

```dotenv
SKIP_UPDATES=Skip telegram updates while bot was dowb
MIXPANEL_KEY=mixpanel.com for stats
LOG_CHANNEL=telegram id for log channel
SENTRY_URL=sentry.io error logging url
CLARIFAI_TOKEN=clarifai.ai token for media recognition as NSFW/SFW
```

And also some Telegram webhook stuff
```dotenv
WEBHOOK=True
WEBHOOK_URL=https://domain.com/webhook
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=80
WEBHOOK_PATH=/webhook
```

or custom mongo database, like this one below

```dotenv
MONGODB_HOST=assistantbot-mongodb
MONGODB_MAX_POOL_SIZE=1000
MONGODB_RETRY_WRITES=1
```

# Develop
Setup environment
```bash
pip install -r requirements-dev.txt
```

## Linters and formatters

For staged files
```bash
pre-commit run
```

for all files
```bash
pre-commit run --all-files
```

# Author
https://t.me/Kylmakalle

# License
MIT
