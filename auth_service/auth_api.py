"""Module to handle JWT token authentification"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from flask import request
from auth_repository import authenticate_user

api = Namespace("Auth", description="Authentification simple")

user_model = api.model("User", {
    "username": fields.String(required=True),
    "password": fields.String(required=True)
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
