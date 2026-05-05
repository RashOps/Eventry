# 🛠 CONVENTIONS DE DÉVELOPPEMENT & GIT STRATEGY

## STRATÉGIE DE VERSIONING (GIT)

Pour éviter les conflits et assurer une traçabilité conforme aux exigences académiques :

### Branches
* **main** : Branche protégée. Contient le code stable et "production-ready". **Aucun commit direct autorisé**.
* **develop** : Branche d'intégration. Les features y sont mergées pour test avant la main.
* **feature/nom-de-la-feature** : Une branche par ticket (ex: `feature/api-auth`, `feature/mongodb-setup`).

### Workflow de Validation
1. **Pull Request (PR)** obligatoire pour chaque merge vers `develop` ou `main`.
2. **Code Review** : Au moins 1 approve nécessaire (Rayhan par défaut pour valider la qualité).
3. **Merge** : Squash and Merge privilégié pour garder un historique propre.

### Convention de Commits (Conventional Commits)
Format : `<type>(<scope>): <description>`
* `feat`: Nouvelle fonctionnalité.
* `fix`: Correction de bug.
* `docs`: Documentation uniquement.
* `refactor`: Modification de code qui ne change pas le comportement.
* `chore`: Maintenance (ex: mise à jour de dépendances).

*Exemple : `feat(api): add post endpoint for user registration`*

### A JAMAIS FAIRE
* Ne jamais push un fichier .env contenant les API / Mots de passe
* Ne jamais travailler sur la branche `main`