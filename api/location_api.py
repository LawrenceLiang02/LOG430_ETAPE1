"""API for /locations using Flask-RESTX"""
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required
from service_layer.location_repository import get_all_locations

api = Namespace("Locations", description="Location operations")

location_model = api.model("Location", {
    "id": fields.Integer,
    "name": fields.String
})


@api.route("/")
class LocationList(Resource):
    """Location list class"""
    @api.marshal_list_with(location_model)
    @jwt_required()
    def get(self):
        """List all available locations"""
        locations = get_all_locations()
        if not locations:
            api.abort(404, "Aucun magasin trouvé.")
        return locations


@api.route("/select")
class LocationSelect(Resource):
    """Location selection API route"""
    @api.doc(params={"index": "Index (1-based) of the location to select"})
    @jwt_required()
    def get(self):
        """
        Select a location by 1-based index.
        Example: /locations/select?index=2
        """
        index_param = request.args.get("index", type=int)
        locations = get_all_locations()

        if not locations:
            api.abort(404, "Aucun magasin trouvé.")

        if index_param is None or index_param < 1 or index_param > len(locations):
            api.abort(400, f"Paramètre 'index' invalide. Veuillez fournir un entier entre 1 et {len(locations)}.")

        selected = locations[index_param - 1]
        return {"id": selected.id, "name": selected.name}
