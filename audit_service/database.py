"""
Set up database for audit service
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import AuditLog, Base

DATABASE_URL = "sqlite:///./audit.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """
    Initialize the database (create table if not exists)
    """
    Base.metadata.create_all(engine)
    print("Audit DB initialized.")
