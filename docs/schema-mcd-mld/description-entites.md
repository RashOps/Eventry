# Entités SQL — PostgreSQL

## 1. utilisateurs
Source de vérité pour toute identité dans le système.

| Attribut          | Type         | Contrainte              |
|-------------------|--------------|-------------------------|
| id                | SERIAL       | PK                      |
| email             | VARCHAR(255) | UNIQUE, NOT NULL        |
| mot_de_passe_hash | VARCHAR(255) | NOT NULL                |
| pseudo            | VARCHAR(100) | UNIQUE, NOT NULL        |
| avatar_url        | TEXT         | NULL                    |
| role              | ENUM         | 'visiteur','participant','organisateur' — DEFAULT 'participant' |
| date_inscription  | TIMESTAMP    | DEFAULT NOW()           |
| est_actif         | BOOLEAN      | DEFAULT TRUE            |

---

## 2. organisateurs
Spécialisation d'un utilisateur avec le rôle 'organisateur'.
Relation 1-1 avec utilisateurs (héritage par référence).

| Attribut      | Type         | Contrainte                        |
|---------------|--------------|-----------------------------------|
| id            | SERIAL       | PK                                |
| id_utilisateur| INTEGER      | FK → utilisateurs(id), UNIQUE     |
| nom           | VARCHAR(255) | NOT NULL                          |
| description   | TEXT         | NULL                              |
| site_web      | VARCHAR(255) | NULL                              |
| est_verifie   | BOOLEAN      | DEFAULT FALSE                     |
| date_creation | TIMESTAMP    | DEFAULT NOW()                     |

---

## 3. lieux
Lieu physique où se déroule un événement.

| Attribut    | Type         | Contrainte     |
|-------------|--------------|----------------|
| id          | SERIAL       | PK             |
| nom         | VARCHAR(255) | NOT NULL       |
| adresse     | VARCHAR(255) | NOT NULL       |
| ville       | VARCHAR(100) | NOT NULL       |
| code_postal | VARCHAR(10)  | NOT NULL       |
| pays        | VARCHAR(100) | DEFAULT 'France'|
| latitude    | DECIMAL(9,6) | NOT NULL       |
| longitude   | DECIMAL(9,6) | NOT NULL       |
| capacite    | INTEGER      | NULL           |

---

## 4. categories
Type d'événement. Données de référence stables.

| Attribut    | Type         | Contrainte     |
|-------------|--------------|----------------|
| id          | SERIAL       | PK             |
| nom         | VARCHAR(100) | UNIQUE, NOT NULL|
| description | TEXT         | NULL           |

Valeurs : festival, exposition, boite_de_nuit, afterwork, sortie

---

## 5. evenements
Entité centrale du système. Données structurelles et transactionnelles.

| Attribut        | Type         | Contrainte                          |
|-----------------|--------------|-------------------------------------|
| id              | SERIAL       | PK                                  |
| titre           | VARCHAR(255) | NOT NULL                            |
| description     | TEXT         | NOT NULL                            |
| date_debut      | TIMESTAMP    | NOT NULL                            |
| date_fin        | TIMESTAMP    | NOT NULL                            |
| prix            | DECIMAL(8,2) | DEFAULT 0.00                        |
| capacite_max    | INTEGER      | NOT NULL                            |
| image_url       | TEXT         | NULL                                |
| statut          | ENUM         | 'draft','published','cancelled','archived' — DEFAULT 'draft' |
| date_creation   | TIMESTAMP    | DEFAULT NOW()                       |
| id_lieu         | INTEGER      | FK → lieux(id), NOT NULL            |
| id_organisateur | INTEGER      | FK → organisateurs(id), NOT NULL    |
| id_categorie    | INTEGER      | FK → categories(id), NOT NULL       |

---

## 6. tags
Mots-clés libres associés aux événements.

| Attribut | Type         | Contrainte      |
|----------|--------------|-----------------|
| id       | SERIAL       | PK              |
| libelle  | VARCHAR(100) | UNIQUE, NOT NULL|

Exemples : techno, gratuit, plein-air, familial, afterwork

---

## 7. evenements_tags
Table de liaison n-n entre evenements et tags.

| Attribut    | Type    | Contrainte                |
|-------------|---------|---------------------------|
| id_evenement| INTEGER | FK → evenements(id)       |
| id_tag      | INTEGER | FK → tags(id)             |
| PK composite| —       | (id_evenement, id_tag)    |

---

## 8. inscriptions
Enregistre la participation d'un utilisateur à un événement.
Cœur transactionnel de l'application.

| Attribut         | Type      | Contrainte                          |
|------------------|-----------|-------------------------------------|
| id               | SERIAL    | PK                                  |
| id_utilisateur   | INTEGER   | FK → utilisateurs(id), NOT NULL     |
| id_evenement     | INTEGER   | FK → evenements(id), NOT NULL       |
| statut           | ENUM      | 'confirmee','liste_attente','annulee'|
| places_reservees | INTEGER   | DEFAULT 1                           |
| date_inscription | TIMESTAMP | DEFAULT NOW()                       |
| UNIQUE           | —         | (id_utilisateur, id_evenement)      |

---

## Relations entre entités (cardinalités)
utilisateurs ||--o{ organisateurs       : "peut être"  
utilisateurs ||--o{ inscriptions        : "effectue"  
organisateurs ||--o{ evenements         : "crée"  
lieux ||--o{ evenements                 : "accueille"  
categories ||--o{ evenements            : "classifie"  
evenements ||--o{ inscriptions          : "reçoit"  
evenements }o--o{ tags                  : "est associé à" (via evenements_tags)  

### Cardinalités détaillées

| Relation                     | Cardinalité |
|------------------------------|-------------|
| utilisateur → organisateur   | 0,1 — 1,1   |
| organisateur → événements    | 1,N — 1,1   |
| lieu → événements            | 1,N — 1,1   |
| catégorie → événements       | 1,N — 1,1   |
| événement → tags             | 0,N — 0,N   |
| utilisateur → inscriptions   | 0,N — 1,1   |
| événement → inscriptions     | 0,N — 1,1   |

