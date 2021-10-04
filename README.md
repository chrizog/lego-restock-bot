# lego-restock-bot

Get informed when Lego shop products are available again.

### Installation

Create a Python virtual environment and install dependencies:

```
python3 -m venv venv_lego
pip3 install -r requirements.txt
```

### Searching Lego products

```
scrapy crawl products
```

### Update availability and prices of found products

```
scrapy crawl availability
```

### Generate Telegram notifications

In the .env file set the Telegram Bot token and the channel ID. The Bot needs to be administrator of the channel.

```
TELEGRAM_BOT_TOKEN=<bot token>
TELEGRAM_CHANNEL_ID=<channel ID>
```

In order to figure out the channel ID, send the channel invitation link to @username_to_id_bot
.