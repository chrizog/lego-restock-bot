# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
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
    def __init__(self) -> None:
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem, spider):
        # the current product does not exist
        if not does_product_exist(item["product_id"], self.engine):
            raise DropItem("Product does not exist in database: %s" % item["name"])

        availability = Availability()
        availability.product_id = item["product_id"]
        availability.availability = item["availability"]
        try:
            add_availability(availability, self.engine)
        except:
            raise
        return item


class UpdatePricePipeline:
    def __init__(self) -> None:
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem):
        # the current product does not exist
        if not does_product_exist(item["product_id"], self.engine):
            raise DropItem(f"Product does not exist in database: {item['name']}")

        product = Product()
        product.name = item["name"]
        product.price = item["price"]
        product.product_id = item["product_id"]
        product.url = item["url"]
        try:
            update_product_price(product, self.engine)
        except:
            raise
        return item


class LegoPipeline:
    def __init__(self) -> None:
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem):
        """Save products in the database
        This method is called for every item pipeline component
        """
        product = Product()
        product.name = item["name"]
        product.price = item["price"]
        product.product_id = item["product_id"]
        product.url = item["url"]
        try:
            add_product(product, self.engine)
        except:
            raise
        return item


class DuplicatesPipeline:
    def __init__(self):
        """
        Create tables if they don't exist yet
        """
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem, spider):
        if does_product_exist(item["product_id"], self.engine):
            raise DropItem("Duplicate item found: %s" % item["name"])
        return item
