"""Saga Orchestration Logic"""
import requests
from database import SessionLocal
from model import CommandeSaga, EtatSaga

STOCK_SVC = "http://stock_service_1:5000"
SALE_SVC = "http://sale_service:5000"
PAYMENT_SVC = "http://payment_service:5000"  # Fake service

def _auth_headers(auth_header):
    return {"Authorization": auth_header} if auth_header else {}

def log_step(saga: CommandeSaga, step: str, session):
    saga.logs += f"\n{step}"
    session.commit()

def orchestrer_commande(user, cart, auth_header=None):
    """
    Orchestrate the saga:
    1) Reserve stock
    2) Simulate payment
    3) Record sale
    On failure: rollback stock.
    """
    session = SessionLocal()
    try:
        saga = CommandeSaga(user=user, etat=EtatSaga.CREEE)
        session.add(saga)
        session.commit()

        headers = _auth_headers(auth_header)

        # Step 1: Reserve stock
        for item in cart:
            r = requests.post(
                f"{STOCK_SVC}/api/stocks/deduct",
                json={"product_id": item["product_id"], "location_id": item["location_id"], "quantity": item["quantity"]},
                headers=headers,
                timeout=3
            )
            if r.status_code != 200:
                saga.etat = EtatSaga.ECHEC
                log_step(saga, f"Stock reservation failed: {r.text}", session)
                session.commit()
                return {"message": "Stock insuffisant", "saga_id": saga.id}, 409
        saga.etat = EtatSaga.STOCK_RESERVE
        log_step(saga, "Stock reserved successfully", session)

        # Step 2: Payment
        pay_resp = requests.post(f"{PAYMENT_SVC}/pay", json={"user": user, "amount": 100}, headers=headers)
        if pay_resp.status_code != 200:
            saga.etat = EtatSaga.ECHEC
            log_step(saga, "Payment failed", session)
            # Compensation: re-add stock
            for item in cart:
                requests.post(f"{STOCK_SVC}/api/stocks", json={
                    "location": item["location"], "product_id": item["product_id"], "quantity": item["quantity"]
                }, headers=headers)
            session.commit()
            return {"message": "Paiement refusé", "saga_id": saga.id}, 402
        saga.etat = EtatSaga.PAIEMENT_OK
        log_step(saga, "Payment OK", session)

        # Step 3: Sale
        for item in cart:
            s = requests.post(
                f"{SALE_SVC}/api/sales/record",
                json={"location": item["location"], "product_id": item["product_id"], "quantity": item["quantity"]},
                headers=headers,
                timeout=3
            )
            if s.status_code != 201:
                saga.etat = EtatSaga.ECHEC
                log_step(saga, "Sale recording failed", session)
                session.commit()
                return {"message": "Erreur vente", "saga_id": saga.id}, 500

        saga.etat = EtatSaga.CONFIRMEE
        log_step(saga, "Sale recorded successfully", session)
        session.commit()

        return {"message": "Commande confirmée", "saga_id": saga.id}, 200
    except Exception as e:
        saga.etat = EtatSaga.ECHEC
        log_step(saga, f"Exception: {e}", session)
        session.commit()
        return {"message": f"Erreur interne: {e}", "saga_id": saga.id}, 500
    finally:
        session.close()

def get_saga_status(saga_id: int):
    session = SessionLocal()
    saga = session.query(CommandeSaga).get(saga_id)
    session.close()
    if not saga:
        return None
    return {"id": saga.id, "user": saga.user, "etat": saga.etat.value, "logs": saga.logs}
