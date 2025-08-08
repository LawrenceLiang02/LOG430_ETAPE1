"""Saga API"""
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from saga_repository import get_all_sagas, orchestrer_commande, get_saga_status

api = Namespace("Saga", description="Orchestrateur de commande")

cart_item = api.model("CartItem", {
    "product_id": fields.Integer(required=True),
    "quantity": fields.Integer(required=True),
    "location": fields.String(required=True)
})

saga_start = api.model("StartSaga", {
    "cart": fields.List(fields.Nested(cart_item))
})

@api.route("/start")
class StartSaga(Resource):
    """start saga"""
    @api.expect(saga_start)
    @jwt_required()
    def post(self):
        """Démarre une saga pour une commande"""
        user = get_jwt_identity()
        data = request.json
        cart = data.get("cart", [])
        auth_header = request.headers.get("Authorization")
        return orchestrer_commande(user, cart, auth_header)

@api.route("/<int:saga_id>/status")
class SagaStatus(Resource):
    """saga by id"""
    @jwt_required()
    def get(self, saga_id):
        """Récupère l'état d'une saga"""
        status = get_saga_status(saga_id)
        if not status:
            api.abort(404, "Saga introuvable.")
        return status

@api.route("/")
class AllSagas(Resource):
    """All sagas"""
    @jwt_required()
    def get(self):
        """Récupère toutes les sagas"""
        return get_all_sagas()