"""Stock API for /stocks using Flask-RESTX"""
from flask_restx import Namespace, Resource, fields
from flask import request
from service_layer.stock_repository import (
    add_stock,
    get_stock,
    create_stock_request,
    get_all_stock_requests,
    fulfill_stock_request
)
from service_layer.location_repository import get_location_by_name

api = Namespace("Stocks", description="Stock operations")

stock_model = api.model("Stock", {
    "product_id": fields.Integer,
    "product_name": fields.String,
    "quantity": fields.Integer,
    "location": fields.String
})

stock_input = api.model("AddStock", {
    "location": fields.String(required=True),
    "product_id": fields.Integer(required=True),
    "quantity": fields.Integer(required=True)
})

stock_request_model = api.model("StockRequest", {
    "id": fields.Integer,
    "location": fields.String,
    "product": fields.String,
    "quantity": fields.Integer
})

@api.route("/")
class StockByLocation(Resource):
    """Get stocks by location"""
    @api.doc(params={"location": "Nom de l'emplacement"})
    @api.marshal_list_with(stock_model)
    def get(self):
        """Get current stock for a specific location"""
        location_name = request.args.get("location")
        if not location_name:
            api.abort(400, "Paramètre 'location' requis.")

        location = get_location_by_name(location_name)
        if not location:
            api.abort(404, f"Emplacement '{location_name}' introuvable.")

        stocks = get_stock(location)
        return [
            {
                "product_id": s.product.id,
                "product_name": s.product.name,
                "quantity": s.quantity,
                "location": s.location.name
            } for s in stocks
        ]

    @api.expect(stock_input)
    def post(self):
        """Add or transfer stock to a location"""
        data = request.json
        location_name = data.get("location")
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        if not location_name or not isinstance(product_id, int) or not isinstance(quantity, int):
            api.abort(400, "Champs 'location', 'product_id', et 'quantity' requis.")

        location = get_location_by_name(location_name)
        if not location:
            api.abort(404, f"Emplacement '{location_name}' introuvable.")

        success = add_stock(product_id, location, quantity)
        if not success:
            api.abort(400, "Échec de l'ajout ou du transfert de stock.")

        return {"message": f"{quantity} unités ajoutées ou transférées avec succès."}, 201


@api.route("/requests")
class StockRequestList(Resource):
    """Create a request API route"""
    @api.marshal_list_with(stock_request_model)
    def get(self):
        """List all stock replenishment requests"""
        requests = get_all_stock_requests()
        return [
            {
                "id": r.id,
                "location": r.location.name,
                "product": r.product.name,
                "quantity": r.quantity
            } for r in requests
        ]

    @api.expect(stock_input)
    def post(self):
        """Create a new stock request"""
        data = request.json
        location_name = data.get("location")
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        if not location_name or not isinstance(product_id, int) or not isinstance(quantity, int):
            api.abort(400, "Champs 'location', 'product_id', et 'quantity' requis.")

        location = get_location_by_name(location_name)
        if not location:
            api.abort(404, f"Emplacement '{location_name}' introuvable.")

        success = create_stock_request(location.id, product_id, quantity)
        if not success:
            api.abort(400, "Échec de la création de la demande.")

        return {"message": "Demande de réapprovisionnement créée avec succès."}, 201


@api.route("/requests/<int:request_id>/fulfill")
class StockRequestFulfill(Resource):
    """Fulfill a stock request API route"""
    def post(self, request_id):
        """Fulfill a stock request by its ID"""
        success, message = fulfill_stock_request(request_id)
        if success:
            return {"message": message}
        api.abort(400, message)
