"""Cart service app"""
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_jwt_extended import JWTManager

from database import init_db
from cart_api import api as cart_namespace

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # à externaliser
jwt = JWTManager(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})

api = Api(app, title="Cart Service API", version="1.0", doc="/api/docs")
api.add_namespace(cart_namespace, path="/api/cart")

@app.route("/")
def health():
    """Shows health of hte system"""
    return {"message": "Cart Service running"}

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
