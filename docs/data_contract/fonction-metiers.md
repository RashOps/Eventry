# Domaines fonctionnels métiers

L'application est structurée autour de cinq domaines fonctionnels indépendants.

## Domaine 1 — Identité & Authentification

| ID      | Fonction                              | Acteur(s)                  | BDD       |
| :------ | :------------------------------------ | :------------------------- | :-------- |
| AUTH-01 | S'inscrire via email + mot de passe   | Tous                       | SQL       |
| AUTH-02 | Se connecter / se déconnecter         | Tous                       | SQL       |
| AUTH-03 | Consulter et modifier son profil      | Participant, Organisateur  | SQL       |
| AUTH-04 | Demander le rôle Organisateur         | Participant                | SQL       |

> Domaine 100% SQL : les données d'identité sont structurées et soumises aux garanties ACID
> (un compte ne peut pas être créé à moitié).

---

## Domaine 2 — Catalogue Événements

| ID     | Fonction                                              | Acteur(s)     | BDD           |
| :----- | :---------------------------------------------------- | :------------ | :------------ |
| CAT-01 | Lister les événements (pagination, filtres, tri)      | Tous          | SQL + NoSQL   |
| CAT-02 | Rechercher un événement par mot-clé                   | Tous          | SQL + NoSQL   |
| CAT-03 | Trouver des événements autour de moi (géolocalisation)| Tous          | **NoSQL**     |
| CAT-04 | Consulter la fiche complète d'un événement            | Tous          | SQL + NoSQL   |
| CAT-05 | Créer un événement avec ses métadonnées               | Organisateur  | SQL + NoSQL   |
| CAT-06 | Modifier ou annuler un événement                      | Organisateur  | SQL + NoSQL   |

> La recherche géospatiale (CAT-03) repose principalement sur MongoDB (index `2dsphere`).  
> Les métadonnées spécifiques par type d'événement sont stockées dans MongoDB (voir justification NoSQL).

---

## Domaine 3 — Inscription

| ID     | Fonction                                                  | Acteur(s)   | BDD   |
| :----- | :-------------------------------------------------------- | :---------- | :---- |
| INS-01 | S'inscrire à un événement disponible                      | Participant | SQL   |
| INS-02 | Annuler son inscription                                   | Participant | SQL   |
| INS-03 | Consulter ses inscriptions passées et à venir             | Participant | SQL   |
| INS-04 | Rejoindre la liste d'attente si l'événement est complet   | Participant | SQL   |
| INS-05 | Promotion automatique depuis la liste d'attente           | Système     | SQL   |

> Domaine 100% SQL : toute inscription implique une transaction atomique
> (vérification de capacité + création de l'inscription = opération indivisible via BEGIN/COMMIT).

---

## Domaine 4 — Social (Avis & Commentaires)

| ID     | Fonction                                               | Acteur(s)    | BDD       |
| :----- | :----------------------------------------------------- | :----------- | :-------- |
| SOC-01 | Déposer un avis sur un événement passé                 | Participant  | **NoSQL** |
| SOC-02 | Lire les avis d'un événement                           | Tous         | **NoSQL** |
| SOC-03 | Liker un avis                                          | Participant  | **NoSQL** |
| SOC-04 | Répondre à un avis (en tant qu'organisateur)           | Organisateur | **NoSQL** |
| SOC-05 | Consulter la note moyenne d'un événement               | Tous         | **NoSQL** |

> Domaine principalement NoSQL : les avis sont des documents flexibles à structure variable
> selon le type d'événement (voir justification NoSQL), consultés massivement en lecture.

---

## Domaine 5 — Dashboard Organisateur

| ID      | Fonction                                              | Acteur(s)    | BDD         |
| :------ | :---------------------------------------------------- | :----------- | :---------- |
| DASH-01 | Voir le taux de remplissage de ses événements         | Organisateur | SQL         |
| DASH-02 | Consulter les statistiques d'avis (notes, répartition)| Organisateur | NoSQL       |
| DASH-03 | Voir la provenance géographique de ses inscrits       | Organisateur | SQL + NoSQL |

> Ce domaine illustre la complémentarité des deux bases :
> les données transactionnelles viennent de PostgreSQL, les agrégations analytiques de MongoDB.