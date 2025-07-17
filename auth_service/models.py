"""
Models for users
"""
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    """user class"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
