# LOG430 - Étape 1
Nom: Lawrence Liang

## Description
Ceci est une application console qui gère l'inventaire et les ventes d'une compagnie. 

Dans ce projet, j'applique:
- Un workflow CI/CD retrouvé dans la page "Actions" de GitHub
- Un conteneur Docker qui est publié sur DockerHub
- Une application CRUD qui gère les ventes et les produits
- Des tests unitaires automatisés sur chaque branche à chaque commit.
- Automatiser l'utilisation d'un Linter pour vérifier mon code source

Les piles technologiques utilisé sont:
- Python pour la logique
- SQLite pour la base de donnée

Ce projet a une architecture 2-tier.

## L'architecture



## Instruction d'installation et execution

### Cloner le projet
`git clone https://github.com/LawrenceLiang02/LOG430_ETAPE1.git`

### Installer un .venv
[Suivre ce lien](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) pour installer un .venv.

### Installer les librairies:
La commande dans le terminal est la suivante: `pip install -r requirements.txt`

### Build docker and run
`docker-compose build`
`docker-compose run --rm app`

### Executer l'application localement

Terminal: `python app.py`

### Executer les tests unitaires manuellement

Terminal: `pytest`

## CI/CD Pipeline:

Le pipeline CI/CD vérifie d'abord le système de lint, spécifiquement PyLint. Ensuite, il exécute les tests dans `test_app.py`, puis il buildera le docker-compose. 

## Mettre à jour les requirements.txt:

`pip freeze > requirements.txt`