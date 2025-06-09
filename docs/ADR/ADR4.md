# Architecture Decision Record 4
## Titre
ADR 3 – Conteneurisation avec Docker Compose pour la simulation multi-sites

## Statut
Accepté

## Contexte
L’application doit représenter plusieurs entités géographiques : 3 magasins, 1 centre logistique, 1 maison mère. Chaque entité doit pouvoir être lancée indépendamment pour simuler un fonctionnement distribué.

## Décision
J'ai choisi d’utiliser Docker Compose pour lancer un conteneur par entité (magasin1, magasin2, magasin3, centre_logistique, maison_mere), chacun avec ses variables d’environnement (ROLE, LOCATION).

## Justification
- Permet de simuler plusieurs instances de l’application sur une même machine ou VM.
- Facilite le déploiement reproductible dans différents environnements.
- Prépare le système pour une architecture distribuée réelle.
- Permet d’avoir un environnement de test cohérent, isolé et scriptable.

## Conséquences
- La base de données SQLite peut être partagée via un volume Docker pour synchroniser les données.
- Possibilité d’ajouter un serveur FastAPI ou un proxy (Nginx) dans le futur.
- Les commandes peuvent être automatisées via des scripts docker-compose pour CI/CD.