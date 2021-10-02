#!/usr/bin/python3

from database import load_product_ids, get_availabilities, db_connect, get_product_name
from items import availability_int_to_str
import datetime

outputfile = "products_log.txt"

if __name__ == "__main__":

    def append_to_logfile(text: str):
        with open(outputfile, "a") as logfile:
            logfile.write(text)

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

            last_availabilty = availabilites[-1]["availability"]
            n_last_availability = availabilites[-2]["availability"]

            if not last_availabilty == n_last_availability:
                old_status = availability_int_to_str(last_availabilty)
                new_status = availability_int_to_str(n_last_availability)
                product_name = get_product_name(product_id, engine)

                append_to_logfile(
                    "Product {} {} changed from {} to {}\n".format(
                        product_id, product_name, old_status, new_status
                    )
                )
