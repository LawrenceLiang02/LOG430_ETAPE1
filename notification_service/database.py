"""
Set up database for notification service
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Notification

DATABASE_URL = "sqlite:///./notification.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """
    Initialise la base de données pour les notifications
    """
    Base.metadata.create_all(engine)
    session = SessionLocal()

    if session.query(Notification).count() == 0:
        print("Notification DB initialized")

    session.close()
