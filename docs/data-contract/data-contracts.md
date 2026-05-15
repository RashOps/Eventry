# Data Contracts — Eventry API

## Conventions générales

- Toutes les requêtes et réponses sont en `application/json`
- Les dates suivent le format ISO 8601 : `"2026-06-15T20:00:00Z"`
- Les IDs sont des entiers (`int`) côté SQL, des strings ObjectId côté MongoDB
- Toute réponse d'erreur suit le format standard ci-dessous

### Format de réponse d'erreur (standard)

```json
{
  "status": 404,
  "error": "NOT_FOUND",
  "message": "L'événement avec l'id 42 n'existe pas.",
  "timestamp": "2026-05-15T10:30:00Z"
}
```

### Format de réponse paginée (standard)

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 87,
    "total_pages": 9
  }
}
```

---

## Modèles — Domaine AUTH

### UserRegisterRequest
```json
{
  "email": "lucas@example.com",
  "password": "MotDePasse123!",
  "pseudo": "Lucas_B"
}
```

### UserLoginRequest
```json
{
  "email": "lucas@example.com",
  "password": "MotDePasse123!"
}
```

### AuthResponse
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### UserProfileResponse
```json
{
  "id": 17,
  "email": "lucas@example.com",
  "pseudo": "Lucas_B",
  "role": "participant",
  "avatar_url": "https://cdn.eventry.fr/avatars/17.jpg",
  "date_inscription": "2026-01-10T14:00:00Z"
}
```

### UserUpdateRequest
```json
{
  "pseudo": "Lucas_B_Updated",
  "avatar_url": "https://cdn.eventry.fr/avatars/17_new.jpg"
}
```

---

## Modèles — Domaine CATALOGUE

### EventCreateRequest
> Envoyé par l'organisateur. `metadata` est polymorphe selon `category`.

```json
{
  "title": "Nuit Électro — Warehouse Paris",
  "description": "Une nuit de techno industrielle dans un entrepôt parisien.",
  "category": "boite_de_nuit",
  "date_start": "2026-07-12T23:00:00Z",
  "date_end": "2026-07-13T06:00:00Z",
  "price": 15.00,
  "capacity": 400,
  "venue_id": 8,
  "tags": ["techno", "house", "soiree"],
  "image_url": "https://cdn.eventry.fr/events/88.jpg",
  "metadata": {
    "genres_musicaux": ["Techno", "House"],
    "dress_code": "Tenue correcte exigée",
    "age_minimum": 21,
    "table_vip_disponible": true
  },
  "location": {
    "type": "Point",
    "coordinates": [2.3522, 48.8566]
  }
}
```

### EventSummaryResponse
> Utilisé dans les listes (pagination). Version allégée sans métadonnées complètes.

```json
{
  "id": 88,
  "title": "Nuit Électro — Warehouse Paris",
  "category": "boite_de_nuit",
  "date_start": "2026-07-12T23:00:00Z",
  "price": 15.00,
  "capacity": 400,
  "spots_remaining": 143,
  "venue": {
    "name": "Warehouse Paris",
    "city": "Paris"
  },
  "average_rating": 4.2,
  "image_url": "https://cdn.eventry.fr/events/88.jpg",
  "tags": ["techno", "house", "soiree"]
}
```

### EventDetailResponse
> Utilisé sur la fiche complète. Agrège SQL + MongoDB.

```json
{
  "id": 88,
  "title": "Nuit Électro — Warehouse Paris",
  "description": "Une nuit de techno industrielle dans un entrepôt parisien.",
  "category": "boite_de_nuit",
  "date_start": "2026-07-12T23:00:00Z",
  "date_end": "2026-07-13T06:00:00Z",
  "price": 15.00,
  "capacity": 400,
  "spots_remaining": 143,
  "status": "published",
  "venue": {
    "id": 8,
    "name": "Warehouse Paris",
    "address": "12 rue de la Forge",
    "city": "Paris",
    "zip_code": "75010",
    "latitude": 48.8566,
    "longitude": 2.3522
  },
  "organizer": {
    "id": 3,
    "name": "Collectif RAVE",
    "verified": true
  },
  "tags": ["techno", "house", "soiree"],
  "image_url": "https://cdn.eventry.fr/events/88.jpg",
  "metadata": {
    "genres_musicaux": ["Techno", "House"],
    "dress_code": "Tenue correcte exigée",
    "age_minimum": 21,
    "table_vip_disponible": true
  },
  "average_rating": 4.2,
  "total_reviews": 38
}
```

### EventUpdateRequest
> Tous les champs sont optionnels (PATCH sémantique).

```json
{
  "title": "Nuit Électro — Warehouse Paris [SOLD OUT]",
  "price": 20.00,
  "status": "cancelled",
  "metadata": {
    "dress_code": "Tenue de soirée obligatoire"
  }
}
```

### GeoSearchRequest (query params)
GET /api/v1/events/nearby?lat=48.8566&lng=2.3522&radius=10000&limit=20
---

## Modèles — Domaine INSCRIPTION

### RegistrationRequest
```json
{
  "places": 2
}
```

### RegistrationResponse
```json
{
  "id": 201,
  "event_id": 88,
  "user_id": 17,
  "status": "confirmed",
  "places": 2,
  "registered_at": "2026-05-15T10:30:00Z"
}
```
> `status` peut valoir : `"confirmed"` | `"waiting_list"` | `"cancelled"`

### UserRegistrationsResponse
> Liste des inscriptions d'un utilisateur, triées par date.

```json
{
  "data": [
    {
      "registration_id": 201,
      "status": "confirmed",
      "places": 2,
      "registered_at": "2026-05-15T10:30:00Z",
      "event": {
        "id": 88,
        "title": "Nuit Électro — Warehouse Paris",
        "date_start": "2026-07-12T23:00:00Z",
        "venue_city": "Paris",
        "image_url": "https://cdn.eventry.fr/events/88.jpg"
      }
    }
  ],
  "pagination": { "page": 1, "limit": 10, "total": 4, "total_pages": 1 }
}
```

---

## Modèles — Domaine SOCIAL

### ReviewCreateRequest
```json
{
  "note_globale": 4,
  "notes_detail": {
    "ambiance": 5,
    "organisation": 3,
    "rapport_qualite_prix": 4
  },
  "contenu": "Super soirée, ambiance au top mais files d'attente interminables."
}
```

### ReviewResponse
```json
{
  "id": "664a1f3e2b4c5d6e7f8a9b0c",
  "event_id": 88,
  "user": {
    "id": 17,
    "pseudo": "Lucas_B",
    "avatar_url": "https://cdn.eventry.fr/avatars/17.jpg"
  },
  "note_globale": 4,
  "notes_detail": {
    "ambiance": 5,
    "organisation": 3,
    "rapport_qualite_prix": 4
  },
  "contenu": "Super soirée, ambiance au top mais files d'attente interminables.",
  "likes": 7,
  "published_at": "2026-07-14T10:00:00Z",
  "organizer_reply": null
}
```

### OrganizerReplyRequest
```json
{
  "contenu": "Merci pour votre retour ! Nous améliorons nos process d'accueil."
}
```

### EventStatsResponse
> Agrégation MongoDB + données SQL. Utilisé pour le dashboard organisateur.

```json
{
  "event_id": 88,
  "title": "Nuit Électro — Warehouse Paris",
  "capacity": 400,
  "registered_count": 257,
  "fill_rate": 64.25,
  "reviews": {
    "total": 38,
    "average": 4.2,
    "distribution": {
      "1": 1, "2": 3, "3": 5, "4": 17, "5": 12
    },
    "average_by_criteria": {
      "ambiance": 4.6,
      "organisation": 3.8,
      "rapport_qualite_prix": 4.1
    }
  }
}
```