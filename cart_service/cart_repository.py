"""Cart repository and business logic"""
import requests
from database import SessionLocal
from models import CartItem

LOCATION_SVC = "http://location_service_1:5000"
STOCK_SVC    = "http://stock_service_1:5000"
SALE_SVC     = "http://sale_service_1:5000"

def _auth_headers(auth_header: str | None):
    """Check auth header"""
    return {"Authorization": auth_header} if auth_header else {}

def _get_location_id(location_name: str, auth_header=None) -> int:
    """get location by id"""
    resp = requests.get(
        f"{LOCATION_SVC}/api/locations/{location_name}",
        headers=_auth_headers(auth_header),
        timeout=3
    )
    resp.raise_for_status()
    return resp.json()["id"]

def _check_stock(product_id: int, location_id: int, auth_header=None) -> int:
    """check stock"""
    resp = requests.get(
        f"{STOCK_SVC}/api/stocks/check",
        params={"product_id": product_id, "location_id": location_id},
        headers=_auth_headers(auth_header),
        timeout=3
    )
    resp.raise_for_status()
    return resp.json()["quantity"]

def _deduct_stock(product_id: int, location_id: int, quantity: int, auth_header=None):
    """deduct stock"""
    resp = requests.post(
        f"{STOCK_SVC}/api/stocks/deduct",
        json={"product_id": product_id, "location_id": location_id, "quantity": quantity},
        headers=_auth_headers(auth_header),
        timeout=3
    )
    resp.raise_for_status()

def _add_back_stock(location_name: str, product_id: int, quantity: int, auth_header=None):
    """add back stock"""
    resp = requests.post(
        f"{STOCK_SVC}/api/stocks",
        json={"location": location_name, "product_id": product_id, "quantity": quantity},
        headers=_auth_headers(auth_header),
        timeout=3
    )
    resp.raise_for_status()

def _create_sale(location: str, product_id: int, quantity: int, auth_header=None):
    """create sale"""
    resp = requests.post(
        f"{SALE_SVC}/api/sale",
        json={"location": location, "product_id": product_id, "quantity": quantity},
        headers=_auth_headers(auth_header),
        timeout=3
    )
    return resp.status_code, resp.text

def add_item_to_cart(user, product_id, quantity, location):
    """add item to cart"""
    session = SessionLocal()
    try:
        item = CartItem(user=user, product_id=product_id, quantity=quantity, location=location)
        session.add(item)
        session.flush()
        item_id = item.id
        session.commit()
        return item_id
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_cart(user):
    """get cart"""
    session = SessionLocal()
    try:
        items = session.query(CartItem).filter_by(user=user).all()
        return [
            {"id": i.id, "product_id": i.product_id, "quantity": i.quantity, "location": i.location}
            for i in items
        ]
    finally:
        session.close()

def clear_cart(user):
    """clear cart"""
    session = SessionLocal()
    try:
        session.query(CartItem).filter_by(user=user).delete()
        session.commit()
    finally:
        session.close()

def add_to_cart(user, product_id, quantity, location, auth_header):
    """add item to cart"""
    try:
        location_id = _get_location_id(location, auth_header)
        available = _check_stock(product_id, location_id, auth_header)
        if available < quantity:
            return {"message": f"Stock insuffisant ({available} disponibles)."}, 409

        _deduct_stock(product_id, location_id, quantity, auth_header)
        item_id = add_item_to_cart(user, product_id, quantity, location)
        return {"message": "Ajouté au panier (stock réservé/déduit)", "id": item_id}, 201
    except requests.HTTPError as e:
        return {"message": f"Erreur API: {e}"}, 502
    except Exception as e:
        return {"message": f"Erreur interne: {e}"}, 500

def checkout_cart(user, auth_header):
    """checkout a cart"""
    cart = get_cart(user)
    if not cart:
        return {"message": "Panier vide"}, 400

    errors = []
    for item in cart:
        code, text = _create_sale(item["location"], item["product_id"], item["quantity"], auth_header)
        if code != 201:
            errors.append(f"Échec vente produit {item['product_id']}: {text}")

    clear_cart(user)
    if errors:
        return {"message": "Commande partiellement validée", "errors": errors}, 207
    return {"message": "Commande validée avec succès"}, 200

def cancel_cart(user, auth_header):
    """cancel a cart"""
    cart = get_cart(user)
    if not cart:
        return {"message": "Panier vide"}, 400

    errors = []
    for item in cart:
        try:
            _add_back_stock(item["location"], item["product_id"], item["quantity"], auth_header)
        except Exception as e:
            errors.append(f"Échec retour stock produit {item['product_id']}: {e}")

    clear_cart(user)
    if errors:
        return {"message": "Annulation partielle", "errors": errors}, 207
    return {"message": "Panier annulé et stock restauré"}, 200
