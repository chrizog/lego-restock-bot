# lego-restock-bot

<img src="./assets/pylint.svg"><br>

Get informed when Lego shop products are available again.

This project uses scrapy to extract information from the German Lego shop page.
It crawls products from the shop and scrapes their information. You can regularly run the scraping to check whether products are in stock again.
In case of available products, you can send automatic Telegram messages to stay up to date.

Find the blog article about the project here: [A Real-World Scrapy Tutorial - Python Lego Shop Restock Bot](https://chrizog.com/lego-shop-python-scraping)

### Installation

Create a Python virtual environment and install dependencies:

```shell
python3 -m venv venv_lego
pip3 install -r requirements.txt
```

### Searching Lego products

It's enough to run this command once. It will save crawled lego products to the SQLite database. Since the products rarely change, it's sufficient to run this sometimes manually.

```shell
scrapy crawl products
```

### Update availability and prices of found products

For retrieving the availabilities of all products in the database, use the availability spider and pipelines. It will save the latest availability information in the database.

```shell
scrapy crawl availability
```

### Generate Telegram notifications

In the .env file set the Telegram Bot token and the channel ID. The Bot needs to be administrator of the channel.

```
TELEGRAM_BOT_TOKEN=<bot token>
TELEGRAM_CHANNEL_ID=<channel ID>
```

In order to figure out the channel ID, send the channel invitation link to @username_to_id_bot


### Automatic notifications

In case you want to get updates regularly, execute the script "update_availability.sh" in a cron job. In case you want to run the script every two hours add the following using crontab -e:

```
0 */2 * * * /<your full path>/update_availability.sh
```

Inside the bash script, configure the two variables with your corresponding paths:

```bash
VENV_PATH=""
SCRAPY_PROJECT_ROOT_DIR=""
```