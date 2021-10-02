from datetime import datetime
import unittest
import os
from sqlalchemy.engine import create_engine
from lego import database
from lego.items import availability_int_to_str, availability_str_to_int

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
      availability1.availability = 1 # Jetzt verfügbar
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


if __name__ == "__main__":
  unittest.main()