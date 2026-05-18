# Collections MongoDB

## Collection 1 : events_catalog

Stocke les métadonnées polymorphes et les coordonnées GPS de chaque événement.
La clé `event_id` est la référence vers la table `evenements` de PostgreSQL.

### Document type — Festival

```json
{
  "_id": "ObjectId('664a1f3e2b4c5d6e7f8a9b01')",
  "event_id": 12,
  "type": "festival",
  "location": {
    "type": "Point",
    "coordinates": [2.3522, 48.8566]
  },
  "metadata": {
    "lineup": ["DJ Snake", "Aya Nakamura", "Hamza"],
    "nombre_scenes": 3,
    "camping_disponible": true,
    "dress_code": null,
    "genres_musicaux": ["Hip-hop", "Electro", "RnB"]
  },
  "search_text": "festival paris electro rnb été 2026",
  "view_count": 1420,
  "created_at": "2026-03-10T09:00:00Z"
}
```

### Document type — Exposition

```json
{
  "_id": "ObjectId('664a1f3e2b4c5d6e7f8a9b02')",
  "event_id": 27,
  "type": "exposition",
  "location": {
    "type": "Point",
    "coordinates": [2.3308, 48.8614]
  },
  "metadata": {
    "artistes_exposes": ["Basquiat", "Banksy"],
    "type_oeuvres": "Street art et peinture contemporaine",
    "visite_guidee_disponible": true,
    "accessibilite_pmr": true,
    "dress_code": null
  },
  "search_text": "exposition paris art contemporain basquiat banksy",
  "view_count": 342,
  "created_at": "2026-02-20T14:00:00Z"
}
```

### Document type — Boîte de nuit

```json
{
  "_id": "ObjectId('664a1f3e2b4c5d6e7f8a9b03')",
  "event_id": 43,
  "type": "boite_de_nuit",
  "location": {
    "type": "Point",
    "coordinates": [2.3600, 48.8700]
  },
  "metadata": {
    "genres_musicaux": ["Techno", "House", "Minimal"],
    "dress_code": "Tenue correcte exigée",
    "age_minimum": 21,
    "table_vip_disponible": true,
    "resident_djs": ["BLOND:ISH", "Amelie Lens"]
  },
  "search_text": "soiree boite nuit paris techno house",
  "view_count": 2100,
  "created_at": "2026-04-01T18:00:00Z"
}
```

### Index de la collection events_catalog

```javascript
// Index géospatial — requis pour $near et $geoWithin
db.events_catalog.createIndex({ "location": "2dsphere" })

// Index full-text — pour la recherche par mot-clé
db.events_catalog.createIndex({ "search_text": "text" })

// Index sur event_id — pour les lookups depuis l'API
db.events_catalog.createIndex({ "event_id": 1 }, { unique: true })
```

---

## Collection 2 : avis

Stocke les avis et commentaires des participants sur les événements.
`event_id` et `user_id` sont des références vers PostgreSQL.

### Document type — Avis complet

```json
{
  "_id": "ObjectId('664b2a4f3c5d6e7f8a9b0c1d')",
  "event_id": 43,
  "user_id": 17,
  "pseudo_utilisateur": "Lucas_B",
  "avatar_url": "https://cdn.eventry.fr/avatars/17.jpg",
  "note_globale": 4,
  "notes_detail": {
    "ambiance": 5,
    "organisation": 3,
    "rapport_qualite_prix": 4
  },
  "contenu": "Super soirée, ambiance incroyable. Files d'attente à l'entrée trop longues.",
  "likes": 12,
  "likes_user_ids": [3, 9, 22, 45],
  "published_at": "2026-07-14T10:00:00Z",
  "updated_at": null,
  "reponse_organisateur": {
    "contenu": "Merci pour votre retour ! Nous améliorons notre système d'accueil.",
    "published_at": "2026-07-15T09:30:00Z"
  }
}
```

### Index de la collection avis

```javascript
// Index composé — récupérer tous les avis d'un événement, triés par date
db.avis.createIndex({ "event_id": 1, "published_at": -1 })

// Index unique — un utilisateur ne peut avoir qu'un seul avis par événement
db.avis.createIndex({ "event_id": 1, "user_id": 1 }, { unique: true })

// Index TTL — purge automatique des avis de plus de 3 ans
db.avis.createIndex(
  { "published_at": 1 },
  { expireAfterSeconds: 94608000 }
)
```

---

## Agrégations MongoDB utilisées dans l'application

### Agrégation 1 — Note moyenne et répartition pour un événement

```javascript
db.avis.aggregate([
  { $match: { event_id: 43 } },
  { $group: {
      _id: "$event_id",
      note_moyenne: { $avg: "$note_globale" },
      total_avis: { $sum: 1 },
      moyenne_ambiance: { $avg: "$notes_detail.ambiance" },
      moyenne_organisation: { $avg: "$notes_detail.organisation" },
      moyenne_qualite_prix: { $avg: "$notes_detail.rapport_qualite_prix" },
      repartition: { $push: "$note_globale" }
  }}
])
```

### Agrégation 2 — Top 5 événements les mieux notés ce mois

```javascript
db.avis.aggregate([
  { $match: {
      published_at: { $gte: new Date("2026-07-01") }
  }},
  { $group: {
      _id: "$event_id",
      moyenne: { $avg: "$note_globale" },
      nb_avis: { $sum: 1 }
  }},
  { $match: { nb_avis: { $gte: 3 } } },
  { $sort: { moyenne: -1 } },
  { $limit: 5 }
])
```

### Agrégation 3 — Recherche géospatiale (10 km autour d'une position)

```javascript
db.events_catalog.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [2.3522, 48.8566] },
      $maxDistance: 10000
    }
  }
})
```