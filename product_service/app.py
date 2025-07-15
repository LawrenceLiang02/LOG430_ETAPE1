"""
Main app file for product service
"""
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from prometheus_flask_exporter import PrometheusMetrics
from database import init_db
from extensions import cache
from product_api import api as service_api

app = Flask(__name__)
app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = "redis"
app.config["CACHE_REDIS_PORT"] = 6379
app.config["CACHE_DEFAULT_TIMEOUT"] = 60
cache.init_app(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})

metrics = PrometheusMetrics(app)
metrics.info('product_app_info', 'Product Microservice Info', version='1.0.0')

api = Api(app, title="Product Microservice API", version="1.0", doc="/api/docs")
api.add_namespace(service_api, path="/api/products")

@app.route("/")
def health():
    """Health of the microservice"""
    return {"message": "Products Microservice running"}

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
