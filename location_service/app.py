"""
Main app file for location service
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

metrics = PrometheusMetrics(app, defaults_prefix=None, group_by='endpoint', register_defaults=True)
metrics.info('app_info', 'Informations de l application', version='1.0.0')

@app.route("/")
def health():
    """Health of the microservice"""
    return {"message": "Location Microservice running"}

api = Api(app, title="Locations Microservice API", version="1.0", doc="/api/docs")
api.add_namespace(service_api, path="/api/locations")

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
