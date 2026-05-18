# 🐘 PostgreSQL - Source de Vérité Transactionnelle

Ce dossier contient les scripts d'initialisation de la base de données relationnelle PostgreSQL pour le projet **Eventry**.

## 🏗️ Architecture du Schéma

La base est structurée selon la **3e Forme Normale (3NF)** pour garantir l'intégrité des données et minimiser la redondance. PostgreSQL est utilisé comme source de vérité (SSoT) pour toutes les données critiques.

### Entités principales
- **utilisateurs** : Gestion des identités et des rôles (visiteur, participant, organisateur).
- **evenements** : Données structurelles (titre, dates, prix, capacité).
- **lieux** : Référentiel des sites physiques accueillant les événements.
- **inscriptions** : Cœur transactionnel gérant les réservations et les files d'attente.

---

## ⚙️ Logique Métier (SQL Avancé)

Conformément au cahier des charges, le script `init.sql` implémente une logique métier complexe directement dans le moteur de base de données.

### 1. Procédures Stockées
- `proc_inscrire_participant` : Gère l'atomicité de l'inscription. Vérifie la capacité restante en temps réel et bascule automatiquement l'utilisateur en `liste_attente` si l'événement est complet.
- `proc_promouvoir_organisateur` : Gère le workflow de passage d'un utilisateur au statut d'organisateur.
- `proc_annuler_evenement` : Annule un événement et met à jour en cascade le statut de toutes les inscriptions liées.

### 2. Triggers
- `tr_after_annulation_inscription` : **Promotion Automatique**. Lorsqu'une inscription confirmée est annulée, ce trigger cherche l'utilisateur le plus ancien en liste d'attente et le promeut automatiquement au statut `confirmee`.
- `tr_before_update_event` : Garantit l'intégrité du workflow des événements (empêche le retour en `draft` après publication).

### 3. Vues Analytiques
- `v_evenements_details` : Vue simplifiée pour l'affichage du catalogue.
- `v_dashboard_organisateur` : **Requête complexe**. Joint 4 tables, utilise des CTE (Common Table Expressions) et des agrégations (`GROUP BY` + `HAVING`) pour calculer le taux de remplissage en temps réel.

---

## 🧪 Seed Data
Le script inclut un jeu de données de test (inséré via une transaction explicite `BEGIN/COMMIT`) comprenant :
- Des catégories de référence.
- Des lieux et des utilisateurs de test.
- Un événement "Nuit Électro" configuré pour tester immédiatement la **liste d'attente** et les **promotions automatiques**.

---

## 🚀 Utilisation

Pour initialiser la base de données manuellement :
```bash
psql -U <username> -d eventry -f init.sql
```
*Note : Dans l'environnement Docker du projet, ce script est automatiquement exécuté au premier lancement.*
