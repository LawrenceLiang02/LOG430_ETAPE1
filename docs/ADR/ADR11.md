# Architecture Decision Records 11

## Titre

ADR 11 - Choix de Redis Streams comme bus d’événements

## Statut

Accepté

## Contexte

Une solution de message broker légère et rapide était requise.

## Décision

Redis Streams a été retenu.

## Justification

- Facile à déployer via Docker
- Compatible avec les structures de données clés/valeurs déjà utilisées
- Permet le Pub/Sub avec persistance d’événements

## Conséquences

Tous les événements doivent être sérialisés et bien structurés pour éviter les pertes d’information.