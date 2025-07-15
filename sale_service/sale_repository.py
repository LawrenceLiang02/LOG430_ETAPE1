"""Sale module for the data access layer"""
import requests
from sqlalchemy.orm import joinedload
from models import Sale
from database import SessionLocal

def get_product_from_api(product_id):
    """Get product request"""
    try:
        response = requests.get(f"http://localhost:8002/api/products/{product_id}", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def get_stock_from_api(product_id, location_id):
    """Check stock availability from stock_service"""
    try:
        response = requests.get(
            f"http://localhost:8003/api/stocks/check",
            params={"product_id": product_id, "location_id": location_id},
            timeout=3
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

def deduct_stock(product_id, location_id, quantity):
    try:
        response = requests.post(
            "http://localhost:8003/api/stocks/deduct",
            json={
                "product_id": product_id,
                "location_id": location_id,
                "quantity": quantity
            },
            timeout=3
        )
        return response.status_code == 200
    except requests.RequestException:
        return False

def add_sale(product_id, location_data, quantity):
    """
    Record a sale after confirming stock via stock_service.
    location_data = {"id": ..., "name": ...}
    """
    session = SessionLocal()
    try:
        product = get_product_from_api(product_id)
        if not product:
            print("Produit introuvable.")
            return False

        stock_info = get_stock_from_api(product_id, location_data["id"])
        if not stock_info:
            print("Erreur lors de la vérification du stock.")
            return False

        if stock_info["quantity"] < quantity:
            print(f"Stock insuffisant ({stock_info['quantity']} disponibles).")
            return False

        if not deduct_stock(product_id, location_data["id"], quantity):
            print("Échec de la déduction de stock.")
            return False

        sale = Sale(
            product_id=product_id,
            location_id=location_data["id"],
            quantity=quantity
        )
        session.add(sale)
        session.commit()

        print(
            f"Vente enregistrée chez {location_data['name']} | "
            f"{quantity} x {product['name']} à {product['price']} = "
            f"${product['price'] * quantity:.2f}"
        )
        return True

    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'enregistrement de la vente : {e}")
        return False
    finally:
        session.close()

def get_sales_by_location(location="Magasin 1", page=1, size=10, sort_field="id", sort_order="asc"):
    """Get sales from a location"""
    session = SessionLocal()
    query = (
        session.query(Sale)
        .options(joinedload(Sale.product), joinedload(Sale.location))
        .filter_by(location_id=location.id)
    )

    if hasattr(Sale, sort_field):
        sort_column = getattr(Sale, sort_field)
    else:
        sort_column = Sale.id

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    results = query.offset((page - 1) * size).limit(size).all()

    session.close()
    return results, total

def get_all_sales():
    """Get all sales from everywhere"""
    session = SessionLocal()
    try:
        return session.query(Sale).options(
            joinedload(Sale.product),
            joinedload(Sale.location)
        ).all()
    finally:
        session.close()

def cancel_sale(sale_id):
    """Cancel a sale and restore stock via stock service API."""
    session = SessionLocal()
    try:
        sale = session.get(Sale, sale_id, options=[
            joinedload(Sale.product),
            joinedload(Sale.location)
        ])

        if not sale:
            print(f"Aucune vente trouvée avec l'ID {sale_id}.")
            return False

        product_id = sale.product.id
        location_name = sale.location.name
        quantity = sale.quantity

        try:
            response = requests.post(
                "http://localhost:8003/api/stocks",
                json={
                    "location": location_name,
                    "product_id": product_id,
                    "quantity": quantity
                },
                timeout=3
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Erreur lors de la restauration du stock via l'API: {e}")
            return False

        session.delete(sale)
        session.commit()

        print(f"Vente #{sale.id} annulée. {quantity} unités de '{sale.product.name}' restaurées à '{location_name}'.")
        return True

    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'annulation de la vente : {e}")
        return False
    finally:
        session.close()

def get_location_by_name_from_api(name):
    """Method to get from location service"""
    try:
        response = requests.get(f"http://localhost:8001/api/locations/{name}", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None
