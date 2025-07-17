"""Models for cart"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class CartItem(Base):
    """Cart item"""
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    user = Column(String, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
