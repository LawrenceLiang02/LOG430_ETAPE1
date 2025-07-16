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
