"""Module to handle store management"""
from sqlalchemy.orm import joinedload
from data_class.models import Product, Sale
from data_access_layer.database import SessionLocal

def add_product(name, price, quantity):
    """Add product method to create a new product in the database"""
    session = SessionLocal()
    p = Product(name=name, price=price, quantity=quantity)
    session.add(p)
    session.commit()
    session.close()
    print("Successfully added")

def add_sale(product_id, quantity):
    """Record a sale of a specific product with a given quantity."""
    session = SessionLocal()
    try:
        product = session.query(Product).get(product_id)

        if not product:
            print("Produit introuvable.")
            return

        if product.quantity < quantity:
            print(f"Stock insuffisant pour le produit : {product.name}")
            return

        product.quantity -= quantity

        sale = Sale(product=product, quantity=quantity)
        session.add(sale)
        session.commit()

        print(f"Vente enregistrée: {quantity} {product.name} x {product.price} = ${(product.price * quantity):.2f}")

    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'enregistrement de la vente: {e}")
    finally:
        session.close()

def get_products():
    """Method to get all the products"""
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()
    return products

def get_sales():
    """Method to get all the sales"""
    session = SessionLocal()
    sales = session.query(Sale).options(joinedload(Sale.product)).all()
    session.close()
    return sales

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

        else:
            raise ValueError("Type de recherche invalide.")
    finally:
        session.close()

def cancel_sale(sale_id):
    """Cancel a sale by its ID and restore the product's stock."""
    session = SessionLocal()
    try:
        sale = session.query(Sale).options(joinedload(Sale.product)).get(sale_id)

        if not sale:
            print(f"Aucune vente trouvée avec l'ID {sale_id}.")
            return

        product = sale.product
        product.quantity += sale.quantity

        session.delete(sale)
        session.commit()

        print(f"Vente #{sale.id} annulée. Stock de {product.name} restauré à {product.quantity}.")

    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'annulation de la vente : {e}")
    finally:
        session.close()
