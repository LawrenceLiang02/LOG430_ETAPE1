"""
Locations model
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()
class Location(Base):
    """
    Locations class model
    """
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}')>"
