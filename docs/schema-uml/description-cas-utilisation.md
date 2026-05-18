# Cas d'utilisation — Eventry

## Acteurs

- **Visiteur** : utilisateur non authentifié
- **Participant** : utilisateur authentifié avec le rôle participant
- **Organisateur** : utilisateur authentifié avec le rôle organisateur
- **Système** : traitement automatique interne (promotion liste d'attente, TTL)

> L'Organisateur hérite de tous les cas d'utilisation du Participant.

---

## UC-01 — S'inscrire sur la plateforme
- Acteur : Visiteur
- Précondition : aucune
- Scénario nominal :
  1. Le visiteur saisit email, mot de passe, pseudo
  2. Le système valide l'unicité de l'email et du pseudo
  3. Le système hash le mot de passe (bcrypt)
  4. Le système crée le compte et retourne un JWT
- Exceptions :
  - Email déjà utilisé → 409
  - Format invalide → 422

---

## UC-02 — Se connecter
- Acteur : Visiteur
- Précondition : compte existant
- Scénario nominal :
  1. Le visiteur saisit email + mot de passe
  2. Le système vérifie le hash bcrypt
  3. Le système génère et retourne un JWT (access token)
- Exceptions :
  - Identifiants incorrects → 401

---

## UC-03 — Parcourir le catalogue d'événements
- Acteur : Visiteur, Participant, Organisateur
- Précondition : aucune
- Scénario nominal :
  1. L'acteur accède au listing paginé
  2. L'acteur applique des filtres (catégorie, ville, date, prix, tags)
  3. Le système interroge PostgreSQL (données structurelles)
    et MongoDB (note moyenne via agrégation)
  4. Le système retourne la liste paginée avec les données enrichies
- Extensions :
  - UC-04 (recherche full-text)
  - UC-05 (recherche géospatiale)

---

## UC-04 — Rechercher un événement par mot-clé
- Acteur : Visiteur, Participant, Organisateur
- Précondition : aucune
- Scénario nominal :
  1. L'acteur saisit un mot-clé
  2. Le système interroge l'index full-text de MongoDB (collection events_catalog)
  3. Le système retourne les résultats triés par pertinence

---

## UC-05 — Trouver des événements à proximité
- Acteur : Visiteur, Participant, Organisateur
- Précondition : l'acteur autorise la géolocalisation du navigateur
- Scénario nominal :
  1. Le navigateur transmet les coordonnées GPS (lat, lng)
  2. L'acteur choisit un rayon (5 km, 10 km, 25 km)
  3. Le système interroge l'index 2dsphere de MongoDB
  4. Le système retourne les événements dans le rayon, triés par distance

---

## UC-06 — Consulter la fiche d'un événement
- Acteur : Visiteur, Participant, Organisateur
- Précondition : aucune
- Scénario nominal :
  1. L'acteur clique sur un événement
  2. Le système récupère les données structurelles depuis PostgreSQL
  3. Le système récupère les métadonnées depuis MongoDB (events_catalog)
  4. Le système récupère la note moyenne depuis MongoDB (agrégation avis)
  5. Le système assemble et retourne la fiche complète

---

## UC-07 — S'inscrire à un événement
- Acteur : Participant
- Précondition : authentifié, événement publié, non déjà inscrit
- Scénario nominal :
  1. Le participant clique sur "S'inscrire" et choisit le nombre de places
  2. Le système exécute la procédure stockée SQL :
     a. Vérifie que la capacité n'est pas atteinte
     b. Crée l'inscription avec statut "confirmee"
     c. Décrémente les places disponibles (calculé via COUNT)
  3. Le système retourne la confirmation
- Extension (capacité atteinte) :
  1. La procédure crée l'inscription avec statut "liste_attente"
  2. Le système retourne le statut "waiting_list"

---

## UC-08 — Annuler son inscription
- Acteur : Participant
- Précondition : inscription existante avec statut "confirmee"
- Scénario nominal :
  1. Le participant annule son inscription
  2. Le système passe le statut à "annulee" (trigger SQL)
  3. Le trigger vérifie s'il existe des inscrits en liste d'attente
  4. Si oui, le premier en liste est automatiquement promu à "confirmee"
- Note : c'est le trigger SQL qui gère la promotion automatique

---

## UC-09 — Déposer un avis
- Acteur : Participant
- Précondition : authentifié, inscription "confirmee" sur cet événement,
  date_fin de l'événement passée, aucun avis existant (unicité)
- Scénario nominal :
  1. Le participant saisit note globale, notes détaillées, commentaire
  2. Le système vérifie les préconditions côté API
  3. Le système insère le document dans MongoDB (collection avis)
  4. Le système retourne l'avis créé

---

## UC-10 — Répondre à un avis
- Acteur : Organisateur
- Précondition : authentifié, être l'organisateur de l'événement concerné
- Scénario nominal :
  1. L'organisateur saisit sa réponse
  2. Le système met à jour le sous-document "reponse_organisateur" dans MongoDB
  3. Le système retourne l'avis mis à jour

---

## UC-11 — Créer un événement
- Acteur : Organisateur
- Précondition : authentifié avec rôle organisateur
- Scénario nominal :
  1. L'organisateur remplit le formulaire
     (titre, description, catégorie, dates, prix, capacité, lieu, métadonnées)
  2. L'API exécute une transaction SQL :
     a. INSERT dans evenements → retourne event_id
     b. INSERT dans evenements_tags pour chaque tag
  3. L'API insère dans MongoDB (events_catalog) avec l'event_id retourné
  4. L'API retourne la fiche créée
- Exceptions :
  - Échec MongoDB après succès SQL → statut "draft_incomplete" dans PostgreSQL

---

## UC-12 — Consulter le dashboard organisateur
- Acteur : Organisateur
- Précondition : authentifié avec rôle organisateur
- Scénario nominal :
  1. L'organisateur accède à son tableau de bord
  2. Le système interroge PostgreSQL pour les taux de remplissage
     (requête complexe avec GROUP BY + HAVING)
  3. Le système interroge MongoDB pour les agrégations d'avis
  4. Le système retourne la vue consolidée