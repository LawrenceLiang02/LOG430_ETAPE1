"""Location repository module for the data access layer"""
from service_layer.database import SessionLocal
from data_class.models import Location


def get_all_locations():
    """Récupère toutes les locations depuis la base de données."""
    session = SessionLocal()
    try:
        return session.query(Location).order_by(Location.name).all()
    finally:
        session.close()
