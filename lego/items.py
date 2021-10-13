"""Models definition for scraped items

See documentation in:
https://docs.scrapy.org/en/latest/topics/items.html
"""

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def process_price(price_text: str) -> int:
    """Convert the incoming price string to an integer in cents
    Example:
        in: 19,99\xa0€
        out: 1999
    """
    try:
        splitted = price_text.split("\xa0")
        price = float(splitted[0].replace(",", "."))
        price = int(price * 100)
        return price
    except:  # pylint: disable=bare-except
        return 0


def str_to_int(text: str) -> int:
    """Convert a string to int"""
    try:
        i = int(text)
        return i
    except:  # pylint: disable=bare-except
        return text


AVAILABILITY_CODES = {
    1: "Jetzt verfügbar",
    2: "Vorübergehend nicht auf Lager",
    3: "Ausverkauft",
    # Example: "Nachbestellungen möglich. Versand zum 12. Oktober 2021"
    4: "Nachbestellungen möglich",
    -1: "Unknown",
}


def availability_str_to_int(text: str) -> int:
    """Lookup the corresponding availability status int code for the string"""
    for key, value in AVAILABILITY_CODES.items():
        if value == text:
            return key
        if (
            key == 4 and AVAILABILITY_CODES[4] in text
        ):  # special case. Text contains "Nachbestellungen möglich"
            return key
    raise Exception(f"Verfügbarkeitsstatus {text} unkown")


def availability_int_to_str(availability: int) -> str:
    """Lookup the corresponding availability string for the int code"""
    return AVAILABILITY_CODES[availability]


class LegoItem(scrapy.Item):
    """Model for a Lego scrapy Item

    Fields:
        - name
        - price: in cents
        - product_id: Lego product ID
        - availability: integer representing the availability status
        - url: url to lego product page
    """

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
