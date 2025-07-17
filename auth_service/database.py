"""
Database for users
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./auth.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    """Initialise la base de données et insère les rôles par défaut"""
    from models import User
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()

    if not session.query(User).filter_by(username="admin").first():
        admin_user = User(username="admin", password="admin", role="admin")
        session.add(admin_user)
        print("Utilisateur admin créé avec succès.")

    session.commit()
    session.close()
