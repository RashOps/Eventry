# 📓 Journal de Développement — Frontend & Intégration API

Ce document retrace les étapes de synchronisation du Frontend avec le Backend FastAPI/PostgreSQL/MongoDB.

## 🏁 Résumé des Travaux
L'objectif était de transformer une interface statique avec des données "mockées" en une application de production pilotée par l'état réel des bases de données.

---

## 🛠️ Phase 1 : Authentification & État Global
**Problème** : Le login échouait car le Frontend envoyait du JSON alors que le Backend attendait du Form-Data (OAuth2).

- **Correction Login** : Utilisation de `URLSearchParams` dans `authApi.js` pour envoyer des données encodées en URL.
- **`AuthContext`** : Création d'un contexte React pour centraliser l'état `user` et le `token`.
- **Hydratation** : Appel automatique à `/auth/me` au chargement pour restaurer la session.

## 🔑 Phase 2 : Contrôle d'Accès par Rôle (RBAC)
**Objectif** : Appliquer les permissions métier (Participant vs Organisateur).

- **`ProtectedRoute`** : Composant wrapper empêchant l'accès non-autorisé aux routes sensibles.
- **Navbar Dynamique** : Affichage conditionnel des menus ("Créer", "Dashboard") selon le rôle `organisateur` détecté dans le JWT.
- **Workflow Déconnexion** : Nettoyage propre du `localStorage` et remise à zéro de l'état global.

## 📊 Phase 3 : Synchronisation des Données Réelles
**Objectif** : Supprimer les mocks et refléter la complexité du Backend.

- **`Dashboard.jsx`** : Consommation de la vue SQL complexe du backend (taux de remplissage, nombre d'inscrits réels).
- **`EventDetail.jsx`** :
    - Détection intelligente du statut d'inscription (désactive le bouton si déjà inscrit).
    - Gestion des états de chargement (UX feedback).
    - Rafraîchissement automatique des places restantes après réservation.

## 🍃 Phase 4 : Exploitation NoSQL (MongoDB)
**Objectif** : Afficher les métadonnées polymorphes.

- **Composant Metadata** : Implémentation d'un affichage dynamique dans la fiche événement.
- **Support Polymorphe** : Affiche automatiquement le Lineup (Festivals), les Artistes (Expos) ou le Dress-code (Boîtes de nuit) selon le document présent dans MongoDB.
- **Géolocalisation** : Affichage des coordonnées GPS indexées en NoSQL.

---

## ✅ État Final
- **Connexion Front/Back** : 100% Fonctionnelle.
- **Sécurité** : Routes protégées et authentification persistante.
- **UX** : Feedback visuel sur toutes les actions asynchrones.
- **Architecture** : Cadrée sur les contrats de données Pydantic.
