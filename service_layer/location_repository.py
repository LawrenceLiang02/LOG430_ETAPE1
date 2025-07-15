"""Location repository module for the data access layer"""
import logging
from sqlalchemy import func
from service_layer.database import SessionLocal
from data_class.models import Location

logger = logging.getLogger(__name__)

def get_all_locations():
    """Get all locations."""
    session = SessionLocal()
    try:
        logger.info("Fetching all locations from DB")
        return session.query(Location).order_by(Location.name).all()
    except Exception as e:
        logger.error("Erreur lors de la récupération des locations: %s", e)
        raise
    finally:
        session.close()

def get_location_by_name(name):
    """Get location by name (case-insensitive)"""
    session = SessionLocal()
    try:
        logger.info("Recherche de l'emplacement avec le nom: %s", name)
        result = session.query(Location).filter(func.lower(Location.name) == name.lower()).first()
        if not result:
            logger.warning("Aucun emplacement trouvé pour: %s", name)
        return result
    except Exception as e:
        logger.error("Erreur lors de la recherche de l'emplacement %s: %s", name, e)
        raise
    finally:
        session.close()
