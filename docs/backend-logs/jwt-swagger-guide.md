# 🔐 Guide : Authentification JWT & Utilisation du Swagger

Ce guide explique comment fonctionne l'authentification par **JSON Web Token (JWT)** dans Eventry et comment l'utiliser pour tester les routes protégées via l'interface **Swagger UI**.

---

## 🧐 Comment fonctionne le JWT ?

1.  **Connexion** : L'utilisateur envoie ses identifiants au serveur (`/auth/login`).
2.  **Génération** : Le serveur vérifie les identifiants et génère un jeton crypté (le JWT).
3.  **Stockage** : Le client (Navigateur/Swagger) stocke ce jeton.
4.  **Header** : Pour chaque requête vers une route protégée (ex: voir mon profil), le client envoie le jeton dans le header HTTP :
    `Authorization: Bearer <votre_token>`
5.  **Validation** : Le serveur décode le jeton. S'il est valide, il autorise l'accès.

---

## 🚀 Se connecter via Swagger UI

L'interface Swagger (`/docs`) intègre nativement le flux **OAuth2 Password Bearer**. Voici la procédure pas à pas :

### 1. Accéder au bouton Authorize
En haut à droite de la page Swagger, cliquez sur le bouton vert **Authorize** avec une icône de cadenas.

### 2. Remplir le formulaire
Une fenêtre surgissante apparaît avec le titre "Available authorizations".
*   **username** : Saisissez l'**email** de votre compte (ex: `admin@eventry.fr`).
*   **password** : Saisissez votre mot de passe (ex: `hash_admin` dans le seed actuel).
*   **Note** : Laissez les champs `client_id` et `client_secret` vides (ils ne sont pas requis pour notre configuration).

### 3. Valider
Cliquez sur le bouton **Authorize** dans la fenêtre, puis sur **Close**.
*   **Résultat** : Les cadenas sur les routes protégées seront maintenant "fermés", indiquant que vous êtes authentifié.

---

## 🛠️ Tester une route protégée

Une fois connecté :
1.  Cherchez la route `GET /api/v1/auth/me`.
2.  Cliquez sur **Try it out**.
3.  Cliquez sur **Execute**.
4.  Le serveur doit vous retourner vos informations de profil. Swagger a automatiquement ajouté le header `Authorization` pour vous.

---

## ⚠️ Notes importantes

*   **Expiration** : Les jetons sont configurés pour expirer après **30 minutes**. Si vous recevez une erreur `401 Unauthorized` après un certain temps, reconnectez-vous via le bouton Authorize.
*   **Déconnexion** : Pour supprimer le jeton de Swagger, recliquez sur **Authorize** puis sur **Logout**.
*   **Identifiants de test (Seed Data)** :
    *   Email : `admin@eventry.fr` / MDP : `hash_admin`
    *   Email : `lucas@test.com` / MDP : `hash_lucas`

---

## 🤖 Pourquoi utiliser OAuth2PasswordBearer ?

C'est le standard de FastAPI car il permet :
1.  D'être conforme aux spécifications OpenAPI.
2.  De faciliter l'intégration avec n'importe quel client (Web, Mobile, Postman).
3.  D'automatiser la documentation des schémas de sécurité.
