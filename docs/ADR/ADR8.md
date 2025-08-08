# Architecture Decision Records 8

## Titre

ADR 8 - Choix d’une Saga Orchestrée vs Saga Chorégraphiée

## Statut

Accepté

## Contexte

Pour gérer une commande client impliquant plusieurs microservices (stock, panier, vente), nous devons garantir la cohérence des opérations distribuées, même en cas d’échec partiel. Deux approches s’offrent à nous : la chorégraphie décentralisée ou l’orchestration centralisée.

## Décision

J'ai opté pour une Saga orchestrée avec un service central d’orchestration.

## Justification

- Clarté du flux : l’enchaînement des étapes est centralisé et contrôlé dans un service dédié.
- Traçabilité simplifiée : la machine d’état permet un suivi clair des transitions.
- Facilité de gestion des compensations : les erreurs sont gérées de manière déterministe au même endroit.
- Adaptée à un projet pédagogique : facilite la compréhension et le débogage.

## Conséquences

- Le service d’orchestration devient un point central de coordination (et un SPOF potentiel).
- Les services appelés doivent rester idempotents et exposer des APIs cohérentes.
- La logique métier est centralisée, ce qui peut réduire la flexibilité de chaque microservice.