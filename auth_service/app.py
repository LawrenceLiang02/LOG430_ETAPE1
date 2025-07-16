"""Authentification service"""
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api
from auth_api import api as auth_namespace
from database import init_db

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"
api = Api(app, title="Auth Service API", version="1.0")

jwt = JWTManager(app)

api.add_namespace(auth_namespace, path="/api/auth")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
