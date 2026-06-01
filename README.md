# 🎫 Eventry : Find Events Anywhere

**Eventry** est une plateforme moderne de découverte, d'inscription et d'évaluation d'événements culturels et festifs. Ce projet a été réalisé dans le cadre du module **Bases de Données Avancées** pour démontrer la puissance d'une architecture **polyglotte** (SQL + NoSQL).

---

## 🏗️ Architecture & Technologies

Le projet repose sur une séparation stricte des responsabilités entre deux moteurs de base de données :

- **PostgreSQL** : Source de vérité pour le transactionnel (identités, inscriptions, lieux).
- **MongoDB** : Couche flexible pour le catalogue (métadonnées polymorphes), la recherche géospatiale et les avis communautaires.

### Stack Technique
*   **Backend** : Python 3.10+ avec [FastAPI](https://fastapi.tiangolo.com/) (Asynchrone).
*   **Frontend** : React avec [Vite.js](https://vitejs.dev/) et [Tailwind CSS](https://tailwindcss.com/).
*   **Infrastructure** : [Docker](https://www.docker.com/) & Docker Compose.
*   **Données** : PostgreSQL 15 & MongoDB 6.0.

---

## 🚀 Installation et Démarrage

### 📋 Prérequis
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installé et lancé.
*   [Git](https://git-scm.com/) installé.

### ⚙️ Configuration initiale (Obligatoire)
Avant de lancer les conteneurs, vous devez configurer vos variables d'environnement :

1.  À la racine du projet, créez un fichier nommé `.env`.
2.  Copiez l'intégralité du contenu de `.env.example` vers votre nouveau fichier `.env`.
    ```bash
    cp .env.example .env
    ```
    *(Note : Les identifiants par défaut sont `admin` / `admin1234` pour faciliter le test en local).*

### ⚡ Lancement du projet
Lancez l'ensemble de l'infrastructure en une seule commande :
```bash
docker-compose up --build -d
```

*   **Frontend** : [http://localhost:5173](http://localhost:5173)
*   **Backend (API)** : [http://localhost:8000](http://localhost:8000)
*   **Documentation Swagger** : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📖 Guides pour l'Équipe

Pour faciliter la collaboration, plusieurs guides détaillés sont disponibles dans le projet :

- 🐳 **[Guide Docker](./docker/DOCKER_GUIDE.md)** : Comment gérer les conteneurs, accéder aux bases de données et se connecter via MongoDB Compass ou DBeaver.
- 🛠️ **[Guide Git](./docs/specification/git-guide.md)** : Comment travailler proprement sur les branches, nommer vos commits et faire des Pull Requests.
- 🐘 **[Documentation PostgreSQL](./db/sql/readme.md)** : Détails sur les procédures stockées, triggers et vues.
- 🍃 **[Documentation MongoDB](./db/nosql/readme.md)** : Détails sur les index géospatiaux et le polymorphisme des données.

---

## 👥 L'Équipe Eventry
*   **Rayhan** - Lead Tech / Architecture
*   **Amine** - Lead Data / Backend
*   **Zackaria** - Lead Frontend / UI
*   **Rayan** - Lead Produit / QA

---

## 📝 Licence & Politique IA
L'utilisation de l'IA est autorisée mais doit être documentée dans le fichier `AI_LOGS.md` à la racine, conformément aux règles du projet.
