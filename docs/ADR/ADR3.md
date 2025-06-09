# Architecture Decision Record 3

## Titre
ADR 3 – Choix d’une architecture modulaire inspirée de DDD

## Statut
Accepté

## Contexte
L’application initiale en 2-tiers (interface + accès BD) devenait difficile à maintenir et à faire évoluer pour une logique multi-magasins, multi-rôles (maison mère, centre logistique, etc.) et une séparation claire des responsabilités métier.

## Décision
J'ai adopté une architecture modulaire inspirée du Domain-Driven Design (DDD), où chaque domaine fonctionnel (produits, ventes, stock, etc.) a ses propres dossiers contenant ses vues (UI), services (logique métier) et accès BD (repository).

## Justification
Permet une clarté dans l’organisation du code par domaine métier.

Facilite la maintenance, l’extensibilité, et l’implémentation future d’une API REST.

Encourage la séparation des préoccupations : la logique métier est testable indépendamment de l’IHM.

Prépare le terrain pour une architecture hexagonale ou une migration vers le web.

## Conséquences
L’ajout de nouvelles fonctionnalités (tableau de bord, rapports, réapprovisionnement, etc.) est plus simple.

Les développeurs peuvent travailler en parallèle sur différents domaines.

La structure facilite l’évolution vers des microservices ou un système orienté événements si nécessaire.

