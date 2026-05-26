# 📝 Récapitulatif : Module Social (Avis & Réponses)

## 📅 Date : 18 Mai 2026
**Intervenant** : Gemini CLI (Assistance IA)

---

## 🎯 Objectif
Implémentation du Domaine 4 (Social) en exploitant la complémentarité SQL/NoSQL. L'objectif était de stocker des avis enrichis dans MongoDB tout en garantissant la légitimité des auteurs via PostgreSQL.

---

## 🛠️ Travaux Réalisés

### 1. Modélisation Documentaire (`src/schemas/reviews.py`)
*   **Flexibilité NoSQL** : Utilisation de modèles Pydantic pour structurer les documents `avis` incluant des notes détaillées (ambiance, organisation, prix) et un sous-document pour la réponse organisateur.
*   **Dénormalisation** : Stockage du pseudo et de l'avatar de l'utilisateur directement dans MongoDB lors de la création pour optimiser les performances de lecture (évite une jointure avec Postgres à chaque affichage d'avis).

### 2. Implémentation du Router (`src/routes/reviews.py`)
*   **Validation Croisée (Cross-DB)** : 
    *   Avant d'insérer un avis dans MongoDB, l'API vérifie dans PostgreSQL que l'utilisateur possède une inscription `confirmee` ET que l'événement est déjà terminé (`date_fin < NOW()`).
*   **CRUD Social** :
    *   `GET /events/{id}/reviews` : Lecture performante avec tri chronologique.
    *   `POST /events/{id}/reviews` : Création sécurisée avec dénormalisation.
    *   `PATCH` / `DELETE` : Protection stricte (seul l'auteur peut modifier/supprimer).
*   **Réponse Organisateur** : 
    *   `POST /reviews/{id}/reply` : Vérification en SQL que l'utilisateur est bien l'organisateur **de l'événement spécifique** lié à l'avis avant d'autoriser la réponse dans MongoDB.

### 3. Résolution de Problèmes Critiques (Bug Fix)
*   **Sérialisation des IDs MongoDB** : Résolution du conflit entre `_id` (format BSON interne) et `id` (attendu par le client et les tests). Correction apportée via le `ConfigDict(populate_by_name=True)` et un mapping explicite dans le router pour garantir la visibilité du champ `id` dans le JSON final.
*   **Validation Pydantic V2** : Mise à jour des schémas vers la syntaxe Pydantic V2 (`model_config` au lieu de la classe `Config` dépréciée).

---

## ✅ Validation (Tests Automatisés)
**Fichier : `tests/test_reviews.py` (4 / 4 Tests PASSED)**
1.  **Cycle Complet** : Création d'un événement fini -> Inscription -> Dépôt d'avis -> Réponse organisateur. ✅
2.  **Sécurité Date** : Blocage du dépôt d'avis si l'événement n'est pas terminé. ✅
3.  **Sécurité Inscription** : Blocage du dépôt d'avis si l'utilisateur n'est pas inscrit. ✅
4.  **Lecture** : Récupération correcte des avis avec les infos utilisateurs intégrées. ✅

---

## 🤖 Justification de l'utilisation de l'IA
1.  **Maîtrise de l'Architecture Polyglotte** : L'IA a assuré la cohérence des flux de données entre MongoDB et PostgreSQL, un point critique pour éviter les avis frauduleux.
2.  **Expertise MongoDB** : Configuration optimale de la dénormalisation et résolution des problématiques de sérialisation d'ObjectIDs.
3.  **Rigueur des Tests** : Création d'une suite de tests simulant des interactions temporelles (événements passés) pour valider les garde-fous métiers.

---

## 🚀 Prochaine étape
Passage au **Domaine 5 : Dashboard Organisateur**. Cette phase finale utilisera la vue complexe PostgreSQL `v_dashboard_organisateur` et des agrégations MongoDB pour fournir une vue consolidée des statistiques à l'organisateur.
