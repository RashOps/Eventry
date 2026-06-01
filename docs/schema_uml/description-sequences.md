# Flux de séquence — Eventry

Ces descriptions servent de base à la création des diagrammes de séquence UML.
Participants standards : Navigateur → API FastAPI → PostgreSQL → MongoDB

---

## SEQ-01 — Inscription d'un utilisateur à un événement

````
Navigateur          API FastAPI         PostgreSQL          MongoDB  
|                    |                   |                   |  
|-- POST /events/:id/register ---------->|                   |  
|   { places: 2, token: JWT }            |                   |  
|                    |-- Vérif JWT       |                   |  
|                    |-- CALL proc_inscrire(user_id, event_id, places)  
|                    |                   |                   |  
|                    |   BEGIN           |                   |  
|                    |-- SELECT COUNT places_confirmees ---->|  
|                    |<-- nb_inscrits: 257 ------------------|  
|                    |                   |                   |  
|                    |   [capacite_max=400, places_dispo=143]|  
|                    |                   |                   |  
|                    |-- INSERT inscriptions (confirmee) --->|  
|                    |   COMMIT          |                   |  
|                    |<-- inscription_id: 201 ---------------|  
|                    |                   |                   |  
|<-- 201 { status: "confirmed" } --------|                   |  
|                    |                   |                   |  
[Si capacité atteinte]  
|                    |-- INSERT inscriptions (liste_attente)->|  
|                    |   COMMIT          |                   |  
|<-- 201 { status: "waiting_list" } -----|                   |  
````

---

## SEQ-02 — Consultation de la fiche d'un événement

````
Navigateur          API FastAPI         PostgreSQL          MongoDB
|                    |                   |                   |
|-- GET /events/88 ----------------->    |                   |
|                    |                   |                   |
|                    |-- SELECT evenements JOIN lieux
|                    |   JOIN organisateurs JOIN categories ->|
|                    |<-- données structurelles --------------|
|                    |                   |                   |
|                    |-- find({ event_id: 88 }) ------------>|
|                    |   (events_catalog)                    |
|                    |<-- métadonnées + coordonnées GPS ------|
|                    |                   |                   |
|                    |-- aggregate avis (note_moyenne) ------>|
|                    |<-- { moyenne: 4.2, total: 38 } --------|
|                    |                   |                   |
|                    | [assemblage EventDetailResponse]       |
|<-- 200 EventDetailResponse ------------|                   |
````

---

## SEQ-03 — Recherche géospatiale

```
Navigateur          API FastAPI         PostgreSQL          MongoDB
|                    |                   |                   |
|-- GET /events/nearby?lat=48.85&lng=2.35&radius=10000 ---->|
|                    |                   |                   |
|                    |-- find($near, $maxDistance: 10000) -->|
|                    |   (index 2dsphere sur events_catalog) |
|                    |<-- [event_ids: [12, 43, 88, ...]] -----|
|                    |                   |                   |
|                    |-- SELECT evenements WHERE id IN (...)->|
|                    |<-- données structurelles + statuts ----|
|                    |                   |                   |
|                    | [assemblage + tri par distance]        |
|<-- 200 [EventSummaryResponse] ---------|                   |
```

---

## SEQ-04 — Création d'un événement (transaction bi-base)
```
Navigateur          API FastAPI         PostgreSQL          MongoDB
|                    |                   |                   |
|-- POST /events (EventCreateRequest) -->|                   |
|                    |                   |                   |
|                    |-- Vérif JWT + rôle organisateur       |
|                    |                   |                   |
|                    |   BEGIN           |                   |
|                    |-- INSERT evenements ----------------->|
|                    |<-- event_id: 88 ----------------------|
|                    |-- INSERT evenements_tags (batch) ---->|
|                    |   COMMIT          |                   |
|                    |                   |                   |
|                    |-- insertOne(events_catalog) --------->|
|                    |   { event_id: 88, metadata, location }|
|                    |<-- acknowledged: true -----------------|
|                    |                   |                   |
|<-- 201 EventDetailResponse ------------|                   |
|                    |                   |                   |
[Si MongoDB échoue]
|                    |-- UPDATE evenements SET statut='draft_incomplete'
|<-- 500 { error: "CATALOG_SYNC_FAILED" }|                   |
```

---

## SEQ-05 — Annulation avec promotion liste d'attente (trigger SQL)

```
Navigateur          API FastAPI         PostgreSQL
|                    |                   |
|-- DELETE /events/88/register -------->  |
|                    |                   |
|                    |-- UPDATE inscriptions
|                    |   SET statut='annulee'
|                    |   WHERE user_id=17 AND event_id=88 -->|
|                    |                   |                   |
|                    |   [TRIGGER tr_after_annulation se déclenche]
|                    |                   |                   |
|                    |   SELECT MIN(date_inscription)        |
|                    |   FROM inscriptions                   |
|                    |   WHERE event_id=88                   |
|                    |   AND statut='liste_attente' -------->|
|                    |<-- user_id: 34, inscription_id: 198 --|
|                    |                   |                   |
|                    |   UPDATE inscriptions                 |
|                    |   SET statut='confirmee'              |
|                    |   WHERE id=198 ---------------------->|
|                    |                   |                   |
|<-- 204 No Content  |                   |                   |
```