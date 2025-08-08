# Architecture Decision Records 10

## Titre

ADR 10 - Implémentation de CQRS dans SaleService

## Statut

Accepté

## Contexte

Les lectures sur l’état des commandes étaient fréquentes et ralentissaient les traitements métier.

## Décision
Séparer les écritures (commande) et les lectures via un Read Model.

## Justification

- Meilleures performances en lecture
- Plus grande flexibilité pour les vues (filtrage, agrégation)
- Permet de reconstituer l’état à partir du Event Store

## Conséquences

Complexité accrue (projections, synchronisation via événements) mais meilleure scalabilité.