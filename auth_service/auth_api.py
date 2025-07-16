"""Module to handle JWT token authentification"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask import request
from auth_repository import authenticate_user, create_client, get_client_by_username

api = Namespace("Auth", description="Authentification simple")

user_model = api.model("User", {
    "username": fields.String(required=True),
    "password": fields.String(required=True)
})

user_response_model = api.model("UserInfo", {
    "id": fields.Integer,
    "username": fields.String,
    "role": fields.String,
})

@api.route("/login")
class Login(Resource):
    """Classe pour l'authentification des utilisateurs"""
    @api.expect(user_model)
    def post(self):
        """Login et génération du token JWT"""
        data = request.json
        username = data.get("username")
        password = data.get("password")

        user = authenticate_user(username, password)
        if not user:
            return {"error": "Identifiants invalides"}, 401

        access_token = create_access_token(
            identity=user.username,
            additional_claims={"role": user.role}
        )
        return {"access_token": access_token}

@api.route("/register")
class ClientRegister(Resource):
    """class to create client profile"""
    @api.expect(user_model)
    @api.response(201, "Client créé")
    @api.response(400, "Nom d'utilisateur déjà utilisé")
    def post(self):
        """Method to create client profile"""
        data = request.json
        new_client = create_client(data["username"], data["password"])
        if not new_client:
            return {"error": "Nom d'utilisateur déjà pris"}, 400
        return {"message": "Client créé", "id": new_client.id}, 201
    
@api.route("/me")
class ClientProfile(Resource):
    """class to get client profile"""
    @jwt_required()
    @api.marshal_with(user_response_model)
    def get(self):
        """Method to get client profile"""
        username = get_jwt_identity()
        client = get_client_by_username(username)
        if not client:
            return {"error": "Accès refusé"}, 403
        return client
