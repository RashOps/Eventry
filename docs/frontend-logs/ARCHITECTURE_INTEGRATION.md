# 🧩 Guide d'Architecture & Intégration

## 🔒 Gestion de l'Authentification

### AuthContext.jsx
Le cœur de l'application. Il utilise le hook `useAuth()` pour exposer :
- `user` : L'objet utilisateur complet (id, pseudo, email, role).
- `isAuthenticated` : Boolean pour vérifier la connexion.
- `isOrganizer` : Boolean pour vérifier les droits d'organisation.
- `login(token, userData)` : Fonction pour initialiser la session.
- `logout()` : Fonction pour réinitialiser l'app.

## 🛡️ Sécurisation des Routes

### ProtectedRoute.jsx
Composant wrapper à utiliser dans `App.jsx`.
```jsx
// Exemple pour une route restreinte
<Route path="/admin" element={
  <ProtectedRoute roleRequired="organisateur">
    <AdminPanel />
  </ProtectedRoute>
} />
```

## 🌐 Client API (`client.js`)

Le client API centralise :
1. **Injection du Token** : Récupère automatiquement le token du `localStorage`.
2. **Gestion des erreurs 401** : Si une requête renvoie "Non autorisé", il nettoie la session pour forcer une reconnexion.
3. **Multi-format** : Gère nativement le JSON et le Form-Data (pour le login).

## 🚀 Bonnes Pratiques Appliquées
1. **DRY (Don't Repeat Yourself)** : Les appels API sont centralisés dans le dossier `api/`.
2. **KISS (Keep It Simple, Stupid)** : Utilisation de hooks standards pour la gestion d'état.
3. **Separation of Concerns** : La logique de permission est séparée de la logique d'affichage des composants.
