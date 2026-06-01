# Routes API — Eventry

Base URL : `/api/v1`  
Auth : JWT Bearer Token — header `Authorization: Bearer <token>`

---

## AUTH — 4 endpoints

| # | Méthode | Route           | Auth requise | Description                          |
|---|---------|-----------------|:------------:|--------------------------------------|
| 1 | POST    | `/auth/register`| ✗            | Créer un compte                      |
| 2 | POST    | `/auth/login`   | ✗            | Se connecter, retourne le JWT        |
| 3 | POST    | `/auth/logout`  | ✓            | Invalider le token                   |
| 4 | GET     | `/auth/me`      | ✓            | Profil de l'utilisateur connecté     |

---

## USERS — 3 endpoints

| # | Méthode | Route         | Auth requise | Description                          |
|---|---------|---------------|:------------:|--------------------------------------|
| 5 | GET     | `/users/:id`  | ✓            | Consulter un profil utilisateur      |
| 6 | PATCH   | `/users/:id`  | ✓ (owner)    | Modifier son profil                  |
| 7 | DELETE  | `/users/:id`  | ✓ (owner)    | Supprimer son compte                 |

---

## EVENTS — 7 endpoints

| #  | Méthode | Route                  | Auth requise       | Description                                         |
|----|---------|------------------------|--------------------|-----------------------------------------------------|
| 8  | GET     | `/events`              | ✗                  | Lister les événements (pagination + filtres + tri)  |
| 9  | GET     | `/events/nearby`       | ✗                  | Recherche géospatiale (query: lat, lng, radius)     |
| 10 | GET     | `/events/search`       | ✗                  | Recherche full-text (query: q)                      |
| 11 | GET     | `/events/:id`          | ✗                  | Fiche complète d'un événement                       |
| 12 | POST    | `/events`              | ✓ (organisateur)   | Créer un événement                                  |
| 13 | PATCH   | `/events/:id`          | ✓ (organisateur)   | Modifier un événement                               |
| 14 | DELETE  | `/events/:id`          | ✓ (organisateur)   | Annuler/supprimer un événement                      |

### Filtres disponibles sur GET `/events`
?category=festival
?city=Paris
?date_from=2026-06-01
?date_to=2026-08-31
?price_max=30
?tags=techno,gratuit
?sort=date_asc | date_desc | price_asc | rating_desc
?page=1&limit=10

---

## REGISTRATIONS — 3 endpoints

| #  | Méthode | Route                          | Auth requise  | Description                              |
|----|---------|--------------------------------|:-------------:|------------------------------------------|
| 15 | POST    | `/events/:id/register`         | ✓             | S'inscrire à un événement                |
| 16 | DELETE  | `/events/:id/register`         | ✓             | Annuler son inscription                  |
| 17 | GET     | `/users/:id/registrations`     | ✓ (owner)     | Mes inscriptions (passées + à venir)     |

---

## REVIEWS — 5 endpoints

| #  | Méthode | Route                                   | Auth requise       | Description                        |
|----|---------|-----------------------------------------|--------------------|------------------------------------|
| 18 | GET     | `/events/:id/reviews`                   | ✗                  | Lire les avis d'un événement       |
| 19 | POST    | `/events/:id/reviews`                   | ✓                  | Déposer un avis                    |
| 20 | PATCH   | `/events/:id/reviews/:reviewId`         | ✓ (owner)          | Modifier son avis                  |
| 21 | DELETE  | `/events/:id/reviews/:reviewId`         | ✓ (owner)          | Supprimer son avis                 |
| 22 | POST    | `/events/:id/reviews/:reviewId/reply`   | ✓ (organisateur)   | Répondre à un avis                 |

---

## STATS — 2 endpoints (transverses)

| #  | Méthode | Route                   | Auth requise     | Description                                        |
|----|---------|-------------------------|------------------|----------------------------------------------------|
| 23 | GET     | `/events/:id/stats`     | ✓ (organisateur) | Stats complètes d'un événement (SQL + MongoDB)     |
| 24 | GET     | `/dashboard`            | ✓ (organisateur) | Vue globale de tous ses événements                 |

---

## Récapitulatif — Couverture du barème

| Exigence du sujet                            | Couverture Eventry              |
|----------------------------------------------|---------------------------------|
| 16 endpoints minimum                         | ✅ 24 endpoints                  |
| CRUD complet sur 4 ressources minimum        | ✅ users, events, registrations, reviews |
| 2 endpoints d'authentification minimum       | ✅ 4 endpoints auth              |
| 2 endpoints transverses non-CRUD             | ✅ `/nearby`, `/search`, `/stats`, `/dashboard` |
| Pagination, filtrage, tri sur les listings   | ✅ GET `/events`                 |
| Doc auto-générée Swagger                     | ✅ accessible sur `/docs`        |
| Opération métier reposant sur le NoSQL       | ✅ `/nearby` (géospatial) + reviews |


# Codes HTTP — Comportement attendu par endpoint

## AUTH

| Route            | Succès | Erreurs attendues                                          |
|------------------|--------|------------------------------------------------------------|
| POST `/register` | 201    | 409 (email déjà utilisé), 422 (format invalide)            |
| POST `/login`    | 200    | 401 (identifiants incorrects), 422 (champs manquants)      |
| POST `/logout`   | 204    | 401 (token invalide ou expiré)                             |
| GET `/me`        | 200    | 401 (non authentifié)                                      |

## EVENTS

| Route                  | Succès | Erreurs attendues                                            |
|------------------------|--------|--------------------------------------------------------------|
| GET `/events`          | 200    | 400 (paramètre de filtre invalide)                           |
| GET `/events/nearby`   | 200    | 400 (lat/lng manquants ou invalides)                         |
| GET `/events/search`   | 200    | 400 (paramètre q absent)                                     |
| GET `/events/:id`      | 200    | 404 (événement inexistant)                                   |
| POST `/events`         | 201    | 401, 403 (pas organisateur), 422 (données invalides)         |
| PATCH `/events/:id`    | 200    | 401, 403, 404, 422                                           |
| DELETE `/events/:id`   | 204    | 401, 403, 404                                                |

## REGISTRATIONS

| Route                        | Succès | Erreurs attendues                                               |
|------------------------------|--------|-----------------------------------------------------------------|
| POST `/events/:id/register`  | 201    | 401, 404, 409 (déjà inscrit), 422 (capacité dépassée → 201 waiting_list) |
| DELETE `/events/:id/register`| 204    | 401, 404 (inscription inexistante)                              |
| GET `/users/:id/registrations`| 200   | 401, 403 (pas le bon user)                                      |

## REVIEWS

| Route                              | Succès | Erreurs attendues                                          |
|------------------------------------|--------|------------------------------------------------------------|
| GET `/events/:id/reviews`          | 200    | 404 (événement inexistant)                                 |
| POST `/events/:id/reviews`         | 201    | 401, 403 (pas encore participé), 409 (déjà un avis)        |
| PATCH `/events/:id/reviews/:rid`   | 200    | 401, 403, 404                                              |
| DELETE `/events/:id/reviews/:rid`  | 204    | 401, 403, 404                                              |
| POST `.../reply`                   | 201    | 401, 403 (pas l'organisateur de cet event), 404            |

## Endpoints complexes
* **Premier point :** le ``POST /events/:id/register`` est un endpoint le plus complexe — il doit appeler la procédure stockée SQL qui vérifie la capacité, gerer la liste d'attente, et retourne soit ``confirmed`` soit ``waiting_list`` dans la même réponse 201. Si le code renvoyé est 422 quand c'est complet au lieu de 201 avec ``waiting_list``, on perd la cohérence métier. 
* **Deuxième point :** ``POST /events/:id/reviews`` doit vérifier que l'utilisateur a bien une inscription ``confirmed`` et passée sur cet événement avant d'accepter l'avis — sinon n'importe qui peut noter un événement auquel il n'est pas allé.