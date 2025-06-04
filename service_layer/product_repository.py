"""Product module for the data access layer"""
from data_access_layer.database import SessionLocal
from data_class.models import Product

def add_product(name, price):
    """Add product method to create a new product in the database"""
    session = SessionLocal()
    p = Product(name=name, price=price)
    session.add(p)
    session.commit()
    session.close()
    print("Successfully added")

def get_products():
    """Method to get all the products"""
    session = SessionLocal()
    products = session.query(Product).all()
    session.close()
    return products

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
