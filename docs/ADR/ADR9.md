# Architecture Decision Records 9

## Titre

ADR 9 - Persistance de la machine d’état avec SQLite

## Statut

Accepté

## Contexte

La saga doit maintenir l’état courant de chaque commande (créée, stock réservé, paiement OK, confirmée, échec). Cet état doit être consultable a posteriori et résilient aux pannes.

## Décision

J'ai choisi de persister la machine d’état dans une base SQLite locale dans le microservice `saga_service`.

## Justification

- Simplicité d’utilisation : pas besoin de configurer un serveur SQL externe.
- Rapide et léger : idéal pour un usage de laboratoire.
- Résilience : permet de redémarrer le service sans perdre l’état de la saga.
- Lecture facile : les états et les logs sont facilement consultables pour le diagnostic.

## Conséquences

- Non adapté à un usage distribué ou haute-disponibilité en production.
- Un seul service peut modifier l’état à la fois (pas de concurrence distribuée).
- En production, une base SQL robuste (PostgreSQL, etc.) serait recommandée.