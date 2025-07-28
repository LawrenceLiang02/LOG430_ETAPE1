"""Sale module for the data access layer"""
import requests
from models import Sale
from database import SessionLocal

LOCATION_SVC = "http://location_service_1:5000"
PRODUCT_SVC  = "http://product_service_1:5000"
STOCK_SVC    = "http://stock_service_1:5000"

def _auth_headers(auth_header: str | None):
    """get auth header"""
    return {"Authorization": auth_header} if auth_header else {}

def get_location_by_name_from_api(name, auth_header=None):
    """get location by name"""
    try:
        r = requests.get(f"{LOCATION_SVC}/api/locations/{name}",
                         headers=_auth_headers(auth_header), timeout=3)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None

def get_location_by_id_from_api(location_id, auth_header=None):
    """get location by id from api  """
    try:
        r = requests.get(f"{LOCATION_SVC}/api/locations/id/{location_id}",
                         headers=_auth_headers(auth_header), timeout=3)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None

def get_product_from_api(product_id, auth_header=None):
    """get product from api"""
    try:
        r = requests.get(f"{PRODUCT_SVC}/api/products/get/{product_id}",
                         headers=_auth_headers(auth_header), timeout=3)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None

def get_stock_from_api(product_id, location_id, auth_header=None):
    """get stock from api"""
    try:
        r = requests.get(f"{STOCK_SVC}/api/stocks/check",
                         params={"product_id": product_id, "location_id": location_id},
                         headers=_auth_headers(auth_header), timeout=3)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        return None

def deduct_stock(product_id, location_id, quantity, auth_header=None):
    """deduct stock"""
    try:
        r = requests.post(f"{STOCK_SVC}/api/stocks/deduct",
                          json={"product_id": product_id, "location_id": location_id, "quantity": quantity},
                          headers=_auth_headers(auth_header), timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False

def record_sale_only(product_id, location_name, quantity, auth_header=None):
    """
    Record a sale without stock operations (cart already deducted).
    """
    session = SessionLocal()
    try:
        product = get_product_from_api(product_id, auth_header)
        if not product:
            return False, "Produit introuvable."

        location_data = get_location_by_name_from_api(location_name, auth_header)
        if not location_data:
            return False, "Emplacement introuvable."

        sale = Sale(
            product_id=product_id,
            location_id=location_data["id"],
            quantity=quantity
        )
        session.add(sale)
        session.commit()
        return True, "OK"
    except Exception as e:
        session.rollback()
        return False, f"Erreur lors de l'enregistrement de la vente : {e}"
    finally:
        session.close()

def add_sale_with_deduct(product_id, location_name, quantity, auth_header=None):
    """
    Direct sale: check + deduct stock, then record. (Old behavior)
    """
    session = SessionLocal()
    try:
        product = get_product_from_api(product_id, auth_header)
        if not product:
            return False, "Produit introuvable."

        location_data = get_location_by_name_from_api(location_name, auth_header)
        if not location_data:
            return False, "Emplacement introuvable."

        stock_info = get_stock_from_api(product_id, location_data["id"], auth_header)
        if not stock_info:
            return False, "Erreur lors de la vérification du stock."

        if stock_info["quantity"] < quantity:
            return False, f"Stock insuffisant ({stock_info['quantity']} disponibles)."

        if not deduct_stock(product_id, location_data["id"], quantity, auth_header):
            return False, "Échec de la déduction de stock."

        sale = Sale(
            product_id=product_id,
            location_id=location_data["id"],
            quantity=quantity
        )
        session.add(sale)
        session.commit()
        return True, "OK"

    except Exception as e:
        session.rollback()
        return False, f"Erreur lors de l'enregistrement de la vente : {e}"
    finally:
        session.close()

def get_sales_by_location(location_id: int, page=1, size=10, sort_field="id", sort_order="asc", auth_header=None):
    """
    Return (items, total) with items enriched from product and location services.
    """
    session = SessionLocal()
    try:
        query = session.query(Sale).filter(Sale.location_id == location_id)

        sort_column = getattr(Sale, sort_field, Sale.id)
        query = query.order_by(sort_column.desc() if sort_order.lower() == "desc" else sort_column.asc())

        total = query.count()
        rows = query.offset((page - 1) * size).limit(size).all()

        location_data = get_location_by_id_from_api(location_id, auth_header)
        location_name = location_data.get("name", "Inconnu") if location_data else "Inconnu"

        items = []
        for s in rows:
            product_data = get_product_from_api(s.product_id, auth_header) or {}
            unit_price = product_data.get("price", 0.0)
            items.append({
                "id": s.id,
                "location": location_name,
                "product": product_data.get("name", "Produit inconnu"),
                "quantity": s.quantity,
                "unit_price": unit_price,
                "total": unit_price * s.quantity
            })

        return items, total
    finally:
        session.close()

def cancel_sale(sale_id, auth_header=None):
    """cancel sale"""
    session = SessionLocal()
    try:
        sale = session.get(Sale, sale_id)
        if not sale:
            raise ValueError("Sale not found")

        product_id = sale.product_id
        location_data = get_location_by_name_from_api(sale.location_id, auth_header)
        location_name = location_data.get("name", "Inconnu")

        # Restore stock
        try:
            r = requests.post(
                f"{STOCK_SVC}/api/stocks",
                json={"location": location_name, "product_id": product_id, "quantity": sale.quantity},
                headers=_auth_headers(auth_header),
                timeout=3
            )
            r.raise_for_status()
        except requests.RequestException:
            return False

        session.delete(sale)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()
