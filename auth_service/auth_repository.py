"""Logic for auth"""
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User

def authenticate_user(username: str, password: str):
    """Vérifie les identifiants utilisateur"""
    session: Session = SessionLocal()
    try:
        user = session.query(User).filter_by(username=username, password=password).first()
        return user
    finally:
        session.close()

def create_client(username: str, password: str):
    """Crée un nouveau client, retourne None si le nom est déjà pris"""
    session: Session = SessionLocal()
    try:
        if session.query(User).filter_by(username=username).first():
            return None

        new_client = User(
            username=username,
            password=password,
            role="client"
        )
        session.add(new_client)
        session.commit()
        session.refresh(new_client)
        return new_client
    finally:
        session.close()

def get_client_by_username(username: str):
    """Récupère un client par nom d'utilisateur"""
    session: Session = SessionLocal()
    try:
        return session.query(User).filter_by(username=username, role="client").first()
    finally:
        session.close()
