"""API for /products"""
import logging
from extensions import cache
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required
from service_layer.product_repository import add_product, get_products, search_product_by, update_product

logger = logging.getLogger(__name__)

api = Namespace("Products", description="Product operations")

product_model = api.model("Product", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True),
    "price": fields.Float(required=True),
    "description": fields.String
})

@api.route("/")
class ProductList(Resource):
    """Product list class"""
    @api.doc(params={
        "page": "Page number (starts at 1)",
        "size": "Number of items per page",
        "category": "Filter by category (not yet implemented)",
        "sort": "Sort format: field[,asc|desc] (e.g. name,asc)"
    })
    @jwt_required()
    def get(self):
        """Method to get"""
        logger.info("GET /api/products - page=%s size=%s sort=%s", request.args.get("page"), request.args.get("size"), request.args.get("sort"))
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", 10))
        sort = request.args.get("sort", "id,asc")
        category = request.args.get("category")

        sort_field, sort_order = (sort.split(",") + ["asc"])[:2]
        sort_order = sort_order.lower()

        cache_key = f"products:{page}:{size}:{sort_field}:{sort_order}:{category}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

        products, total = get_products(
            page=page,
            size=size,
            sort_field=sort_field,
            sort_order=sort_order,
            category=category
        )

        response = {
            "page": page,
            "size": size,
            "total": total,
            "items": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "description": p.description
                } for p in products
            ]
        }
        logger.info("Found %d products", total)
        cache.set(cache_key, response)
        return response

    @api.expect(product_model)
    @jwt_required()
    def post(self):
        """Create a new product"""
        
        data = request.json
        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        logger.info("POST /api/products - Adding product: %s", name)

        if not name or not isinstance(price, (int, float)):
            api.abort(400, "Nom et prix valides requis.")

        add_product(name, price, description)
        logger.info("Product added successfully")
        return {"message": "Produit ajouté avec succès."}, 201


@api.route("/search")
class ProductSearch(Resource):
    """Product search API"""
    @jwt_required()
    def get(self):
        """Search for products by ID or name"""
        search_type = request.args.get("type")
        keyword = request.args.get("keyword")

        if search_type not in {"id", "name"} or not keyword:
            api.abort(400, "Paramètres 'type' (id|name) et 'keyword' requis.")

        try:
            results = search_product_by(search_type, keyword)
            if not results:
                return {"message": "Aucun produit trouvé."}, 404
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "description": p.description
                }
                for p in results
            ]
        except ValueError as e:
            api.abort(400, str(e))


@api.route("/<int:product_id>")
class ProductUpdate(Resource):
    """Product updatate API"""
    @jwt_required()
    def put(self, product_id):
        """Update a product by ID"""
        data = request.json
        name = data.get("name")
        price = data.get("price")
        description = data.get("description")

        success = update_product(product_id, name, price, description)
        if success:
            return {"message": "Produit mis à jour avec succès."}
        return {"error": f"Aucun produit trouvé avec l'ID {product_id}."}, 404
