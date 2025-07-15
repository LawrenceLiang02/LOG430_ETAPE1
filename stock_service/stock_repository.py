"""Stock module for the data access layer"""
import requests
from sqlalchemy.orm import joinedload
from database import SessionLocal
from models import Stock, StockRequest

def get_location_by_name_from_api(name):
    """Method to get location"""
    try:
        response = requests.get(f"http://localhost:8001/api/locations/{name}", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_product_by_id_from_api(product_id):
    """Method to get product"""
    try:
        response = requests.get(f"http://localhost:8002/api/products/{product_id}", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def add_stock(product_id: int, location_id: int, quantity: int):
    """
    Ajoute du stock à une localisation.
    - Si la localisation est "Centre logistique" → approvisionner
    - Sinon → déduire du stock du centre logistique
    """
    session = SessionLocal()
    try:
        location_data = get_location_by_id_from_api(location_id)
        if not location_data:
            print("Location inconnue.")
            return False

        is_logistic = location_data["name"].lower() == "centre logistique"

        if is_logistic:
            # Ajoute du stock directement dans le centre logistique
            stock = session.query(Stock).filter_by(
                product_id=product_id,
                location_id=location_id
            ).first()

            if stock:
                stock.quantity += quantity
            else:
                stock = Stock(
                    product_id=product_id,
                    location_id=location_id,
                    quantity=quantity
                )
                session.add(stock)

            session.commit()
            print(f"{quantity} unités ajoutées au centre logistique.")
            return True

        logistic_location = get_location_by_name_from_api("Centre logistique")
        if not logistic_location:
            print("Centre logistique introuvable.")
            return False

        logistic_id = logistic_location["id"]

        logistic_stock = session.query(Stock).filter_by(
            product_id=product_id,
            location_id=logistic_id
        ).first()

        if not logistic_stock or logistic_stock.quantity < quantity:
            print(f"Stock insuffisant au centre logistique ({logistic_stock.quantity if logistic_stock else 0}).")
            return False

        logistic_stock.quantity -= quantity

        target_stock = session.query(Stock).filter_by(
            product_id=product_id,
            location_id=location_id
        ).first()

        if target_stock:
            target_stock.quantity += quantity
        else:
            target_stock = Stock(
                product_id=product_id,
                location_id=location_id,
                quantity=quantity
            )
            session.add(target_stock)

        session.commit()
        print(f"{quantity} unités transférées du centre logistique vers {location_data['name']}")
        return True

    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'ajout de stock : {e}")
        return False
    finally:
        session.close()

def get_stock(location):
    """
    Récupère les niveaux de stock pour une location spécifique."""
    session = SessionLocal()
    try:
        stocks = session.query(Stock).options(
            joinedload(Stock.product),
            joinedload(Stock.location)
        ).filter_by(location_id=location.id).all()
        return stocks
    finally:
        session.close()

def create_stock_request(location_id, product_id, quantity):
    """Create and save a stock request in the database"""
    try:
        session = SessionLocal()
        request = StockRequest(
            location_id=location_id,
            product_id=product_id,
            quantity=quantity
        )
        session.add(request)
        session.commit()
        session.close()
        return True
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def get_all_stock_requests():
    """Retourne toutes les demandes de stock avec leurs relations chargées"""
    session = SessionLocal()
    requests = session.query(StockRequest).options(
        joinedload(StockRequest.product),
        joinedload(StockRequest.location)
    ).all()
    session.close()
    return requests

def fulfill_stock_request(request_id):
    """Execute une demande de réapprovisionnement"""
    session = SessionLocal()

    try:
        request = session.query(StockRequest).get(request_id)
        if not request:
            return False, "Demande introuvable."

        product_id = request.product_id
        destination_id = request.location_id
        quantity = request.quantity

        centre_data = get_location_by_name_from_api("Centre logistique")
        if not centre_data:
            return False, "Centre Logistique introuvable via API."

        centre_id = centre_data["id"]

        source_stock = session.query(Stock).filter_by(
            location_id=centre_id,
            product_id=product_id
        ).first()

        if not source_stock or source_stock.quantity < quantity:
            return False, f"Stock insuffisant au Centre Logistique ({source_stock.quantity if source_stock else 0})."

        source_stock.quantity -= quantity

        dest_stock = session.query(Stock).filter_by(
            location_id=destination_id,
            product_id=product_id
        ).first()

        if dest_stock:
            dest_stock.quantity += quantity
        else:
            dest_stock = Stock(
                location_id=destination_id,
                product_id=product_id,
                quantity=quantity
            )
            session.add(dest_stock)

        session.delete(request)
        session.commit()

        product_data = get_product_by_id_from_api(product_id) or {"name": "Produit inconnu"}
        destination_data = get_location_by_name_from_api(destination_id) or {"name": "Destination inconnue"}

        return True, (
            f"{quantity} unités de {product_data['name']} envoyées à "
            f"{destination_data['name']}."
        )

    except Exception as e:
        session.rollback()
        return False, f"Erreur lors de l’exécution : {e}"
    finally:
        session.close()
    
def get_location_by_id_from_api(location_id):
    """Get locations by id"""
    try:
        response = requests.get(f"http://localhost:8001/api/locations/id/{location_id}", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_stock_by_ids(product_id, location_id):
    """Retourne un stock spécifique pour un produit à un endroit"""
    session = SessionLocal()
    try:
        return session.query(Stock).options(
            joinedload(Stock.product),
            joinedload(Stock.location)
        ).filter_by(
            product_id=product_id,
            location_id=location_id
        ).first()
    finally:
        session.close()

def deduct_stock_quantity(product_id, location_id, quantity):
    """Décrémente la quantité de stock pour un produit à un emplacement"""
    session = SessionLocal()
    try:
        stock = session.query(Stock).filter_by(
            product_id=product_id,
            location_id=location_id
        ).first()

        if not stock:
            return False, "Stock introuvable."

        if stock.quantity < quantity:
            return False, "Stock insuffisant."

        stock.quantity -= quantity
        session.commit()
        return True, f"{quantity} unités déduites."
    except Exception as e:
        session.rollback()
        return False, f"Erreur lors de la déduction : {e}"
    finally:
        session.close()
