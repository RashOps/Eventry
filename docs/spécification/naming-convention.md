## STANDARDS DE CODAGE (NAMING CONVENTIONS)

L'uniformité est non-négociable pour la lisibilité (impact direct sur la note finale).

| Élément | Convention | Exemple |
| :--- | :--- | :--- |
| **Variables & Fonctions** | camelCase | `getUserData()`, `isLogged` |
| **Classes & Types** | PascalCase | `UserModel`, `DatabaseService` |
| **Constantes / Env** | UPPER_SNAKE_CASE | `PORT`, `MONGO_URI` |
| **Fichiers / Dossier** | kebab-case | `auth-controller.ts`, `docker-compose.yml` |
| **Tables SQL** | snake_case (pluriel) | `user_profiles`, `order_items` |
| **Collections NoSQL** | camelCase (singulier) | `userSession`, `productLog` |

## CONVENTIONS API REST (ROUTING)

Il nous faut au minimum 16 endpoints pour valider le projet. Les règles de nommage des routes sont strictes :

*   **Format** : Noms au pluriel, en minuscules, séparés par des tirets (kebab-case).
*   **Ressources** : Pas de verbes dans l'URL. Le verbe HTTP (GET, POST, PUT, DELETE) définit l'action.
    *   ✅ BIEN : `GET /api/v1/events` (Récupérer tous les événements)
    *   ✅ BIEN : `POST /api/v1/event-registrations` (S'inscrire à un événement)
    *   ❌ FAUX : `POST /api/v1/createEvent`
*   **Hiérarchie** : `GET /api/v1/events/{id}/comments` (Récupérer les commentaires d'un événement spécifique).ù
