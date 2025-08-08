"""Notification repository module for the data access layer"""
from database import SessionLocal
from models import AuditLog
import json

def log_event(event_type: str, payload: dict):
    """log event"""
    session = SessionLocal()
    log = AuditLog(
        event_type=event_type,
        payload=json.dumps(payload)
    )
    session.add(log)
    session.commit()
    session.close()


def get_all_logs():
    """get all logs"""
    session = SessionLocal()
    logs = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    session.close()
    return logs