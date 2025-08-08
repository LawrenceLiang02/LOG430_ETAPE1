"""API for /notification using Flask-RESTX"""
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required
from notification_repository import create_notification, get_all_notifications

api = Namespace("Notifications", description="Gestion des notifications envoyées")

notification_model = api.model("Notification", {
    "event_type": fields.String(required=True, description="Type d'événement"),
    "message": fields.String(required=True, description="Message de la notification"),
    "recipient": fields.String(required=True, description="Destinataire de la notification")
})

@api.route("/")
class NotificationList(Resource):
    """Get notificaiton list"""
    @jwt_required()
    def get(self):
        """Lister toutes les notifications enregistrées"""
        return get_all_notifications()

    @api.expect(notification_model)
    def post(self):
        """Recevoir une nouvelle notification (simule un envoi)"""
        data = request.json
        event_type = data.get("event_type")
        message = data.get("message")
        recipient = data.get("recipient")

        if not all([event_type, message, recipient]):
            api.abort(400, "Champs requis manquants.")

        create_notification(event_type, message, recipient)
        return {"message": "Notification enregistrée (envoi simulé)."}, 201
