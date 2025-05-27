# Architecture Decision Records 1

## Titre

ADR 1 - Choix de la plateforme 

## Statut

Accepté

## Contexte

Le projet consiste à créer une application de type caisse enregistreuse locale pour un petit magasin, dans un modèle 2-tiers sans serveur HTTP. L’objectif est de bâtir une base évolutive pour des versions futures (multi-succursales, e-commerce).

## Décision

J'ai choisi la plateforme **Python** avec l'ORM **SQLAlchemy** et la base de données **SQLite** pour l’environnement local.

## Justification

- **Python** : langage simple et expressif, très utilisé pour des projets rapides.
- **SQLAlchemy** : ORM mature et compatible avec plusieurs SGBD (SQLite, PostgreSQL, etc.), facilite la persistance tout en gardant l’indépendance du SGBD.
- **SQLite** : SGBD léger, sans configuration serveur, idéal pour une application locale.

## Conséquences

- L’application est facilement portable (fonctionne sur Windows/macOS/Linux).
- Le système est prêt pour évoluer vers PostgreSQL si nécessaire sans changements majeurs.
- Le code reste simple, compréhensible et facilement testable.