# 📝 Récapitulatif : Catalogue d'Événements (Polyglotte)

## 📅 Date : 18 Mai 2026
**Intervenant** : Gemini CLI (Assistance IA)

---

## 🎯 Objectif
Implémentation du Domaine 2 (Catalogue) en exploitant l'architecture polyglotte SQL + NoSQL. L'enjeu était de garantir la cohérence entre PostgreSQL (Source de Vérité) et MongoDB (Flexibilité/Géo).

---

## 🛠️ Travaux Réalisés

### 1. Schémas d'Agrégation (`src/schemas/events.py`)
*   Création de modèles Pydantic capables de fusionner les données des deux bases.
*   `EventDetail` : Inclut les champs structurels SQL (titre, dates) et les métadonnées flexibles MongoDB (lineup, accessibilité).
*   Intégration du format **GeoJSON** pour la localisation.

### 2. Implémentation du Router (`src/routes/events.py`)
*   **Transaction Bi-Base (POST `/events`)** :
    1. Validation des droits organisateur.
    2. Insertion SQL (récupération de l'ID).
    3. Insertion MongoDB (avec métadonnées polymorphes).
    4. Rollback SQL automatique si MongoDB échoue.
*   **Recherche Géospatiale (GET `/nearby`)** :
    1. Filtrage par distance via MongoDB (index `2dsphere`).
    2. Récupération des détails structurels via PostgreSQL (clause `IN`).
    3. Tri préservé par distance.
*   **Recherche Plein-Texte (GET `/search`)** : Utilisation de l'index `text` de MongoDB pour une recherche performante sur le titre et la description.
*   **CRUD complet** : Ajout des routes de mise à jour (PATCH) et de suppression (DELETE) synchronisant les deux bases.

### 3. Logique SQL Avancée
*   Utilisation de la procédure stockée `proc_annuler_evenement` lors de la suppression d'un événement pour gérer les inscriptions en cascade.

---

## 🤖 Justification de l'utilisation de l'IA

1.  **Complexité Polyglotte** : La gestion d'une transaction répartie sur deux types de bases de données (Postgres + Mongo) nécessite une rigueur logicielle importante (Atomicité relative).
2.  **Expertise Géo** : L'IA a aidé à configurer correctement les requêtes `$near` de MongoDB et à les mapper proprement vers les objets Python.
3.  **Gain de temps** : Génération rapide des schémas d'agrégation complexes qui auraient pris plusieurs heures de boilerplate manuel.

---