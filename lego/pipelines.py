# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from typing import List
from lego.items import LegoItem
from lego.database import (
    add_availability,
    add_product,
    create_table,
    db_connect,
    Product,
    Availability,
    does_product_exist,
)
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import and_, func
from scrapy.exceptions import DropItem
from datetime import date


class AvailabilityDuplicatePipeline:
    def __init__(self) -> None:
        engine = db_connect()
        create_table(engine)
        self.session = sessionmaker(bind=engine)

    def process_item(self, item: LegoItem, spider):
        session: Session = self.session()
        exist_product: Product = (
            session.query(Product).filter_by(product_id=item["product_id"]).first()
        )
        session.close()
        if exist_product is None:  # the current product does not exist
            raise DropItem("Product does not exist in database: %s" % item["name"])
        else:
            session: Session = self.session()
            exist_availability: List[Availability] = (
                session.query(Availability)
                .filter(
                    and_(
                        func.date(Availability.timestamp) == date.today(),
                        Availability.product_id == exist_product.product_id,
                    )
                )
                .all()
            )
            session.close()
            if len(exist_availability) < 1:
                # there is no data for today yet
                print("!!!! No data yet for: " + item["name"] + " !!!!")
                return item
            else:
                raise DropItem("There is already a sample for today: %s" % item["name"])


class AvailabilityPipeline:
    def __init__(self) -> None:
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem, spider):
        # the current product does not exist
        if not does_product_exist(item["product_id"], self.engine):
            raise DropItem("Product does not exist in database: %s" % item["name"])
        else:
            availability = Availability()
            availability.product_id = item["product_id"]
            availability.availability = item["availability"]
            try:
                add_availability(availability, self.engine)
            except:
                raise
            return item


class LegoPipeline:
    def __init__(self) -> None:
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem, spider):
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


class DuplicatesPipeline(object):
    def __init__(self):
        """
        Create tables if they don't exist yet
        """
        self.engine = db_connect()
        create_table(self.engine)

    def process_item(self, item: LegoItem, spider):
        if does_product_exist(item["product_id"], self.engine):
            raise DropItem("Duplicate item found: %s" % item["name"])
        else:
            return item
