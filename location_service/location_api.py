"""API for /locations using Flask-RESTX"""
import logging
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required
from extensions import cache
from location_repository import get_all_locations, get_location_by_id, get_location_by_name

logger = logging.getLogger(__name__)

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
        logger.info("GET /api/locations - Fetching all locations")
        cache_key = "locations:all"
        cached = cache.get(cache_key)
        if cached:
            return cached

        locations = get_all_locations()
        if not locations:
            logger.error("GET /locations - Aucun magasin trouvé dans la base de données.")
            api.abort(404, "Aucun magasin trouvé.")

        result = [{"id": l.id, "name": l.name} for l in locations]
        cache.set(cache_key, result)
        logger.info("Returned %d locations", len(locations))
        return result

@api.route("/id/<int:location_id>")
class LocationById(Resource):
    """Location by id"""
    @api.doc(params={"location_id": "ID de l'emplacement"})
    @jwt_required()
    def get(self, location_id):
        """Get location by id"""
        location = get_location_by_id(location_id)
        if not location:
            api.abort(404, f"Location ID {location_id} introuvable.")
        return {"id": location.id, "name": location.name}

@api.route("/select")
class LocationSelect(Resource):
    """Location selection API route"""
    @api.doc(params={"index": "Index (1-based) of the location to select"})
    def get(self):
        """
        Select a location by 1-based index.
        Example: /locations/select?index=2
        """
        index_param = request.args.get("index", type=int)
        logger.info("GET /api/locations/select - index=%s", index_param)

        cache_key = "locations:all"
        locations = cache.get(cache_key)

        if not locations:
            logger.info("Cache miss for key %s. Fetching from DB...", cache_key)
            locations_db = get_all_locations()
            if not locations_db:
                logger.error("GET /locations/select - Aucun magasin trouvé dans la base de données.")
                api.abort(404, "Aucun magasin trouvé.")
            locations = [{"id": l.id, "name": l.name} for l in locations_db]
            cache.set(cache_key, locations)
            logger.info("Locations mises en cache avec la clé %s", cache_key)

        if index_param is None or index_param < 1 or index_param > len(locations):
            logger.warning(
                "GET /locations/select - Paramètre 'index' invalide: %s (taille liste: %d)",
                index_param, len(locations)
            )
            api.abort(400, f"Paramètre 'index' invalide. Veuillez fournir un entier entre 1 et {len(locations)}.")

        selected = locations[index_param - 1]
        logger.info("Location selected: %s", selected["name"])
        return selected

@api.route("/<string:name>")
class LocationByName(Resource):
    """Get location by name (used by other services)"""
    def get(self, name):
        """Get location by name"""
        logger.info("GET /api/locations/%s - Recherche par nom", name)
        location = get_location_by_name(name)
        if not location:
            api.abort(404, f"Emplacement '{name}' introuvable.")
        return {"id": location.id, "name": location.name}
