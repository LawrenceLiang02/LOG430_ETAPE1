"""
Sales model
"""
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Sale(Base):
    """Sales model"""
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
