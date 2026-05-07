# 🚀 STACK TECHNIQUE & LANGAGES

Ce document détaille les choix technologiques retenus pour le projet **Eventry**, ainsi que les bibliothèques structurantes qui permettront de répondre aux exigences de performance et de maintenabilité.

## 1. FRONTEND : React (Vite.js)

Le frontend est conçu comme une **Single Page Application (SPA)** moderne, rapide et optimisée.

* **Framework :** [React](https://react.dev/) pour sa gestion efficace du DOM virtuel et son écosystème de composants.
* **Outil de Build :** [Vite.js](https://vitejs.dev/) pour des builds de production optimisés, garantissant une meilleure expérience de développement que CRA.
* **Langage :** **JavaScript (ES6+)** ou **TypeScript**.
* **Stylisation :** [Tailwind CSS](https://tailwindcss.com/) pour une interface 100% personnalisée, évitant les pièges des templates génériques interdits par le sujet.
* **Gestion d'état & Fetching :** `Axios` pour les requêtes HTTP et `React Query` (TanStack) pour la mise en cache des données et la synchronisation avec l'API.

## 2. BACKEND : Python (FastAPI)

Le backend est une **API REST** asynchrone, conçue pour supporter des charges de lecture massives et une intégration fluide avec PostgreSQL et MongoDB.

* **Langage :** **Python 3.10+** pour sa lisibilité et sa puissance dans le traitement des données.
* **Framework :** [FastAPI](https://fastapi.tiangolo.com/). 
    * **Justification :** Rapidité d'exécution (basé sur Starlette et Pydantic), support natif de l'asynchrone (`async/await`) crucial pour les accès bases de données non-bloquants, et génération automatique de la documentation Swagger/OpenAPI.
* **Validation de données :** `Pydantic` pour la définition de schémas de données stricts, assurant l'intégrité des données entrantes.
* **Serveur ASGI :** `Uvicorn` pour la gestion des requêtes asynchrones en environnement de développement et production.

## 3. DATA ACCESS LAYER (DAL)

Pour gérer l'aspect polyglotte, nous utilisons des connecteurs spécifiques :

* **SQL (PostgreSQL) :** [SQLAlchemy](https://www.sqlalchemy.org/) ou [SQLModel](https://sqlmodel.tiangolo.com/) comme ORM pour mapper nos objets Python vers nos tables 3NF, tout en permettant l'écriture de requêtes complexes en SQL brut si nécessaire.
* **NoSQL (MongoDB) :** [Motor](https://motor.readthedocs.io/) (pilote asynchrone pour MongoDB) ou [Beanie](https://beanie-odm.dev/) (ODM basé sur Pydantic) pour manipuler les documents JSON de manière intuitive et asynchrone.

## 4. ENVIRONNEMENT & DEVOPS

* **Conteneurisation :** [Docker](https://www.docker.com/) & **Docker Compose** pour orchestrer les quatre services (Frontend, Backend, Postgres, MongoDB) et garantir le fonctionnement "en une commande" exigé.
* **Package Management :** `pip` avec un fichier `requirements.txt` ou `uv` (recommandé pour la vitesse) côté Backend, et `npm` ou `pnpm` côté Frontend.
* **Documentation API :** Accessible via `/docs` (Swagger UI) pour faciliter les tests par le correcteur.