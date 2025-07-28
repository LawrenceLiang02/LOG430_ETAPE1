"""Sale API for /sales using Flask-RESTX"""

from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required
from sale_repository import (
    record_sale_only,          # NEW
    add_sale_with_deduct,      # RENAMED old add_sale
    cancel_sale,
    get_sales_by_location,
    get_location_by_name_from_api
)

api = Namespace("Sales", description="Sale operations")

sale_model = api.model("Sale", {
    "id": fields.Integer,
    "location": fields.String,
    "product": fields.String,
    "quantity": fields.Integer,
    "unit_price": fields.Float,
    "total": fields.Float
})

sale_input_model = api.model("NewSale", {
    "location": fields.String(required=True),
    "product_id": fields.Integer(required=True),
    "quantity": fields.Integer(required=True)
})

def _auth_header():
    return request.headers.get("Authorization")

@api.route("/", strict_slashes=False)
class SaleList(Resource):
    """List & direct sale (with deduction)"""

    @api.doc(params={
        "location": "Nom de l'emplacement (obligatoire)",
        "page": "Page number (starts at 1)",
        "size": "Number of items per page",
        "sort": "Sort format: field[,asc|desc] (e.g. total,desc)"
    })
    @jwt_required()
    def get(self):
        """Get paginated sales for a specific location"""
        auth = _auth_header()
        location_name = request.args.get("location")
        if not location_name:
            api.abort(400, "Paramètre 'location' requis.")

        location_data = get_location_by_name_from_api(location_name, auth)
        if not location_data:
            api.abort(404, f"Emplacement '{location_name}' introuvable.")
        location_id = location_data["id"]

        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 10))
        sort = request.args.get("sort", "id,asc")
        sort_field, sort_order = (sort.split(",") + ["asc"])[:2]

        sales, total = get_sales_by_location(
            location_id,
            page=page,
            size=size,
            sort_field=sort_field,
            sort_order=sort_order,
            auth_header=auth
        )


        return {
            "page": page,
            "size": size,
            "total": total,
            "items": sales
        }

    @api.expect(sale_input_model)
    @jwt_required()
    def post(self):
        """
        Direct sale (check & deduct stock + record). Keep it for back-office / manual ops.
        For the cart flow, call /sales/record instead.
        """
        auth = _auth_header()
        data = request.json
        location_name = data.get("location")
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        if not location_name or not isinstance(product_id, int) or not isinstance(quantity, int):
            api.abort(400, "Champs 'location', 'product_id' et 'quantity' requis.")
        if quantity <= 0:
            api.abort(400, "La quantité doit être supérieure à 0.")

        ok, msg = add_sale_with_deduct(product_id, location_name, quantity, auth)
        if not ok:
            api.abort(400, msg)
        return {"message": "Vente enregistrée avec succès."}, 201


@api.route("/record")
class SaleRecord(Resource):
    """Record-only sale (used by /cart/checkout)"""

    @api.expect(sale_input_model)
    @jwt_required()
    def post(self):
        """Record a sale without touching stock (cart already deducted it)."""
        auth = _auth_header()
        data = request.json
        location_name = data.get("location")
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        if not location_name or not isinstance(product_id, int) or not isinstance(quantity, int):
            api.abort(400, "Champs 'location', 'product_id' et 'quantity' requis.")
        if quantity <= 0:
            api.abort(400, "La quantité doit être supérieure à 0.")

        ok, msg = record_sale_only(product_id, location_name, quantity, auth)
        if not ok:
            api.abort(400, msg)
        return {"message": "Vente enregistrée avec succès."}, 201


@api.route("/<int:sale_id>")
class SaleDelete(Resource):
    @jwt_required()
    def delete(self, sale_id):
        """Cancel a sale by its ID"""
        auth = _auth_header()
        try:
            cancel_sale(sale_id, auth)
            return {"message": f"Vente #{sale_id} annulée."}
        except ValueError:
            api.abort(400, "ID de vente invalide.")
