"""Location repository module for the data access layer"""
from sqlalchemy import func
from service_layer.database import SessionLocal
from data_class.models import Location


def get_all_locations():
    """Get all locations."""
    session = SessionLocal()
    try:
        return session.query(Location).order_by(Location.name).all()
    finally:
        session.close()

def get_location_by_name(name):
    """Get location by name case sensitive."""

    session = SessionLocal()
    try:
        return session.query(Location).filter(func.lower(Location.name) == name.lower()).first()
    finally:
        session.close()
