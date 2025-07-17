"""Database for cart"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "sqlite:///cart.db"  # ou PostgreSQL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Method pour initialiser la base de donnee"""
    Base.metadata.create_all(bind=engine)
