# 🛠️ Guide d'utilisation Git - Eventry

Ce guide explique pas à pas comment utiliser Git pour contribuer au projet sans faire d'erreurs, même si vous débutez.

---

## 📋 Routine de démarrage (À faire à chaque fois)

Avant de commencer à coder, assurez-vous d'avoir la dernière version du projet.

1. **Ouvrez votre terminal** à la racine du projet `Eventry/`.
2. **Mettez à jour votre code local** :
   ```bash
   git pull
   ```
3. **Vérifiez où vous êtes** :
   ```bash
   git branch
   ```
4. **Positionnez-vous sur la branche commune** (la branche de travail principale) :
   ```bash
   git switch develop
   ```

---

## 🚀 Créer une nouvelle tâche (Feature)

On ne travaille **jamais** directement sur `develop` ou `main`. On crée une "branche" pour sa tâche.

1. **Créez votre propre branche** (remplacez le nom par celui de votre tâche) :
   ```bash
   git checkout -b feature/ma-super-tache
   ```
   > 💡 *Consultez `docs/spécification/versionning-git.md` pour les règles de nommage.*

---

## ✍️ Travailler et Sauvegarder (Commit)

Pendant que vous codez, sauvegardez régulièrement votre avancement.

1. **Ajoutez vos fichiers modifiés** à la préparation :
   ```bash
   git add le-nom-du-fichier.py
   # Ou pour tout ajouter d'un coup :
   git add .
   ```
2. **Validez vos changements** avec un message clair :
   ```bash
   git commit -m "feat(api): ajout de la route de création d'événement"
   ```
   > 💡 *Respectez le format : type(périmètre): description.*

---

## 📤 Envoyer votre travail sur GitHub

Une fois que votre tâche est terminée et que tous vos commits sont faits :

1. **Envoyez votre branche sur le serveur** :
   ```bash
   git push -u origin feature/ma-super-tache
   ```

---

## 🔄 Fusionner votre travail (Pull Request)

C'est l'étape finale pour que votre code rejoigne le projet commun.

1. Allez sur la page du projet sur **GitHub**.
2. Cliquez sur l'onglet **"Pull Requests"**.
3. Cliquez sur le bouton vert **"New Pull Request"**.
4. **Attention au sens** : Sélectionnez `base: develop` ← `compare: feature/ma-super-tache`.
5. Décrivez ce que vous avez fait et cliquez sur **"Create Pull Request"**.
6. Prévenez Rayhan (Lead Tech) pour la validation !

---

## ⚠️ Les règles d'or (À ne JAMAIS faire)

*   ❌ **Ne jamais travailler sur `main`** : C'est la branche de production.
*   ❌ **Ne jamais push le fichier `.env`** : Il contient des mots de passe. Il est déjà dans le `.gitignore`.
*   ❌ **Ne jamais supprimer une branche** avant qu'elle ne soit validée sur GitHub.

*En cas de conflit ou de message d'erreur bizarre : ne paniquez pas, demandez de l'aide sur le groupe !*
