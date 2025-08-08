"""API for audit"""
from flask_restx import Namespace, Resource, fields
from audit_repository import get_all_logs

api = Namespace("Audit", description="Audit event operations")

audit_model = api.model("AuditLog", {
    "id": fields.Integer(readonly=True),
    "event_type": fields.String(required=True),
    "payload": fields.String(required=True),
    "timestamp": fields.DateTime
})

@api.route("/logs")
class AuditLogList(Resource):
    """List of audit logs"""
    @api.marshal_list_with(audit_model)
    def get(self):
        """Return all audit logs"""
        return get_all_logs()
