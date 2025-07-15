"""
Stock model
"""
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Stock(Base):
    """Stock model"""
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=0)


class StockRequest(Base):
    """Stock request model"""
    __tablename__ = 'stock_requests'
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)

    def __repr__(self):
        return (
            f"<StockRequest(id={self.id}, location_id={self.location_id}, "
            f"product_id={self.product_id}, quantity={self.quantity})>"
        )
