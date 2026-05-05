# Cahier des charges : Projet Eventry

## 1. Choix d'architecture
La structure retenue est un **Monorepo**. Ce choix stratégique permet de simplifier le travail d'équipe et de centraliser la base de code pour les membres moins familiers avec les environnements Git complexes.
L'ensemble de l'architecture (Backend, Frontend, Bases de données) reposera sur des conteneurs isolés et s'exécutera via une commande unique : `docker-compose up -d`.

---

## 2. Choix du type d'API
L'application exposera une **API RESTful**. 
Justification de ce choix d'architecture :
* **Standardisation et robustesse :** Utilisation stricte des verbes HTTP et des codes de statut standards (200, 201, 400, 401, 403, 404, etc.).
* **Scalabilité et Stateless :** Facilité de mise en cache et séparation nette des responsabilités entre le client (React) et le serveur (FastAPI).
* **Conformité académique :** Le périmètre couvrira le minimum exigé de 16 endpoints (incluant authentification, opérations CRUD complètes sur 4 ressources, et endpoints analytiques).

---

## 3. Architecture Bases de Données (Approche Polyglotte)

Le projet impose l'exploitation simultanée et justifiée de deux paradigmes de stockage. La séparation des responsabilités sera stricte : PostgreSQL gère le relationnel structuré (utilisateurs, transactions) et MongoDB gère le non-structuré et l'analytique (contenu variable, géolocalisation).

### 3.1. Côté SQL : PostgreSQL
**Justification :** Choisi pour la rigueur transactionnelle, l'intégrité référentielle (ACID) et notre familiarité avec ce SGBD. Il sera la source de vérité pour les données critiques.

**Spécifications techniques implémentées :**
* Schéma normalisé jusqu'à la 3NF minimum.
* Implémentation de la logique métier SQL avancée : au moins 2 vues, 2 triggers, 3 procédures stockées, et 1 transaction explicite (BEGIN/COMMIT/ROLLBACK).
* Optimisation : Ajout d'au moins 1 index manuel (hors Primary Key).
* Requêtage complexe : Intégration d'une requête métier impliquant au minimum 4 jointures, 2 agrégations (GROUP BY + HAVING), et 2 sous-requêtes corrélées (ou 1 CTE).
* Automatisation : Script d'initialisation complet (schéma + seed data de démo) géré dans le versioning.

### 3.2. Côté NoSQL : MongoDB (Base Documentaire)
**Justification du choix documentaire (vs Clé-Valeur, Colonnes ou Graphes) :** 
Une plateforme d'événements manipule des données hautement polymorphes. Un "Festival" possède une liste de DJs, tandis qu'une "Exposition" possède un catalogue d'œuvres. Le modèle relationnel nous forcerait à créer des tables creuses ou des EAV (Entity-Attribute-Value) anti-performants. Le modèle Document de MongoDB permet d'encapsuler ces métadonnées hétérogènes dans des objets JSON flexibles.

**Exploitation des spécificités du moteur MongoDB :**
* **Recherche Géospatiale (Core Feature) :** Utilisation des index `2dsphere` pour implémenter une recherche "Trouver des événements autour de moi dans un rayon de X km".
* **Aggregation Framework :** Utilisation des pipelines d'agrégation (`$match`, `$group`, `$lookup`) pour générer des statistiques d'événements et des recommandations basées sur les tags, sans surcharger le backend.
* **Indexation TTL (Time-To-Live) :** Purge automatique des sessions éphémères ou des événements expirés nécessitant un archivage temporaire.

---

## 4. Conteneurisation (Docker)
L'environnement de développement et de production sera standardisé :
* **Backend :** Dockerfile dédié (utilisation de multi-stage builds si nécessaire).
* **Frontend :** Dockerfile dédié (build process ViteJS + serveur statique type Nginx).
* **Orchestration :** Un fichier `docker-compose.yml` orchestre le réseau local (Front, Back, PostgreSQL, MongoDB).
* **Sécurité :** Aucun secret codé en dur. Utilisation systématique de variables d'environnement encapsulées via un `.env.example` de référence.
* **Persistance :** Utilisation de `volumes` nommés pour sécuriser les données des BDD lors de l'arrêt des conteneurs.

---

## 5. Identité Visuelle et UI/UX
* **Charte graphique :** Création d'une identité propre incluant un logo, une palette stricte (3 à 5 couleurs avec codes hexadécimaux), et une typographie définie (1 à 2 polices).
* **Documentation :** Cette charte sera documentée dans le dossier de conception final (section dédiée avec exemples UI).
* **Responsive Design :** L'interface React devra être fully responsive (Mobile-first vers Desktop) sous peine de pénalités.

---

## 6. Méthodologie et Gestion de Projet

**Outil sélectionné : GitHub Projects**
*Justification de l'outil :* Afin de minimiser le changement de contexte ("context-switching") et d'assurer une traçabilité totale entre le code et les tâches, le Board sera hébergé directement sur GitHub. Cela simplifie le flux de travail pour l'ensemble de l'équipe par rapport à un outil externe (Notion/Trello).

**Cadre de travail : Kanban agile**
Le Board Kanban sera strictement structuré avec les colonnes imposées :
1. `Backlog`
2. `À faire` (To Do)
3. `En cours` (In Progress)
4. `À valider` (In Review / QA)
5. `Problématique` (Blocked)
6. `Terminé` (Done)

**Règles de création des tickets :**
Chaque issue/ticket GitHub devra impérativement contenir :
* Un titre clair.
* Une description détaillée (Critères d'acceptation).
* Un Assignee responsable de la livraison.
* Une estimation de complexité (T-shirt sizing : S, M, L, XL).
* Des labels de catégorisation (`bug`, `feature`, `techdette`, `doc`).
