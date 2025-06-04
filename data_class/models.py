"""This moducle contains data classes"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

sale_product = Table(
    'sale_product',
    Base.metadata,
    Column('sale_id', ForeignKey('sales.id'), primary_key=True),
    Column('product_id', ForeignKey('products.id'), primary_key=True)
)

class Product(Base):
    """Global product definition (shared across stores)"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    stocks = relationship("Stock", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"

class Stock(Base):
    """stock model"""
    __tablename__ = 'stocks'

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=0)

    product = relationship("Product", back_populates="stocks")
    location = relationship("Location")

class Sale(Base):
    """A sale model"""
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    product = relationship("Product")
    location = relationship("Location")

class Location(Base):
    """Represents a physical location (store, HQ, logistic center)"""
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}')>"
