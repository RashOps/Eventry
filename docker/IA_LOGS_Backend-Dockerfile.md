# Journal des Décisions d'Architecture (ADR) - Dockerisation FastAPI

LLM utilisé : Gemini 3 pro  
Prompt utilisé pour amélioré le Dockerfile : 
``
voici mon dockerfile pour creer un containeur fastapi qui fera des appels vers des db mongodb et postgresql, verifie s'il est complet, challenge le et s'il faut l'optimiser avec justification. 
``  
Justification : Présenter un Dockerfile **production-ready**, renforcer notre Dockerfile (qui était déjà utilisable bien que présentant des failles de sécurité) afin d'éviter les surprises désagréables dans la suite du projet. Et aussi dans l'optique de vérifier s'il ne manquait pas des éléments nécessaires au fonctionnement du projet (dépendances postgreSQL).

## 1. Correction des Erreurs de Syntaxe
- **Problème :** Présence de fautes de frappe (`isntall`) empêchant le build.
- **Décision :** Correction en `install` et ajout du flag `-y` pour automatiser la validation des prompts APT.

## 2. Implémentation du Multi-stage Build
- **Problème :** Image finale trop lourde (contenant des compilateurs GCC et headers de dev).
- **Décision :** Séparation en deux étapes :
    - `builder` : Installation et compilation des dépendances (GCC, libpq-dev).
    - `final` : Copie uniquement des binaires compilés et des librairies d'exécution.
- **Impact :** Réduction de la taille de l'image (~40%) et surface d'attaque diminuée.

## 3. Optimisation de la Gestion du Cache
- **Problème :** Réinstallation des packages Python à chaque modification du code source.
- **Décision :** Isoler le `COPY requirements.txt` et le `pip install` avant le `COPY . .`.
- **Impact :** Build quasi-instantané lors des modifications de logique métier (le layer des dépendances est réutilisé).

## 4. Renforcement de la Sécurité (Principe du Moindre Privilège)
- **Problème :** Exécution du container en tant qu'utilisateur `root`.
- **Décision :** Création d'un groupe et d'un utilisateur système `appuser` non-privilégié.
- **Impact :** Si l'application est compromise, l'attaquant n'a pas les droits root sur le système de fichiers du container.

## 5. Standardisation de l'Environnement Python
- **Problème :** Génération de fichiers de cache inutiles et logs bufferisés.
- **Décision :** Injection des variables d'environnement :
    - `PYTHONDONTWRITEBYTECODE=1` : Évite les fichiers .pyc.
    - `PYTHONUNBUFFERED=1` : Permet de voir les logs de l'API en temps réel dans la console Docker.

## 6. Support des Bases de Données (PostgreSQL & MongoDB)
- **Problème :** Manque de drivers natifs pour les appels DB.
- **Décision :** Installation de `libpq5` pour PostgreSQL. MongoDB étant géré via le driver pur python `pymongo` (ou `motor`), aucune dépendance OS supplémentaire n'a été nécessaire.

## 7. Préparation au Déploiement (Prod vs Dev)
- **Problème :** Utilisation de `--reload` qui consomme des ressources et nuit à la stabilité.
- **Décision :** Suppression du `--reload` dans le Dockerfile. Ce flag doit être activé uniquement via le `docker-compose.yml` pour le développement local.