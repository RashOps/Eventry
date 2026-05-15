# Stratégie de cohérence inter-bases (SQL ↔ MongoDB)

## Règle de partage des responsabilités
### PostgreSQL = Source de vérité pour tout ce qui est transactionnel et relationnel
PostgreSQL/  
├── users             (identité, authentification, rôles)  
├── organisateurs     (profil organisation, vérification)  
├── lieux             (adresse, ville, coordonnées de référence)  
├── evenements        (titre, date_debut, date_fin, prix, capacité, statut, id_lieu, id_organisateur)  
├── inscriptions      (id_user, id_event, statut, places_reservees, date_inscription)  
└── categories        (festival, expo, boite_de_nuit, afterwork, sortie)  

### MongoDB = Couche flexible, analytique et géospatiale  
MongoDB/  
├── events_catalog    (métadonnées polymorphes par type + coordonnées GPS indexées)  
├── avis              (documents enrichis : notes détaillées, réponses, likes)  
└── event_views       (compteurs de vues pour le trending — optionnel)  

## Règle d'or

> Si la donnée implique de **l'argent, une identité forte, ou une relation contractuelle**
> entre entités → **PostgreSQL**.
>
> Si la donnée implique de la **flexibilité de schéma, du volume de lecture,
> ou des coordonnées GPS** → **MongoDB**.

## Stratégie de synchronisation

L'`id` d'un événement dans PostgreSQL est la **clé de référence étrangère** dans MongoDB.
Les deux bases ne se synchronisent pas automatiquement : c'est la couche applicative (API FastAPI)
qui garantit la cohérence lors des opérations d'écriture.

**Exemple — Création d'un événement (opération en deux phases) :**
1. PostgreSQL
BEGIN (PostgreSQL)
INSERT INTO evenements → retourne event_id = 42
COMMIT

2. db.events_catalog.insertOne({ event_id: 42, metadata: {...}, location: {...} })


En cas d'échec de la phase 2 (MongoDB), l'API lève une alerte et l'événement est marqué
`statut = 'incomplet'` dans PostgreSQL jusqu'à correction. PostgreSQL reste la source de vérité :
un événement n'existe officiellement que s'il existe dans PostgreSQL.

## Ce qui ne transite pas entre les bases

| Donnée                      | Réside dans    | Ne duplique jamais vers |
| :-------------------------- | :------------- | :---------------------- |
| Mot de passe (hashé)        | PostgreSQL     | MongoDB                 |
| Capacité max d'un événement | PostgreSQL     | MongoDB                 |
| Statut d'une inscription    | PostgreSQL     | MongoDB                 |
| Métadonnées polymorphes     | MongoDB        | PostgreSQL              |
| Coordonnées GPS (indexées)  | MongoDB        | PostgreSQL              |
| Contenu des avis            | MongoDB        | PostgreSQL              |

> Les coordonnées GPS existent en deux endroits : dans la table `lieux` de PostgreSQL
> (données de référence du lieu physique) et dans `events_catalog` de MongoDB
> (indexées pour les requêtes géospatiales). C'est une **dénormalisation volontaire et justifiée**
> pour la performance des requêtes de proximité.

Note : 
Que se passe-t-il si MongoDB est down ?
> L'application reste fonctionnelle pour l'inscription (SQL), les avis et la géoloc deviennent indisponibles.