"""
Main app file for product service
"""
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from flask_jwt_extended import JWTManager
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from database import init_db
from extensions import cache
from stock_api import api as service_api

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = "redis"
app.config["CACHE_REDIS_PORT"] = 6379
app.config["CACHE_DEFAULT_TIMEOUT"] = 60
cache.init_app(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def health():
    """Health of the microservice"""
    return {"message": "Stock Microservice running"}

metrics = PrometheusMetrics(app)
metrics.info('stock_app_info', 'Stock Microservice Info', version='1.0.0')

api = Api(app, title="Stock Microservice API", version="1.0", doc="/api/docs")
api.add_namespace(service_api, path="/api/stocks")

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
