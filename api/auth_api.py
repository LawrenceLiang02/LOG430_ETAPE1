"""Module to handle JWT token authentification"""
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from flask import request

api = Namespace("Auth", description="Authentification simple")

user_model = api.model("User", {
    "username": fields.String(required=True),
    "password": fields.String(required=True)
})

USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "logistique": {"password": "logi123", "role": "centre_logistique"},
    "Magasin 1": {"password": "mag1pass", "role": "magasin"},
    "Magasin 2": {"password": "mag1pass", "role": "magasin"}
}

@api.route("/login")
class Login(Resource):
    """Class for /login"""
    @api.expect(user_model)
    def post(self):
        """Method to post /login"""
        data = request.json
        user = USERS.get(data["username"])
        if not user or user["password"] != data["password"]:
            return {"error": "Identifiants invalides"}, 401

        access_token = create_access_token(identity=data["username"])
        return {"access_token": access_token}
