from datetime import datetime
import unittest
import os
from sqlalchemy.engine import create_engine
from lego import database
from lego import telegram_message
from lego.items import availability_int_to_str, availability_str_to_int
from lego.telegram_message import LegoRestockBot


class AvailabilityCodeTest(unittest.TestCase):
    def test_str_to_int(self):
        self.assertEqual(availability_str_to_int("Jetzt verfügbar"), 1)
        self.assertEqual(availability_str_to_int("Vorübergehend nicht auf Lager"), 2)
        self.assertEqual(availability_str_to_int("Ausverkauft"), 3)

    def test_int_to_str(self):
        self.assertEqual(availability_int_to_str(1), "Jetzt verfügbar")
        self.assertEqual(availability_int_to_str(2), "Vorübergehend nicht auf Lager")
        self.assertEqual(availability_int_to_str(3), "Ausverkauft")


class DataBaseTest(unittest.TestCase):
    def setUp(self) -> None:
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
            availability1.timestamp = datetime.now()
            database.add_availability(availability1, self.engine)

        except:
            self.tearDown()

    def tearDown(self) -> None:
        if os.path.exists(self.database_filename):
            os.remove(self.database_filename)

    def test_select_all_products(self):
        products = database.select_all_products(self.engine)
        print(products)
        self.assertEqual(len(products), 2)

    def test_load_product_ids(self):
        ids = database.load_product_ids(self.engine)
        self.assertEqual(ids, [1, 2])

    def test_load_product_urls(self):
        ids = database.load_product_urls(self.engine)
        self.assertEqual(ids, ["url1", "url2"])

    def test_get_product(self):
        self.assertEqual(database.get_product_name(1, self.engine), "Product 1")
        self.assertEqual(database.get_product_name(2, self.engine), "Product 2")
        # self.assertEqual(database.get_product_name(999), "Unknown product")

    def test_does_product_exist(self):
        self.assertEqual(database.does_product_exist(1, self.engine), True)
        self.assertEqual(database.does_product_exist(999, self.engine), False)

    def test_update_product_price(self):
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


class TelegramBotTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = LegoRestockBot("", "")

    def test_send_message(self):
        html_message = self.bot.create_message_available(
            60267,
            "Sarafi-Geländewagen",
            "https://www.lego.com/de-de/product/safari-off-roader-60267",
            9999,
        )
        html_message = self.bot.create_message_reorder(
            60267,
            "Sarafi-Geländewagen",
            "https://www.lego.com/de-de/product/safari-off-roader-60267",
        )
        self.bot.send_html_message_to_channel(html_message)

    def test_format_price(self):
        self.assertEqual(telegram_message.price_cents_to_str(0), "0,00")
        self.assertEqual(telegram_message.price_cents_to_str(100), "1,00")
        self.assertEqual(telegram_message.price_cents_to_str(222), "2,22")
        self.assertEqual(telegram_message.price_cents_to_str(9999), "99,99")


if __name__ == "__main__":
    unittest.main()
