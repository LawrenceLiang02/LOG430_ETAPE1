# Architecture Decision Records 6

## Titre

ADR 6 - Choix du reverse proxy

## Statut

Accepté

## Contexte

Le système inclut plusieurs instances de services et de gateways, ce qui nécessite une gestion du trafic HTTP en amont. Un reverse proxy permet de gérer la répartition des charges, le SSL/TLS, et les redirections d'URL.

## Décision

J'ai choisi **NGINX** comme serveur proxy inverse devant KrakenD.

## Justification

- **Stabilité et robustesse** : largement utilisé en production dans l’industrie.
- **Répartition de charge (load balancing)** : NGINX peut distribuer le trafic vers plusieurs instances KrakenD.
- **Terminaison TLS** : permet de gérer les certificats HTTPS indépendamment des services.
- **Cache statique et compression** : peut optimiser les performances globales si nécessaire.

## Conséquences

- Le système devient plus sécurisé grâce à la terminaison TLS.
- NGINX agit comme point d'entrée unique, simplifiant la configuration côté client.
- On peut facilement scaler horizontalement les instances de KrakenD.
