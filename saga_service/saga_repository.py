"""Saga Orchestration Logic"""
import requests
from database import SessionLocal
from model import CommandeSaga, EtatSaga

STOCK_SVC = "http://stock_service_1:5000"
SALE_SVC = "http://sale_service_1:5000"
CART_SVC = "http://cart_service_1:5000"

def _auth_headers(auth_header):
    return {"Authorization": auth_header} if auth_header else {}

def log_step(saga: CommandeSaga, step: str, session):
    saga.logs += f"\n{step}"
    session.commit()

def orchestrer_commande(user, cart, auth_header=None):
    """
    Orchestrate the saga:
    1) Reserve stock (deduct stock)
    2) Checkout cart (acts like payment + validation)
    3) Record sales
    On failure: rollback stock.
    """
    session = SessionLocal()
    try:
        saga = CommandeSaga(user=user, etat=EtatSaga.CREEE)
        session.add(saga)
        session.commit()

        headers = _auth_headers(auth_header)

        for item in cart:
            r = requests.post(
                f"{STOCK_SVC}/api/stocks/deduct",
                json={
                    "product_id": item["product_id"],
                    "location_id": item["location_id"],
                    "quantity": item["quantity"]
                },
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

        checkout_resp = requests.post(
            f"{CART_SVC}/api/cart/checkout",
            headers=headers,
            timeout=5
        )
        if checkout_resp.status_code != 200:
            saga.etat = EtatSaga.ECHEC
            log_step(saga, f"Cart checkout failed: {checkout_resp.text}", session)
            for item in cart:
                requests.post(
                    f"{STOCK_SVC}/api/stocks",
                    json={
                        "location": item["location"],
                        "product_id": item["product_id"],
                        "quantity": item["quantity"]
                    },
                    headers=headers
                )
            session.commit()
            return {"message": "Échec de la commande (checkout)", "saga_id": saga.id}, 402
        saga.etat = EtatSaga.PAIEMENT_OK
        log_step(saga, "Cart checkout OK", session)

        for item in cart:
            s = requests.post(
                f"{SALE_SVC}/api/sale/record",
                json={
                    "location": item["location"],
                    "product_id": item["product_id"],
                    "quantity": item["quantity"]
                },
                headers=headers,
                timeout=3
            )
            if s.status_code != 201:
                saga.etat = EtatSaga.ECHEC
                log_step(saga, f"Sale recording failed: {s.text}", session)
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
    return {
        "id": saga.id,
        "user": saga.user,
        "etat": saga.etat.value,
        "logs": saga.logs
    }
