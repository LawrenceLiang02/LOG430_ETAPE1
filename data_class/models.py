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
    """This is the data model for a product"""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, quantity={self.quantity})>"   

class Sale(Base):
    """This is the data model for a sale"""
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)

    product = relationship("Product")

    def __repr__(self):
        return f"<Sale(product={self.product.name}, quantity={self.quantity})>"