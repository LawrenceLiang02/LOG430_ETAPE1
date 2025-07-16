"""API for client creation"""
from flask_restx import Namespace, Resource, fields
from flask import request
from client_repository import create_client, get_client_by_username, get_all_clients
api = Namespace("Clients", description="Client account management")

client_model = api.model("Client", {
    "username": fields.String(required=True),
    "password": fields.String(required=True),
    "email": fields.String(required=True)
})

@api.route("/")
class ClientCreate(Resource):
    @api.expect(client_model)
    def post(self):
        """Create a new client account"""
        data = request.json
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")

        if get_client_by_username(username):
            api.abort(400, "Nom d'utilisateur déjà utilisé")

        try:
            client = create_client(username, password, email)
            return {"message": "Client créé", "id": client.id}, 201
        except Exception as e:
            api.abort(500, f"Erreur lors de la création: {str(e)}")
    
    def get(self):
            """Get all clients"""
            try:
                clients = get_all_clients()
                return [{"id": c.id, "username": c.username, "email": c.email} for c in clients]
            except Exception as e:
                api.abort(500, f"Erreur lors de la récupération: {str(e)}")