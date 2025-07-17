"""
Set up database for location
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Location, Base

DATABASE_URL = "sqlite:///./location.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """
    Initialise db with locations
    """
    Base.metadata.create_all(engine)
    session = SessionLocal()
    if session.query(Location).count() == 0:
        session.add_all([
            Location(name="Maison mère"),
            Location(name="Centre logistique"),
            Location(name="Magasin 1"),
            Location(name="Magasin 2"),
            Location(name="Magasin 3"),
        ])
        session.commit()
        print("Default locations added")
    session.close()
