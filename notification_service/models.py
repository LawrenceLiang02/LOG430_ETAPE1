"""
Notification model
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Notification(Base):
    """
    Notification model for storing events sent to users.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    recipient = Column(String, nullable=False)  # Optional: if you're sending to a user or email
    message = Column(String, nullable=False)    # Human-readable message
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification(id={self.id}, event_type='{self.event_type}', recipient='{self.recipient}')>"
