# 🐳 Guide d'utilisation Docker - Eventry

Ce guide est destiné aux membres de l'équipe pour gérer l'environnement de développement du projet via Docker.

---

## 🚀 Commandes de base

### 1. Démarrer le projet (Première fois ou modification)
Cette commande télécharge les images, construit les conteneurs et les lance en arrière-plan.
```bash
docker-compose up --build -d
```

### 2. Éteindre les conteneurs
Arrête les services proprement sans supprimer les données.
```bash
docker-compose down
```

### 3. Réinitialisation complète (⚠️ Supprime les données)
Arrête les conteneurs et **supprime tous les volumes** (utile pour relancer les scripts de seed SQL/NoSQL si vous avez fait des erreurs).
```bash
docker-compose down -v
```

---

## 🛠️ Accès aux bases de données (Ligne de commande)

Pour exécuter des requêtes manuellement, placez-vous à la racine du projet (`Eventry/`) et utilisez les commandes suivantes :

### 🍃 MongoDB
```bash
docker exec -it eventry-nosql mongosh -u admin -p admin1234 --authenticationDatabase admin
```

### 🐘 PostgreSQL
```bash
docker exec -it eventry-sql psql -U admin -d eventry_db
```

> **Note** : Pour sortir d'un conteneur, utilisez la combinaison de touches `Ctrl + D`.

---

## 🖥️ Connexion via interfaces graphiques (GUI)

### 🧩 MongoDB Compass
Après avoir lancé les conteneurs, utilisez ce lien de connexion (URI) :
`mongodb://admin:admin1234@localhost:27017/?authSource=admin`

### 🐘 PgAdmin / DBeaver (PostgreSQL)

**Configuration commune :**
- **Host (Serveur)** : `localhost`
- **Port** : `5432`
- **Utilisateur** : `admin`
- **Mot de passe** : `admin1234`
- **Base de données** : `eventry_db`

---

## 💡 Rappels importants
- **Fichier .env** : Ne modifiez pas les credentials sans prévenir l'équipe, car ils sont synchronisés entre le Backend et les Bases de données.
- **Port 8000** : Le backend est accessible sur `http://localhost:8000`.
- **Port 5173** : Le frontend est accessible sur `http://localhost:5173` (via Nginx).
- **Problèmes ?** En cas de bug bizarre, la commande magique est souvent `docker-compose down -v && docker-compose up --build -d`.

*Pour toute recherche plus poussée, consultez la documentation officielle de Docker ou demandez à l'IA du projet.*
