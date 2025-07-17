"""Authentification service"""
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from auth_api import api as auth_namespace
from database import init_db

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"

jwt = JWTManager(app)

@app.route("/")
def health():
    """Auth health check"""
    return {"message": "Auth service running"}

api = Api(app, title="Auth Service API", version="1.0", doc="/api/docs")
api.add_namespace(auth_namespace, path="/api/auth")

metrics = PrometheusMetrics(app, defaults_prefix=None, group_by='endpoint', register_defaults=True)
metrics.info('auth_service_info', 'Auth service metrics info', version='1.0.0')

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
