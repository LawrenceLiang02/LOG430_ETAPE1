"""Module of the data access layer to connect to the database."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_class.models import Base, Location

# DATABASE_URL = "postgresql://myuser:mypassword@db:5432/mydb"
DATABASE_URL = "sqlite:///./store.db"

# engine = create_engine(DATABASE_URL)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Initialize database and seed initial locations"""
    Base.metadata.create_all(engine)
    session = SessionLocal()

    existing = session.query(Location).count()
    if existing == 0:
        default_locations = [
            Location(name="Maison mère"),
            Location(name="Centre logistique"),
            Location(name="Magasin 1"),
            Location(name="Magasin 2"),
            Location(name="Magasin 3"),
        ]
        session.add_all(default_locations)
        session.commit()
        print("5 default locations added")

    session.close()
