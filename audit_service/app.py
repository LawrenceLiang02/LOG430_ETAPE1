"""
Main app file for audit service
"""
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from database import init_db
from audit_api import api as service_api

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

metrics = PrometheusMetrics(app, defaults_prefix=None, group_by='endpoint', register_defaults=True)
metrics.info('audit_app_info', 'Audit Service Info', version='1.0.0')

@app.route("/")
def health():
    return {"message": "Audit Microservice running"}

api = Api(app, title="Audit Microservice API", version="1.0", doc="/api/docs")
api.add_namespace(service_api, path="/api/audit")

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
