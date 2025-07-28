"""Database configuration for Saga Orchestrator"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///saga.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    from model import CommandeSaga
    Base.metadata.create_all(bind=engine)
