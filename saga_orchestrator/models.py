"""Models for Saga Orchestrator"""
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from database import Base
import enum

class EtatSaga(enum.Enum):
    CREEE = "CREEE"
    STOCK_RESERVE = "STOCK_RESERVE"
    PAIEMENT_OK = "PAIEMENT_OK"
    CONFIRMEE = "CONFIRMEE"
    ECHEC = "ECHEC"

class CommandeSaga(Base):
    __tablename__ = "commande_saga"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, nullable=False)
    etat = Column(Enum(EtatSaga), default=EtatSaga.CREEE, nullable=False)
    logs = Column(String, default="")
    created_at = Column(DateTime, server_default=func.now())
