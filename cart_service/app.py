"""Cart service app"""
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_jwt_extended import JWTManager
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from database import init_db
from cart_api import api as cart_namespace

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"

jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def health():
    """Shows health of the system"""
    return {"message": "Cart Service running"}

api = Api(app, title="Cart Service API", version="1.0", doc="/api/docs")
api.add_namespace(cart_namespace, path="/api/cart")

metrics = PrometheusMetrics(app, defaults_prefix=None, group_by='endpoint', register_defaults=True)
metrics.info('cart_service_info', 'Cart Service Info', version='1.0.0')

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
