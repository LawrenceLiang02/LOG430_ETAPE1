"""Stock module for the data access layer"""
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from service_layer.database import SessionLocal
from data_class.models import Location, Product, Stock, StockRequest

def add_stock(product_id, store, quantity):
    """
    Add stock to store
    If it is centre logistique, then it stocks up
    Or else it takes from centre logistique
    """
    session = SessionLocal()
    try:
        product = session.get(Product, product_id)
        if not product:
            print(f"Produit avec ID {product_id} introuvable.")
            return False

        if store.name.lower() == "centre logistique":
            stock = session.query(Stock).filter_by(
                product_id=product.id,
                location_id=store.id
            ).first()

            if stock:
                stock.quantity += quantity
            else:
                stock = Stock(
                    product_id=product.id,
                    location_id=store.id,
                    quantity=quantity
                )
                session.add(stock)

            session.commit()
            print(f"{quantity} unités ajoutées dans le centre logistique.")
            return True

        logistic = session.query(Location).filter_by(name="Centre logistique").first()
        if not logistic:
            print("Centre logistique introuvable.")
            return False

        logistic_stock = session.query(Stock).filter_by(
            product_id=product.id,
            location_id=logistic.id
        ).first()

        if not logistic_stock or logistic_stock.quantity < quantity:
            print(f"Stock insuffisant dans le centre logistique ({logistic_stock.quantity if logistic_stock else 0}).")
            return False

        logistic_stock.quantity -= quantity

        target_stock = session.query(Stock).filter_by(
            product_id=product.id,
            location_id=store.id
        ).first()

        if target_stock:
            target_stock.quantity += quantity
        else:
            target_stock = Stock(
                product_id=product.id,
                location_id=store.id,
                quantity=quantity
            )
            session.add(target_stock)

        session.commit()
        print(f"{quantity} unités transférées de 'Centre logistique' vers '{store.name}'.")
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
    """Method to fulfill stock request"""
    session = SessionLocal()

    request = session.query(StockRequest).options(
        joinedload(StockRequest.product),
        joinedload(StockRequest.location)
    ).get(request_id)

    if not request:
        session.close()
        return False, "Demande introuvable."

    product = request.product
    destination = request.location

    centre = session.query(Location).filter(func.lower(Location.name) == "centre logistique").first()
    if not centre:
        session.close()
        return False, "Centre Logistique introuvable."

    source_stock = session.query(Stock).filter_by(
        location_id=centre.id, product_id=product.id).first()

    if not source_stock or source_stock.quantity < request.quantity:
        session.close()
        return False, "Stock insuffisant au Centre Logistique."

    source_stock.quantity -= request.quantity

    dest_stock = session.query(Stock).filter_by(
        location_id=destination.id, product_id=product.id).first()
    if dest_stock:
        dest_stock.quantity += request.quantity
    else:
        dest_stock = Stock(
            location_id=destination.id,
            product_id=product.id,
            quantity=request.quantity
        )
        session.add(dest_stock)

    product_name = product.name
    destination_name = destination.name
    qty = request.quantity

    session.delete(request)
    session.commit()
    session.close()

    return True, f"{qty} unités de {product_name} envoyées à {destination_name}."
