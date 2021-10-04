#!/usr/bin/python3

import datetime
from dotenv import dotenv_values
from database import (
    load_product_ids,
    get_availabilities,
    db_connect,
    get_product_name,
    get_product,
)
from items import availability_int_to_str
from telegram_message import LegoRestockBot

outputfile = "products_log.txt"

if __name__ == "__main__":

    def append_to_logfile(text: str):
        with open(outputfile, "a") as logfile:
            logfile.write(text)

    config = dotenv_values(".env")

    append_to_logfile(
        "--- Last update {} ---\n".format(
            datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
        )
    )

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

                append_to_logfile(
                    "Product {} {} changed from {} to {}\n".format(
                        product_id, product_name, old_status, new_status
                    )
                )

                if (
                    last_availability == 1 or last_availability == 4
                ):  # 1: Jetzt verfügbar oder 4: Nachbestellungen möglich
                    telegram_bot = LegoRestockBot(
                        config["TELEGRAM_BOT_TOKEN"], config["TELEGRAM_CHANNEL_ID"]
                    )

                    product = get_product(product_id, engine)

                    if last_availability == 1:
                        message = telegram_bot.create_message_available(
                            product_id, product.name, product.url, product.price
                        )
                        telegram_bot.send_html_message_to_channel(message)
                    elif last_availability == 4:
                        message = telegram_bot.create_message_reorder(
                            product_id, product.name, product.url
                        )
                        telegram_bot.send_html_message_to_channel(message)
