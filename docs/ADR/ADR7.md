# Architecture Decision Records 7

## Titre

ADR 7 - Choix du système de cache

## Statut

Accepté

## Contexte

Certains services, notamment le service d’authentification, doivent manipuler des sessions, des jetons JWT ou d’autres données temporaires fréquemment consultées. Il est nécessaire d’utiliser un système de cache performant pour limiter les appels inutiles à la base de données.

## Décision

J'ai choisi **Redis** comme système de cache partagé entre les services.

## Justification

- **Ultra rapide** : stockage en mémoire, temps de réponse très faible.
- **Clé-valeur simple** : adapté pour stocker des tokens JWT ou des sessions utilisateur.
- **Partagé entre services** : permet de centraliser certaines données temporaires.
- **Support natif dans Flask et KrakenD** : facile à intégrer dans notre pile actuelle.

## Conséquences

- Les performances globales sont améliorées (moins d’accès DB).
- La gestion des tokens ou sessions est centralisée et cohérente.
- Redis doit être déployé comme un service externe persistant ou volatile.
