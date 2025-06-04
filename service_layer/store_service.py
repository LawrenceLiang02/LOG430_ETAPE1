"""Module to handle store management"""
from sqlalchemy.orm import joinedload
from data_class.models import Product, Sale, Location, Stock
from data_access_layer.database import SessionLocal

def add_product(name, price):
    """Add product method to create a new product in the database"""
    session = SessionLocal()
    p = Product(name=name, price=price)
    session.add(p)
    session.commit()
    session.close()
    print("Successfully added")

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

        if not store or not store.id:
            print("Magasin invalide.")
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

def get_products():
    """Method to get all the products"""
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()
    return products

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

def search_product_by(type_, keyword):
    """Search products by ID, name, or category."""
    session = SessionLocal()
    try:
        if type_ == "id":
            product = session.get(Product, int(keyword))
            return [product] if product else []

        if type_ == "name":
            return session.query(Product).filter(Product.name.ilike(f"%{keyword}%")).all()

        if type_ == "category":
            return session.query(Product).filter(Product.category.ilike(f"%{keyword}%")).all()

        raise ValueError("Type de recherche invalide.")
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

def get_all_locations():
    """Récupère toutes les locations depuis la base de données."""
    session = SessionLocal()
    try:
        return session.query(Location).order_by(Location.name).all()
    finally:
        session.close()
