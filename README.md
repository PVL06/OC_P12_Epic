# OC Projet 12: Epic Event

## :v:Présentation du projet:


## :arrow_heading_down:Installation
Récupération du dépôt en local avec Git.
```
https://github.com/PVL06/OC_P12_Epic.git
```
Si uv non installé:
- Installation d'uv:
https://github.com/astral-sh/uv
- Alternative:
Créer et activer un environnement virtuel et installer les dépendances du fichier requirements.txt. Lancer les commandes avec python à la place de uv run.
1. Serveur:

- Création du fichier de configuration .env:
```
# DATABASE CONFIG
DB_USER = postgres
DB_PWD = ******
DB_HOST = localhost:5432

# DATABASE NAMES
DB_ROOT = postgres
DB_APP = epic
DB_TEST = epic_test

# FIRST USER, WARNING: CHANGE PASSWORD IN FIRST CONNEXION
USER_NAME = epic
USER_EMAIL = epic@epic.com
USER_PASSWORD = *******

# SECRET FOR TOKEN JWT
SECRET_KEY = "secret"

# SENTRY DSN
SENTRY_DSN = sentry url
```
- Initialisation de la base de donnée postgresql
Création de la base de donnée de l'application et des tables
```
uv run init_db.py
```
- Lancement du serveur
```
uv run server_epic.py
```

2. Lancement de l'application client:

```
uv run cli_epic.py --help
```

## Utilisation

Commandes:
- login
- logout
- collab
- client
- contract
- event

Voir les options pour chaque commande avec --help (filtres, création, mise a jour et suppression)