from typing import List
import datetime
from sqlalchemy import create_engine, Column, ForeignKey, func
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, DateTime
from scrapy.utils.project import get_project_settings
from sqlalchemy.orm.session import Session
from sqlalchemy.sql.expression import asc

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column("name", String(256))
    price = Column("price", Integer())
    product_id = Column("product_id", Integer(), unique=True)
    url = Column("url", String(512), unique=True)
    availabilities = relationship("Availability")


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True)
    availability = Column("availability", Integer())
    product_id = Column("product_id", ForeignKey("products.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


def select_all_products(engine: Engine) -> List[Product]:
    with Session(engine) as session:
        products = session.query(Product).all()
    if products is None:
        raise Exception("Products cannot be queried")
    return products


def load_product_urls(engine: Engine) -> List[str]:
    return [p.url for p in select_all_products(engine)]


def load_product_ids(engine: Engine) -> List[int]:
    return [p.product_id for p in select_all_products(engine)]


def get_product_name(product_id_to_search: int, engine: Engine) -> str:
    with Session(engine) as session:
        product_name = (
            session.query(Product.name)
            .filter_by(product_id=product_id_to_search)
            .first()
        )
        if product_name is None:
            raise Exception(
                "Product for ID {} does not exist".format(product_id_to_search)
            )
        return product_name[0]


def does_product_exist(product_id_to_search: int, engine: Engine) -> bool:
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
    with Session(engine) as session:
        product = session.query(Product).filter_by(product_id=product_id).first()
        if product is None:
            raise Exception("Product for ID {} does not exist".format(product_id))
        return product


def add_product(product: Product, engine: Engine):
    with Session(engine) as session:
        session.add(product)
        session.commit()


def update_product_price(product: Product, engine: Engine):
    with Session(engine) as session:
        session.query(Product).filter_by(product_id=product.product_id).update(
            {"price": product.price}
        )
        session.commit()


def add_availability(availability: Availability, engine: Engine):
    with Session(engine) as session:
        session.add(availability)
        session.commit()


def delete_old_availability_entries(min_timestamp: datetime, engine: Engine):
    with Session(engine) as session:
        session.query(Availability).filter(
            Availability.timestamp <= min_timestamp
        ).delete()
        session.commit()
