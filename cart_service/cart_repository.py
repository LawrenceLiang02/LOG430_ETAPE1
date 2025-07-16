"""Cart repository"""
from models import CartItem
from database import SessionLocal

def add_item_to_cart(user, product_id, quantity, location):
    """Method to add item to cart"""
    session = SessionLocal()
    try:
        item = CartItem(user=user, product_id=product_id, quantity=quantity, location=location)
        session.add(item)
        session.commit()
        return item
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_cart(user):
    """Method to get cart"""
    session = SessionLocal()
    try:
        return session.query(CartItem).filter_by(user=user).all()
    finally:
        session.close()

def clear_cart(user):
    """Method to clear cart"""
    session = SessionLocal()
    try:
        session.query(CartItem).filter_by(user=user).delete()
        session.commit()
    finally:
        session.close()
