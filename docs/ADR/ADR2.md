# Architecture Decision Records 1

## Titre

ADR 2 - Séparation des responsabilités entre présentation, logique métier et persistance

## Statut

Accepté

## Contexte

Le système implémente une architecture 2-tiers. Pour assurer la maintenabilité, l’évolutivité et les tests unitaires, une bonne séparation des responsabilités est nécessaire.

## Décision

J'ai structuré l’application en **trois couches principales** :
- **Présentation** : interface utilisateur console (ex. via `main()` ou `app.py`)
- **Logique métier** : services dans `service_layer/store_service.py`
- **Persistance** : modèles ORM et sessions SQLAlchemy dans `data_class/models.py`

## Justification

- Favorise les tests unitaires (on peut tester la logique sans dépendre de la base).
- Prépare à une éventuelle migration vers une architecture 3-tiers (REST API ou interface web).
- Permet de maintenir une base de code modulaire et propre (clean architecture).

## Conséquences

- L’ajout de nouvelles fonctionnalités (par exemple : filtres de recherche) peut se faire sans modifier la base ou l’interface.
- L’intégration de validations ou de règles métier complexes est centralisée dans la couche service.