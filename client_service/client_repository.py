"""Client repository"""
from models import Client
from database import SessionLocal
from werkzeug.security import generate_password_hash

def create_client(username, password, email):
    """Method to get create client"""
    session = SessionLocal()
    try:
        hashed_pw = generate_password_hash(password)
        new_client = Client(username=username, password=hashed_pw, email=email)
        session.add(new_client)
        session.commit()
        session.refresh(new_client)
        return new_client
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def get_client_by_username(username):
    """Method to get all clients by username"""
    session = SessionLocal()
    try:
        return session.query(Client).filter(Client.username == username).first()
    finally:
        session.close()

def get_all_clients():
    """Method to get all clients"""
    session = SessionLocal()
    try:
        return session.query(Client).all()
    finally:
        session.close()
