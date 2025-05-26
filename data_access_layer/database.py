"""Module of the data access layer to connect to the database."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_class.models import Base

# DATABASE_URL = "postgresql://myuser:mypassword@db:5432/mydb"
DATABASE_URL = "sqlite:///./store.db"

# engine = create_engine(DATABASE_URL)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Method to initialize the database"""
    Base.metadata.create_all(engine)
