"""Main app file for client service"""
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_jwt_extended import JWTManager

from client_api import api as client_namespace
from database import init_db

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # à extraire dans .env idéalement
jwt = JWTManager(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})

api = Api(app, title="Client Microservice API", version="1.0", doc="/api/docs")
api.add_namespace(client_namespace, path="/api/clients")

@app.route("/")
def health():
    return {"message": "Client Microservice running"}

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
