# pylint: disable=R0903
"""Scrapy pipelines for

- LegoPipeline: Adds new lego products to the database
- DuplicatesPipelines: Drop items that already exist in the database
- UpdatePricePipeline: Update the price of a lego product in the database
- AvailabilityPipeline: Add an entry about the availability of a product to the database

Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
"""

from scrapy.exceptions import DropItem
from lego.items import LegoItem
from lego.database import (
    add_availability,
    add_product,
    create_table,
    db_connect,
    Product,
    Availability,
    does_product_exist,
    update_product_price,
)


class AvailabilityPipeline:
    """Pipeline for adding an availability entry for a product to the database"""

    def __init__(self) -> None:
        """Create tables if they don't exist yet"""
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem):
        """Pipeline process function.
        Drops the item if product does not exist in the database.
        Adds an entry to the Availability table for the product
        """
        if not does_product_exist(item["product_id"], self.engine):
            raise DropItem(f"Product does not exist in database: {item['name']}")

        availability = Availability()
        availability.product_id = item["product_id"]
        availability.availability = item["availability"]
        add_availability(availability, self.engine)
        return item


class UpdatePricePipeline:
    """Pipeline for updating the price of a lego product in the database"""

    def __init__(self) -> None:
        """Create tables if they don't exist yet"""
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem):
        """Pipeline process function.
        Drops the item if product does not exist in the database.
        Updates the price of the product in the Product table
        """
        if not does_product_exist(item["product_id"], self.engine):
            raise DropItem(f"Product does not exist in database: {item['name']}")

        product = Product()
        product.name = item["name"]
        product.price = item["price"]
        product.product_id = item["product_id"]
        product.url = item["url"]
        update_product_price(product, self.engine)
        return item


class LegoPipeline:
    """Pipeline for adding new lego products to the database"""

    def __init__(self) -> None:
        """Create tables if they don't exist yet"""
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem):
        """Pipeline process function.
        Save products in the database
        """
        product = Product()
        product.name = item["name"]
        product.price = item["price"]
        product.product_id = item["product_id"]
        product.url = item["url"]
        add_product(product, self.engine)
        return item


class DuplicatesPipeline:
    """Pipeline for dropping duplicate lego products"""

    def __init__(self):
        """Create tables if they don't exist yet"""
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem):
        """Pipeline process function.
        Drop items that already exist in the database
        """
        if does_product_exist(item["product_id"], self.engine):
            raise DropItem(f"Duplicate item found: {item['name']}")
        return item
