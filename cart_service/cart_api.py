"""Cart api"""
import requests
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from cart_repository import add_item_to_cart, get_cart, clear_cart

api = Namespace("Cart", description="Shopping cart and checkout")

cart_item_model = api.model("CartItem", {
    "product_id": fields.Integer(required=True),
    "quantity": fields.Integer(required=True),
    "location": fields.String(required=True)
})

@api.route("/")
class Cart(Resource):
    """Cart api"""
    @jwt_required()
    def get(self):
        """Get current user's cart"""
        user = get_jwt_identity()
        items = get_cart(user)
        return [
            {"id": item.id, "product_id": item.product_id, "quantity": item.quantity, "location": item.location}
            for item in items
        ]

    @api.expect(cart_item_model)
    @jwt_required()
    def post(self):
        """Add item to cart"""
        data = request.json
        product_id = data["product_id"]
        quantity = data["quantity"]
        location = data["location"]
        user = get_jwt_identity()

        item = add_item_to_cart(user, product_id, quantity, location)
        return {"message": "Ajouté au panier", "id": item.id}, 201

@api.route("/checkout")
class Checkout(Resource):
    """Checkout api"""
    @jwt_required()
    def post(self):
        """Validate the current user's cart (create sales + update stock)"""
        user = get_jwt_identity()
        cart = get_cart(user)
        if not cart:
            return {"message": "Panier vide"}, 400

        errors = []
        for item in cart:
            stock_resp = requests.get("http://localhost:8003/api/stocks/check", params={
                "product_id": item.product_id,
                "location_id": _get_location_id(item.location)
            }, timeout=3)
            stock_data = stock_resp.json()
            if stock_data["quantity"] < item.quantity:
                errors.append(f"Stock insuffisant pour produit {item.product_id}")
                continue

            deduct_resp = requests.post("http://localhost:8003/api/stocks/deduct", json={
                "product_id": item.product_id,
                "location_id": stock_data["location_id"],
                "quantity": item.quantity
            }, timeout=3)
            if deduct_resp.status_code != 200:
                errors.append(f"Échec du déstockage produit {item.product_id}")
                continue

            sale_resp = requests.post("http://localhost:8004/api/sale", json={
                "location": item.location,
                "product_id": item.product_id,
                "quantity": item.quantity
            }, headers={"Authorization": request.headers.get("Authorization")}, timeout=3)

            if sale_resp.status_code != 201:
                errors.append(f"Échec de la vente pour produit {item.product_id}")

        clear_cart(user)

        if errors:
            return {"message": "Commande partiellement validée", "errors": errors}, 207

        return {"message": "Commande validée avec succès"}, 200


def _get_location_id(location_name):
    resp = requests.get(f"http://localhost:8001/api/locations/{location_name}", timeout=3)
    if resp.status_code != 200:
        raise ValueError(f"Emplacement '{location_name}' introuvable.")
    return resp.json()["id"]
