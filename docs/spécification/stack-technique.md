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

# Justification du choix NoSQL : MongoDB (Base Documentaire)

## Pourquoi une base NoSQL est nécessaire

Eventry manipule deux familles de données aux natures fondamentalement différentes :

- Des données **structurées et relationnelles** (utilisateurs, inscriptions, lieux) → PostgreSQL
- Des données **flexibles, polymorphes et à fort volume de lecture** (métadonnées d'événements,
  avis communautaires) → MongoDB

La coexistence des deux est justifiée par des besoins métiers qui ne peuvent pas être
efficacement couverts par un seul paradigme.

---

## Pourquoi MongoDB plutôt que les autres types NoSQL

### Comparaison des paradigmes

| Type         | Moteur exemple  | Adapté pour                              | Inadapté pour Eventry car...                                      |
| :----------- | :-------------- | :--------------------------------------- | :---------------------------------------------------------------- |
| **Documentaire** | **MongoDB** | Documents JSON flexibles, géospatial, agrégations | —                                                        |
| Clé-Valeur   | Redis           | Cache, sessions, pub/sub                 | Pas de requêtes complexes, pas de documents imbriqués             |
| Colonnes     | Cassandra       | Séries temporelles, écritures massives   | Pas de schéma flexible, requêtes analytiques limitées             |
| Graphe       | Neo4j           | Relations sociales, recommandations      | Surengineering pour notre périmètre, pas de géospatial natif      |

> Redis aurait été pertinent pour un système de cache de sessions, mais ne peut pas stocker
> des documents enrichis comme des avis avec sous-documents et notes détaillées.  
> Neo4j serait pertinent pour un moteur de recommandation basé sur un graphe social,
> fonctionnalité hors périmètre du projet.

---

## Les trois justifications métier de MongoDB pour Eventry

### 1. Polymorphisme structurel des métadonnées d'événements

Un **Festival**, une **Exposition** et une **Boîte de nuit** ne partagent pas les mêmes attributs.
Un schéma SQL forcerait des dizaines de colonnes NULL ou un pattern EAV
(Entity-Attribute-Value) reconnu comme anti-performant.

MongoDB permet des documents de structure variable selon le type d'événement :

```json
// Métadonnées d'un Festival
{
  "event_id": 12,
  "type": "festival",
  "metadata": {
    "lineup": ["DJ Snake", "Aya Nakamura"],
    "camping_disponible": true,
    "nombre_scenes": 3,
    "dress_code": null
  }
}
```

```json
// Métadonnées d'une Exposition
{
  "event_id": 27,
  "type": "exposition",
  "metadata": {
    "artistes_exposes": ["Basquiat", "Banksy"],
    "type_oeuvres": "Peinture contemporaine",
    "visite_guidee_disponible": true,
    "dress_code": null
  }
}
```

```json
// Métadonnées d'une Boîte de nuit
{
  "event_id": 43,
  "type": "boite_de_nuit",
  "metadata": {
    "genres_musicaux": ["Techno", "House"],
    "dress_code": "Tenue correcte exigée",
    "age_minimum": 21,
    "table_vip_disponible": true
  }
}
```

> C'est l'argument central : le modèle documentaire est le seul à absorber nativement
> ce polymorphisme sans dégradation de schéma.

---

### 2. Recherche géospatiale native (feature métier critique)

La fonctionnalité **"Trouver des événements autour de moi"** repose sur des index `2dsphere`
de MongoDB, permettant des requêtes de proximité sans extension externe :

```javascript
// Trouver tous les événements dans un rayon de 10 km autour d'une position
db.events_catalog.find({
  "location": {
    $near: {
      $geometry: { type: "Point", coordinates: [2.3522, 48.8566] },
      $maxDistance: 10000
    }
  }
})
```

> Cette opération métier repose **principalement sur MongoDB**,
> satisfaisant l'exigence du sujet sur l'exploitation effective des spécificités du moteur.

---

### 3. Documents auto-contenus pour les avis (optimisation lecture)

Les avis ont une structure imbriquée naturelle (note globale, notes détaillées par critère,
réponse de l'organisateur, likes) et sont consultés massivement en lecture par tous les visiteurs.

MongoDB stocke chaque avis comme un document auto-contenu, évitant les jointures :

```json
{
  "_id": "ObjectId(...)",
  "event_id": 42,
  "user_id": 17,
  "pseudo": "Lucas_B",
  "note_globale": 4,
  "notes_detail": {
    "ambiance": 5,
    "organisation": 4,
    "rapport_qualite_prix": 3
  },
  "contenu": "Super festival, ambiance incroyable mais files d'attente longues.",
  "likes": 12,
  "date_publication": "2026-04-15T20:00:00Z",
  "reponse_organisateur": {
    "contenu": "Merci pour votre retour, nous travaillons sur les files d'attente !",
    "date": "2026-04-16T09:00:00Z"
  }
}
```

> Un seul appel MongoDB retourne l'avis complet avec sa réponse et ses likes,
> sans aucune jointure. Pattern optimal pour un usage read-heavy.

---

## Exploitations spécifiques du moteur MongoDB dans Eventry

| Spécificité MongoDB       | Usage dans Eventry                                              |
| :------------------------ | :-------------------------------------------------------------- |
| Index `2dsphere`          | Recherche géospatiale (CAT-03)                                  |
| Aggregation Framework     | Note moyenne par événement, top événements du mois (DASH-02)    |
| Index TTL                 | Purge automatique des événements archivés après 2 ans           |
| Index full-text           | Recherche par mot-clé dans les titres et descriptions (CAT-02)  |
| Documents imbriqués       | Avis avec réponse organisateur et notes détaillées (SOC-01)     |