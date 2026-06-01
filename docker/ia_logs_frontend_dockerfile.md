# Journal des Décisions d'Architecture (ADR) - Dockerisation Frontend

LLM utilisé : Gemini 3 pro  
Prompt utilisé pour amélioré le Dockerfile : 
``
Applique le meme processus sur mon dockerfile pour frontend utilisant nodejs + vite (suite de la conversation commencé pour le Dockerfile du Backend). 
``  
Justification : Présenter un Dockerfile **production-ready**, renforcer notre Dockerfile (qui était déjà utilisable bien que présentant des failles de sécurité) afin d'éviter les surprises désagréables dans la suite du projet. Et aussi dans l'optique de vérifier s'il ne manquait pas des éléments nécessaires au fonctionnement du projet (dépendances postgreSQL).

## 1. Migration vers Nginx pour la Production
- **Problème :** `npm run dev` est un serveur de développement, instable et lourd pour la production.
- **Décision :** Utilisation de `nginx:alpine` comme image de runtime.
- **Impact :** Performance décuplée, consommation RAM divisée par 10, sécurité renforcée.

## 2. Utilisation de `npm ci` au lieu de `npm install`
- **Problème :** `npm install` peut modifier le `package-lock.json` et est plus lent.
- **Décision :** Utilisation de `npm ci` (Clean Install).
- **Impact :** Builds reproductibles à 100% et plus rapides dans un environnement CI/CD.

## 3. Extraction des fichiers statiques
- **Problème :** Le code source et les `node_modules` (souvent > 200Mo) n'ont aucune utilité une fois le build terminé.
- **Décision :** Seul le dossier `/dist` (quelques Mo) est transféré dans l'image finale.
- **Impact :** Image finale extrêmement légère (environ 20Mo contre 400Mo+ précédemment).

## 4. Choix de l'image Alpine
- **Problème :** Les images Debian/Ubuntu contiennent des outils inutiles.
- **Décision :** Utilisation de `node:18-alpine` et `nginx:stable-alpine`.
- **Impact :** Réduction de la surface d'attaque et téléchargement plus rapide de l'image sur le registre.