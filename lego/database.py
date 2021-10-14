# pylint: disable=R0903

""" A collection of functions to work with the Lego products database and SQLalchemy

It includes functions for creating tables, selecting, updating and deleting entries.
Also the tables, columns and relationships of the database are defined
"""

from typing import List
import datetime
from sqlalchemy import (
    create_engine,
    Column,
    ForeignKey,
    func,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import asc
from scrapy.utils.project import get_project_settings


Base = declarative_base()


class Product(Base):
    """Class defining the Product table"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column("name", String(256))
    price = Column("price", Integer())
    product_id = Column("product_id", Integer(), unique=True)
    url = Column("url", String(512), unique=True)
    availabilities = relationship("Availability")


class Availability(Base):
    """Class defining the Availability table"""

    __tablename__ = "availability"

    id = Column(Integer, primary_key=True)
    availability = Column("availability", Integer())
    product_id = Column("product_id", ForeignKey("products.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


def db_connect():
    """Returns sqlalchemy engine instance using the database settings from settings.py"""
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    """Creates all tables if they don't exist yet"""
    Base.metadata.create_all(engine)


def select_all_products(engine: Engine) -> List[Product]:
    """Returns all products from the Product table"""
    with Session(engine) as session:
        products = session.query(Product).all()
    if products is None:
        raise Exception("Products cannot be queried")
    return products


def load_product_urls(engine: Engine) -> List[str]:
    """Returns the list of strings of all product urls"""
    return [p.url for p in select_all_products(engine)]


def load_product_ids(engine: Engine) -> List[int]:
    """Returns the list of int of all lego product ids"""
    return [p.product_id for p in select_all_products(engine)]


def get_product_name(product_id_to_search: int, engine: Engine) -> str:
    """Retrieves the product name from the Product table for a given product id"""
    with Session(engine) as session:
        product_name = (
            session.query(Product.name)
            .filter_by(product_id=product_id_to_search)
            .first()
        )
        if product_name is None:
            raise Exception(f"Product for ID {product_id_to_search} does not exist")
        return product_name[0]


def does_product_exist(product_id_to_search: int, engine: Engine) -> bool:
    """Returns true if the product with the id exists in the Product table"""
    with Session(engine) as session:
        product_name = (
            session.query(Product.name)
            .filter_by(product_id=product_id_to_search)
            .first()
        )
        if product_name is None:
            return False
        return True


def get_availabilities(product_id_to_search: int, engine: Engine):
    """Returns all availability entries for a given lego product id

    Returns a list of dicts of format:
    {
        "timestamp": <timestamp of entry>,
        "availability": <integer code for availability>
    }
    """
    with Session(engine) as session:
        availabilites = (
            session.query(Availability)
            .filter_by(product_id=product_id_to_search)
            .order_by(asc(Availability.timestamp))
            .all()
        )
        ret = [
            {"timestamp": a.timestamp, "availability": a.availability}
            for a in availabilites
        ]
        return ret


def get_product(product_id: int, engine: Engine) -> Product:
    """Returns a Product object from the Product table for a given product id"""
    with Session(engine) as session:
        product = session.query(Product).filter_by(product_id=product_id).first()
        if product is None:
            raise Exception(f"Product for ID {product_id} does not exist")
        return product


def add_product(product: Product, engine: Engine):
    """Add a new Product object to the Product table"""
    with Session(engine) as session:
        session.add(product)
        session.commit()


def update_product_price(product: Product, engine: Engine):
    """Updates the price of a product in the Product table"""
    with Session(engine) as session:
        session.query(Product).filter_by(product_id=product.product_id).update(
            {"price": product.price}
        )
        session.commit()


def add_availability(availability: Availability, engine: Engine):
    """Add a new Availability object to the Availability table"""
    with Session(engine) as session:
        session.add(availability)
        session.commit()


def delete_old_availability_entries(min_timestamp: datetime, engine: Engine):
    """Delete entries from the Availability tablee that are older than min_timestamp"""
    with Session(engine) as session:
        session.query(Availability).filter(
            Availability.timestamp <= min_timestamp
        ).delete()
        session.commit()
