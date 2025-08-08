"""Notification repository module for the data access layer"""
from database import SessionLocal
from models import Notification

def create_notification(event_type, recipient, message):
    """create notification"""
    session = SessionLocal()
    notif = Notification(
        event_type=event_type,
        recipient=recipient,
        message=message
    )
    session.add(notif)
    session.commit()
    session.close()
    print(f"Notification envoyée à {recipient}: {message}")

def get_all_notifications():
    """get all notifications"""
    session = SessionLocal()
    notifs = session.query(Notification).all()
    session.close()
    return [{
        "event_type": n.event_type,
        "recipient": n.recipient,
        "message": n.message
    } for n in notifs]
