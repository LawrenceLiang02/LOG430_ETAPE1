"""Cart API"""
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
import cart_repository as cart_repo

api = Namespace("Cart", description="Shopping cart and checkout")

cart_item_model = api.model("CartItem", {
    "product_id": fields.Integer(required=True),
    "quantity": fields.Integer(required=True),
    "location": fields.String(required=True)
})

@api.route("/")
class Cart(Resource):
    """Cart endpoints"""

    @jwt_required()
    def get(self):
        """Get current user's cart"""
        user = get_jwt_identity()
        return cart_repo.get_cart(user)

    @api.expect(cart_item_model)
    @jwt_required()
    def post(self):
        """Add item to cart with stock deduction"""
        user = get_jwt_identity()
        data = request.json
        auth_header = request.headers.get("Authorization")

        result, status = cart_repo.add_to_cart(
            user=user,
            product_id=data["product_id"],
            quantity=data["quantity"],
            location=data["location"],
            auth_header=auth_header
        )
        return result, status


@api.route("/checkout")
class Checkout(Resource):
    """Checkout endpoint"""

    @jwt_required()
    def post(self):
        """checkout for payment"""
        user = get_jwt_identity()
        auth_header = request.headers.get("Authorization")
        result, status = cart_repo.checkout_cart(user, auth_header)
        return result, status


@api.route("/cancel")
class Cancel(Resource):
    """Cancel endpoint"""

    @jwt_required()
    def post(self):
        user = get_jwt_identity()
        auth_header = request.headers.get("Authorization")
        result, status = cart_repo.cancel_cart(user, auth_header)
        return result, status
