# 🍃 MongoDB - Flexibilité & Performance Analytique

Ce dossier contient les scripts d'initialisation de la base de données documentaire MongoDB pour le projet **Eventry**.

## 🎯 Pourquoi MongoDB ?

Conformément à la stratégie de persistance polyglotte du projet, MongoDB est utilisé pour :
1. **Le polymorphisme** : Stocker des métadonnées d'événements dont la structure varie (Festival vs Exposition).
2. **Le Géospatial** : Permettre la recherche de proximité "autour de moi".
3. **Le Social (Read-Heavy)** : Stocker les avis et réponses de manière auto-contenue pour optimiser les performances de lecture.

---

## 🗃️ Collections et Modèles

### 1. `events_catalog`
Cette collection enrichit les données de PostgreSQL.
- **Clé de liaison** : `event_id` (référence SQL).
- **Flexibilité** : Le champ `metadata` contient les attributs spécifiques au type d'événement.
- **Géo** : Utilise le format GeoJSON `Point` pour le champ `location`.

### 2. `avis`
Stocke l'expérience utilisateur.
- **Structure imbriquée** : Contient les `notes_detail`, les `likes` et la `reponse_organisateur`.
- **Atomicité** : Un utilisateur ne peut laisser qu'un seul avis par événement (index unique composé).

---

## ⚡ Exploitation des Spécificités

Le script `init-mongo.js` configure les fonctionnalités avancées suivantes :

### Indexation
- **Index `2dsphere`** : Sur `location` pour les requêtes `$near` et `$geoWithin`.
- **Index Full-Text** : Sur le champ `search_text` pour la recherche par mot-clé globale.
- **Index TTL** : Sur `published_at` avec une expiration de 3 ans pour la purge automatique des données anciennes (conformité RGPD/Maintenance).

### Pipelines d'Agrégation
Des exemples d'agrégations sont fournis dans le script pour :
- Calculer les moyennes de notes pondérées par critères.
- Générer les statistiques du dashboard organisateur en combinant les données sociales.

---

## 🧪 Seed Data
Le jeu de données initial est synchronisé avec les IDs du script PostgreSQL pour permettre des tests d'intégration immédiats sur les événements "Nuit Électro" et "Expo Basquiat".

---

## 🚀 Utilisation

Pour initialiser la base de données manuellement :
```bash
mongosh init-mongo.js
```
*Note : Dans l'environnement Docker du projet, MongoDB utilise les scripts présents dans ce dossier pour son initialisation initiale.*
