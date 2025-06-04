"""Module to handle store management"""
from sqlalchemy.orm import joinedload
from data_class.models import Product, Sale, Location, Stock
from data_access_layer.database import SessionLocal

def add_sale(product_id, location, quantity):
    """Record a sale of a specific product with a given quantity."""
    session = SessionLocal()
    try:
        product = session.get(Product, product_id)

        if not product:
            print("Produit introuvable.")
            return

        stock = session.query(Stock).filter_by(
            product_id=product.id,
            location_id=location.id
        ).first()

        if not stock or stock.quantity < quantity:
            print(f"Stock insuffisant pour le produit '{product.name}' dans le magasin '{location.name}'.")
            return
        
        stock.quantity -= quantity

        sale = Sale(product=product, location_id=location.id, quantity=quantity)
        session.add(sale)
        session.commit()

        print(f"Vente enregistrée chez {location.name} | {quantity} {product.name} x {product.price} = ${(product.price * quantity):.2f}")

    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'enregistrement de la vente: {e}")
    finally:
        session.close()

def get_sales_by_location(location):
    """Get sales from a location"""
    session = SessionLocal()
    try:
        sales = session.query(Sale).options(
            joinedload(Sale.product),
            joinedload(Sale.location)
        ).filter_by(location_id=location.id).all()
        return sales
    finally:
        session.close()

def get_all_sales():
    """Récupère toutes les ventes avec produit et magasin préchargés."""
    session = SessionLocal()
    try:
        return session.query(Sale).options(
            joinedload(Sale.product),
            joinedload(Sale.location)
        ).all()
    finally:
        session.close()

def cancel_sale(sale_id):
    """Cancel a sale from a store."""
    session = SessionLocal()
    try:
        sale = session.get(Sale, sale_id, options=[
            joinedload(Sale.product),
            joinedload(Sale.location)
        ])

        if not sale:
            print(f"Aucune vente trouvée avec l'ID {sale_id}.")
            return

        product = sale.product
        location = sale.location
        stock = session.query(Stock).filter_by(
            product_id=product.id,
            location_id=location.id
        ).first()

        if stock:
            stock.quantity += sale.quantity
        else:
            stock = Stock(
                product_id=product.id,
                location_id=location.id,
                quantity=sale.quantity
            )
            session.add(stock)

        session.delete(sale)
        session.commit()

        print(f"Vente #{sale.id} annulée. Stock de {product.name} restauré à {stock.quantity} dans {location.name}.")

    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'annulation de la vente : {e}")
    finally:
        session.close()
