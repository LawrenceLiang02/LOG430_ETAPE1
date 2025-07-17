# Architecture Decision Records 5

## Titre

ADR 5 - Choix de la passerelle API (Gateway)

## Statut

Accepté

## Contexte

Le projet utilise une architecture à base de microservices. Chaque service expose sa propre API, ce qui rend nécessaire une solution centralisée pour router les requêtes, gérer les en-têtes, appliquer l'authentification et éventuellement agréger les réponses. Une Gateway permet également de limiter l’exposition directe des services internes au client.

## Décision

J'ai choisi **KrakenD** comme passerelle API (API Gateway) pour centraliser l'accès aux microservices.

## Justification

- **Performance élevée** : KrakenD est conçu pour la vitesse et la faible latence.
- **Aucune logique métier** : il respecte le principe d’un gateway léger, sans interférer avec la logique des services.
- **Routage et agrégation** : facilite la redirection des appels vers les bons microservices, même avec transformation des réponses.
- **Support JWT natif** : idéal pour un système d’authentification centralisée.
- **Open Source & simple à configurer** : adapté à un projet éducatif ou léger.

## Conséquences

- Les microservices sont protégés derrière une seule interface exposée.
- La structure du système devient plus modulaire et découplée.
- L'intégration de nouveaux services est simplifiée.
