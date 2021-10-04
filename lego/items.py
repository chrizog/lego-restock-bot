# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def process_price(price_text: str) -> int:
    # 19,99\xa0€ -> 19.99
    # return the price in cents as an integer
    try:
        splitted = price_text.split(u"\xa0")
        price = float(splitted[0].replace(",", "."))
        price = int(price * 100)
        return price
    except:
        return 0


def str_to_int(text: str) -> int:
    try:
        i = int(text)
        return i
    except:
        return text


AVAILABILITY_CODES = {
    1: "Jetzt verfügbar",
    2: "Vorübergehend nicht auf Lager",
    3: "Ausverkauft",
    4: "Nachbestellungen möglich",  # Example: "Nachbestellungen möglich. Versand zum 12. Oktober 2021"
    -1: "Unknown",
}


def availability_str_to_int(text: str) -> int:
    for k, v in AVAILABILITY_CODES.items():
        if v == text:
            return k
        elif (
            k == 4 and AVAILABILITY_CODES[4] in text
        ):  # special case. Text contains "Nachbestellungen möglich"
            return k
    raise Exception("Verfügbarkeitsstatus {} unkown".format(text))


def availability_int_to_str(a: int) -> str:
    return AVAILABILITY_CODES[a]


class LegoItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(
        input_processor=MapCompose(process_price), output_processor=TakeFirst()
    )
    product_id = scrapy.Field(
        input_processor=MapCompose(str_to_int), output_processor=TakeFirst()
    )
    availability = scrapy.Field(
        input_processor=MapCompose(availability_str_to_int),
        output_processor=TakeFirst(),
    )
    url = scrapy.Field(output_processor=TakeFirst())
