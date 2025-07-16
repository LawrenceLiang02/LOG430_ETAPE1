"""
Main app file for location service
"""
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api
from flask_jwt_extended import JWTManager
from prometheus_flask_exporter import PrometheusMetrics

from database import init_db
from extensions import cache
from location_api import api as service_api

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = "redis"
app.config["CACHE_REDIS_PORT"] = 6379
app.config["CACHE_DEFAULT_TIMEOUT"] = 60
cache.init_app(app)

CORS(app, resources={r"/api/*": {"origins": "*"}})

metrics = PrometheusMetrics(app)
metrics.info('locations_app_info', 'Locations Microservice Info', version='1.0.0')

api = Api(app, title="Locations Microservice API", version="1.0", doc="/api/docs")
api.add_namespace(service_api, path="/api/locations")

@app.before_request
def log_headers():
    print("------ REQUEST HEADERS ------")
    for k, v in request.headers.items():
        print(f"{k}: {v}")
    print("-----------------------------")

@app.route("/debug/headers")
def debug_headers():
    from flask import request
    return {k: v for k, v in request.headers.items()}

@app.route("/")
def health():
    """Health of the microservice"""
    return {"message": "Location Microservice running"}

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
