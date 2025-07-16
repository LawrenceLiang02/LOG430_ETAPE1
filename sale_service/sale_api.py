"""Sale API for /sales using Flask-RESTX"""

from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required
from sale_repository import add_sale, cancel_sale, get_sales_by_location, get_location_by_name_from_api

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


@api.route("/", strict_slashes=False)
class SaleList(Resource):
    """main api route for /"""
    @api.doc(params={
        "location": "Nom de l'emplacement (obligatoire)",
        "page": "Page number (starts at 1)",
        "size": "Number of items per page",
        "sort": "Sort format: field[,asc|desc] (e.g. total,desc)"
    })
    @jwt_required()
    def get(self):
        """Get paginated sales for a specific location"""
        location_name = request.args.get("location")
        if not location_name:
            api.abort(400, "Paramètre 'location' requis.")

        location_data = get_location_by_name_from_api(location_name)
        if not location_data:
            api.abort(404, f"Emplacement '{location_name}' introuvable.")
        location = location_data["id"]

        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 10))
        sort = request.args.get("sort", "id,asc")
        sort_field, sort_order = (sort.split(",") + ["asc"])[:2]
        sort_order = sort_order.lower()

        sales, total = get_sales_by_location(
            location,
            page=page,
            size=size,
            sort_field=sort_field,
            sort_order=sort_order
        )

        return {
            "page": page,
            "size": size,
            "total": total,
            "items": [
                {
                    "id": s.id,
                    "location": s.location.name if s.location else "Inconnu",
                    "product": s.product.name if s.product else "Produit inconnu",
                    "quantity": s.quantity,
                    "unit_price": s.product.price if s.product else 0.0,
                    "total": (s.product.price * s.quantity) if s.product else 0.0
                }
                for s in sales
            ]
        }

    @api.expect(sale_input_model)
    @jwt_required()
    def post(self):
        """Record a new sale"""
        data = request.json
        location_name = data.get("location")
        product_id = data.get("product_id")
        quantity = data.get("quantity")

        if not location_name or not isinstance(product_id, int) or not isinstance(quantity, int):
            api.abort(400, "Champs 'location', 'product_id' et 'quantity' requis.")

        if quantity <= 0:
            api.abort(400, "La quantité doit être supérieure à 0.")

        location_data = get_location_by_name_from_api(location_name)
        if not location_data:
            api.abort(404, f"Emplacement '{location_name}' introuvable.")
        location = location_data["id"]

        if not location:
            api.abort(404, f"Emplacement '{location_name}' introuvable.")

        success = add_sale(product_id, location, quantity)
        if not success:
            api.abort(400, "Échec de l'enregistrement de la vente.")

        return {"message": "Vente enregistrée avec succès."}, 201


@api.route("/<int:sale_id>")
class SaleDelete(Resource):
    """Class to delete sale"""
    @jwt_required()
    def delete(self, sale_id):
        """Cancel a sale by its ID"""
        try:
            cancel_sale(sale_id)
            return {"message": f"Vente #{sale_id} annulée."}
        except ValueError:
            api.abort(400, "ID de vente invalide.")
