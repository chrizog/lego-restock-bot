#!/usr/bin/python3

"""Script which checks the availability of Lego products

Adds new entries to the Availability database for the newest availability
If an availability changes to "available" it sends notifications via Telegram
"""

from dotenv import dotenv_values
from lego.database import (
    load_product_ids,
    get_availabilities,
    db_connect,
    get_product_name,
    get_product,
)
from lego.items import availability_int_to_str
from lego.telegram_message import LegoRestockBot

if __name__ == "__main__":
    config = dotenv_values(".env")
    engine = db_connect()
    product_ids = load_product_ids(engine)

    for product_id in product_ids:
        availabilites = get_availabilities(product_id, engine)

        if len(availabilites) > 1:
            last_availability = availabilites[-1]["availability"]
            n_last_availability = availabilites[-2]["availability"]

            if not last_availability == n_last_availability:
                old_status = availability_int_to_str(n_last_availability)
                new_status = availability_int_to_str(last_availability)
                product_name = get_product_name(product_id, engine)

                if last_availability in [
                    1,
                    4,
                ]:  # 1: Jetzt verfügbar oder 4: Nachbestellungen möglich
                    telegram_bot = LegoRestockBot(
                        config["TELEGRAM_BOT_TOKEN"], config["TELEGRAM_CHANNEL_ID"]
                    )
                    product = get_product(product_id, engine)

                    if last_availability == 1:
                        message = telegram_bot.create_message_available(
                            product_id, product.name, product.url, product.price
                        )
                    else:
                        message = telegram_bot.create_message_reorder(
                            product_id, product.name, product.url
                        )
                    telegram_bot.send_html_message_to_channel(message)
