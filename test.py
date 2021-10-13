""" This module contains the unit tests for the lego scraping functionalities.
    Tests are implemented for conversions, preprocessors, database operations, telegram operations
"""

import datetime
import unittest
import os
from dotenv import dotenv_values
from sqlalchemy.engine import create_engine
from lego import database
from lego import telegram_message
from lego.items import availability_int_to_str, availability_str_to_int
from lego.telegram_message import LegoRestockBot


class AvailabilityCodeTest(unittest.TestCase):
    """Test the conversions between the availability nums and string representations"""

    def test_str_to_int(self):
        """Test conversion from availability strings to integer representation"""
        self.assertEqual(availability_str_to_int("Jetzt verfügbar"), 1)
        self.assertEqual(availability_str_to_int("Vorübergehend nicht auf Lager"), 2)
        self.assertEqual(availability_str_to_int("Ausverkauft"), 3)

    def test_int_to_str(self):
        """Test conversion from availability integer representation to strings"""
        self.assertEqual(availability_int_to_str(1), "Jetzt verfügbar")
        self.assertEqual(availability_int_to_str(2), "Vorübergehend nicht auf Lager")
        self.assertEqual(availability_int_to_str(3), "Ausverkauft")


class DataBaseTest(unittest.TestCase):
    """Test the database functions"""

    def setUp(self) -> None:
        """Setup a temporary SQLite database with some dummy products"""
        self.database_filename = "test_db.db"
        self.engine = create_engine("sqlite:///" + self.database_filename, echo=True)
        database.Base.metadata.create_all(self.engine)
        try:
            product_1 = database.Product()
            product_1.name = "Product 1"
            product_1.price = 1000
            product_1.url = "url1"
            product_1.product_id = 1
            database.add_product(product_1, self.engine)

            product_2 = database.Product()
            product_2.name = "Product 2"
            product_2.price = 2000
            product_2.url = "url2"
            product_2.product_id = 2
            database.add_product(product_2, self.engine)

            availability1 = database.Availability()
            availability1.availability = 1  # Jetzt verfügbar
            availability1.timestamp = datetime.datetime.now()
            availability1.product_id = 1
            database.add_availability(availability1, self.engine)

        except:  # pylint: disable=bare-except
            self.tearDown()

    def tearDown(self) -> None:
        """Remove the temporary SQLite database"""
        if os.path.exists(self.database_filename):
            os.remove(self.database_filename)

    def test_select_all_products(self):
        """Test selecting all products and check the number of products"""
        products = database.select_all_products(self.engine)
        print(products)
        self.assertEqual(len(products), 2)

    def test_load_product_ids(self):
        """Test selecting all product ids"""
        ids = database.load_product_ids(self.engine)
        self.assertEqual(ids, [1, 2])

    def test_load_product_urls(self):
        """Test selecting the product urls"""
        ids = database.load_product_urls(self.engine)
        self.assertEqual(ids, ["url1", "url2"])

    def test_get_product(self):
        """Test selecting a product name for a given product id"""
        self.assertEqual(database.get_product_name(1, self.engine), "Product 1")
        self.assertEqual(database.get_product_name(2, self.engine), "Product 2")
        # self.assertEqual(database.get_product_name(999), "Unknown product")

    def test_does_product_exist(self):
        """Test does_product_exist function"""
        self.assertEqual(database.does_product_exist(1, self.engine), True)
        self.assertEqual(database.does_product_exist(999, self.engine), False)

    def test_update_product_price(self):
        """Testing update operations for the price in the Products table"""
        product_id = 1000
        product_temp = database.Product()
        product_temp.name = "Product Temp"
        product_temp.price = 1000
        product_temp.url = "url1000"
        product_temp.product_id = product_id
        database.add_product(product_temp, self.engine)

        product_get = database.get_product(product_id, self.engine)
        self.assertEqual(product_get.product_id, product_id)
        self.assertEqual(product_get.price, 1000)

        product_temp_updated = database.Product()
        product_temp_updated.name = "Product Temp"
        product_temp_updated.price = 2000
        product_temp_updated.url = "url1000"
        product_temp_updated.product_id = product_id

        database.update_product_price(product_temp_updated, self.engine)

        product_get_updated = database.get_product(product_id, self.engine)
        self.assertEqual(product_get_updated.product_id, product_id)
        self.assertEqual(product_get_updated.price, 2000)

    def test_delete_old_availibility_entries(self):
        """Test removing old availability entries from the Availability table"""
        availability_count_initial = len(database.get_availabilities(1, self.engine))
        datetime_minimum = datetime.date(2021, 1, 1)

        availability_new = database.Availability()
        availability_new.availability = 1  # Jetzt verfügbar
        availability_new.timestamp = datetime.date(2022, 1, 1)
        availability_new.product_id = 1
        database.add_availability(availability_new, self.engine)

        availability_old = database.Availability()
        availability_old.availability = 1  # Jetzt verfügbar
        availability_old.timestamp = datetime.date(2020, 1, 1)
        availability_old.product_id = 1
        database.add_availability(availability_old, self.engine)

        self.assertEqual(
            availability_count_initial + 2,
            len(database.get_availabilities(1, self.engine)),
        )

        database.delete_old_availability_entries(datetime_minimum, self.engine)

        self.assertEqual(
            availability_count_initial + 1,
            len(database.get_availabilities(1, self.engine)),
        )


class TelegramBotTest(unittest.TestCase):
    """Test sending Telegram messages using the LegoRestockBot class"""

    def setUp(self) -> None:
        """Instantiate the LegoRestockBot class with bot token and channel id"""
        config = dotenv_values(".env")

        self.bot = LegoRestockBot(
            config["TELEGRAM_BOT_TOKEN"], config["TELEGRAM_CHANNEL_ID"]
        )

    def test_send_message(self):
        """Send some dummy messages to the channel"""
        html_message_1 = self.bot.create_message_available(
            60267,
            "Sarafi-Geländewagen",
            "https://www.lego.com/de-de/product/safari-off-roader-60267",
            9999,
        )
        html_message_2 = self.bot.create_message_reorder(
            60267,
            "Sarafi-Geländewagen",
            "https://www.lego.com/de-de/product/safari-off-roader-60267",
        )
        print(html_message_1)
        print(html_message_2)
        # self.bot.send_html_message_to_channel(html_message_1)

    def test_format_price(self):
        """Test the currency formating from cents to a string"""
        self.assertEqual(telegram_message.price_cents_to_str(0), "0,00")
        self.assertEqual(telegram_message.price_cents_to_str(100), "1,00")
        self.assertEqual(telegram_message.price_cents_to_str(222), "2,22")
        self.assertEqual(telegram_message.price_cents_to_str(9999), "99,99")


if __name__ == "__main__":
    unittest.main()
