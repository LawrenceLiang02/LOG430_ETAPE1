"""Stock module for the data access layer"""
import requests
from database import SessionLocal
from models import Stock, StockRequest
from urllib.parse import quote

def _auth_headers(auth_header: str | None):
    print("Token", auth_header)
    if not auth_header:
        return {}
    if not auth_header.lower().startswith("bearer "):
        auth_header = f"Bearer {auth_header}"
    return {"Authorization": auth_header}

def get_location_by_name_from_api(name, auth_header=None):
    try:
        headers = _auth_headers(auth_header)
        response = requests.get(
            f"http://localhost:8001/api/locations/{quote(name)}",
            headers=headers,
            timeout=3
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_location_by_id_from_api(location_id, auth_header=None):
    try:
        headers = _auth_headers(auth_header)
        response = requests.get(
            f"http://localhost:8001/api/locations/id/{location_id}",
            headers=headers,
            timeout=3
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_product_by_id_from_api(product_id, auth_header=None):
    try:
        headers = _auth_headers(auth_header)
        response = requests.get(
            f"http://localhost:8002/api/products/get/{product_id}",
            headers=headers,
            timeout=3
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def add_stock(product_id: int, location_id: int, quantity: int, auth_header=None):
    """Add stock directly to a location without checking Centre logistique."""
    session = SessionLocal()
    try:
        # Check that location exists
        location_data = get_location_by_id_from_api(location_id, auth_header)
        if not location_data:
            print(f"Location ID {location_id} inconnue.")
            return False

        # Add stock to the location
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
        print(f"{quantity} unités ajoutées à {location_data['name']}.")
        return True

    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'ajout de stock : {e}")
        return False
    finally:
        session.close()

def get_stock(location_id, auth_header=None):
    """
    Récupère les niveaux de stock pour une location spécifique en appelant
    les services product et location.
    """
    session = SessionLocal()
    stocks_list = []

    try:
        stocks = session.query(Stock).filter_by(location_id=location_id).all()

        location_data = get_location_by_id_from_api(location_id, auth_header)
        location_name = location_data.get("name", "Inconnu") if location_data else "Inconnu"

        for s in stocks:
            product_data = get_product_by_id_from_api(s.product_id, auth_header)
            product_name = product_data.get("name", "Produit inconnu") if product_data else "Produit inconnu"

            stocks_list.append({
                "product_id": s.product_id,
                "product_name": product_name,
                "quantity": s.quantity,
                "location": location_name
            })

        return stocks_list

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

def get_all_stock_requests(auth_header=None):
    """Retourne toutes les demandes de stock avec infos produits et locations via API."""
    session = SessionLocal()
    try:
        requests = session.query(StockRequest).all()
        result = []
        for r in requests:
            product_data = get_product_by_id_from_api(r.product_id, auth_header)
            location_data = get_location_by_id_from_api(r.location_id, auth_header)
            result.append({
                "id": r.id,
                "location": location_data.get("name", "Inconnu") if location_data else "Inconnu",
                "product": product_data.get("name", "Produit inconnu") if product_data else "Produit inconnu",
                "quantity": r.quantity
            })
        return result
    finally:
        session.close()


def fulfill_stock_request(request_id, auth_header=None):
    """Execute une demande de réapprovisionnement avec API calls."""
    session = SessionLocal()
    try:
        request = session.query(StockRequest).get(request_id)
        if not request:
            return False, "Demande introuvable."

        product_id = request.product_id
        destination_id = request.location_id
        quantity = request.quantity

        centre_data = get_location_by_name_from_api("Centre logistique", auth_header)
        if not centre_data:
            return False, "Centre Logistique introuvable via API."
        centre_id = centre_data["id"]

        source_stock = session.query(Stock).filter_by(
            location_id=centre_id,
            product_id=product_id
        ).first()

        if not source_stock or source_stock.quantity < quantity:
            return False, (
                f"Stock insuffisant au Centre Logistique "
                f"({source_stock.quantity if source_stock else 0})."
            )

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

        product_data = get_product_by_id_from_api(product_id, auth_header) or {"name": "Produit inconnu"}
        destination_data = get_location_by_id_from_api(destination_id, auth_header) or {"name": "Destination inconnue"}

        return True, f"{quantity} unités de {product_data['name']} envoyées à {destination_data['name']}."
    except Exception as e:
        session.rollback()
        return False, f"Erreur lors de l’exécution : {e}"
    finally:
        session.close()

def get_stock_by_ids(product_id, location_id, auth_header=None):
    """Retourne un stock spécifique avec infos produits et location."""
    session = SessionLocal()
    try:
        stock = session.query(Stock).filter_by(
            product_id=product_id,
            location_id=location_id
        ).first()

        if not stock:
            return None

        product_data = get_product_by_id_from_api(product_id, auth_header)
        location_data = get_location_by_id_from_api(location_id, auth_header)

        return {
            "product_id": product_id,
            "product_name": product_data.get("name", "Produit inconnu") if product_data else "Produit inconnu",
            "quantity": stock.quantity,
            "location": location_data.get("name", "Inconnu") if location_data else "Inconnu"
        }
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
