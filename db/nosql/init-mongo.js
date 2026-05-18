/**
 * PROJET EVENTRY - SCRIPT D'INITIALISATION MONGODB
 * Auteur : Gemini CLI (Expert Data)
 * Usage : mongo init-mongo.js (ou via mongosh)
 */

db = db.getSiblingDB('eventry');

// 1. NETTOYAGE
db.events_catalog.drop();
db.avis.drop();

// 2. CRÉATION DES COLLECTIONS ET INDEX

// Collection : events_catalog (Métadonnées polymorphes + Géo)
db.createCollection('events_catalog');

db.events_catalog.createIndex({ "location": "2dsphere" });
db.events_catalog.createIndex({ "search_text": "text" });
db.events_catalog.createIndex({ "event_id": 1 }, { unique: true });

// Collection : avis (Social & Feedback)
db.createCollection('avis');

db.avis.createIndex({ "event_id": 1, "published_at": -1 });
db.avis.createIndex({ "event_id": 1, "user_id": 1 }, { unique: true });
db.avis.createIndex({ "published_at": 1 }, { expireAfterSeconds: 94608000 }); // TTL 3 ans

// 3. SEED DATA (Jeu de données initial cohérent avec SQL)

db.events_catalog.insertMany([
  {
    "event_id": 1, // Nuit Électro
    "type": "boite_de_nuit",
    "location": { "type": "Point", "coordinates": [2.3522, 48.8566] },
    "metadata": {
      "genres_musicaux": ["Techno", "House"],
      "dress_code": "Tenue correcte exigée",
      "age_minimum": 21,
      "table_vip_disponible": true,
      "resident_djs": ["Amelie Lens", "Charlotte de Witte"]
    },
    "search_text": "soiree boite nuit paris techno house warehouse clubbing",
    "view_count": 1250,
    "created_at": new Date()
  },
  {
    "event_id": 2, // Expo Basquiat
    "type": "exposition",
    "location": { "type": "Point", "coordinates": [2.3308, 48.8614] },
    "metadata": {
      "artistes_exposes": ["Basquiat"],
      "type_oeuvres": "Peinture et Street Art",
      "visite_guidee_disponible": true,
      "accessibilite_pmr": true
    },
    "search_text": "exposition paris art contemporain basquiat louvre culture",
    "view_count": 2100,
    "created_at": new Date()
  },
  {
    "event_id": 3, // Delta Festival
    "type": "festival",
    "location": { "type": "Point", "coordinates": [5.3700, 43.3100] },
    "metadata": {
      "lineup": ["Justice", "Phoenix", "Vitalic"],
      "nombre_scenes": 5,
      "camping_disponible": true,
      "genres_musicaux": ["Electro", "Pop", "Rock"]
    },
    "search_text": "festival marseille delta musique plage plein air",
    "view_count": 5400,
    "created_at": new Date()
  },
  {
    "event_id": 4, // Afterwork Tech Lyon
    "type": "afterwork",
    "location": { "type": "Point", "coordinates": [4.8140, 45.7390] },
    "metadata": {
      "type_boisson": "Cocktails & Craft Beer",
      "networking_inclus": true,
      "terrasse_chauffee": true
    },
    "search_text": "afterwork lyon tech networking rooftop cocktail",
    "view_count": 450,
    "created_at": new Date()
  },
  {
    "event_id": 5, // Boat Party Bordeaux
    "type": "boite_de_nuit",
    "location": { "type": "Point", "coordinates": [-0.5530, 44.8660] },
    "metadata": {
      "genres_musicaux": ["Deep House", "Nu-Disco"],
      "type_bateau": "Catamaran Géant",
      "buffet_inclus": true
    },
    "search_text": "boat party bordeaux garonne soiree bateau house",
    "view_count": 1100,
    "created_at": new Date()
  }
]);

db.avis.insertMany([
  {
    "event_id": 1,
    "user_id": 2, // Lucas_B
    "pseudo_utilisateur": "Lucas_B",
    "avatar_url": "https://cdn.eventry.fr/avatars/17.jpg",
    "note_globale": 4,
    "notes_detail": { "ambiance": 5, "organisation": 3, "rapport_qualite_prix": 4 },
    "contenu": "Super soirée au Warehouse ! Le son était monstrueux. Seul bémol : l'attente au vestiaire.",
    "likes": 12,
    "likes_user_ids": [1, 3, 4, 6],
    "published_at": new Date("2026-07-14T10:00:00Z"),
    "reponse_organisateur": {
      "contenu": "Merci Lucas ! On a noté pour le vestiaire, on double l'effectif pour la prochaine.",
      "published_at": new Date("2026-07-15T09:00:00Z")
    }
  },
  {
    "event_id": 1,
    "user_id": 3, // Marie_Music
    "pseudo_utilisateur": "Marie_Music",
    "note_globale": 5,
    "notes_detail": { "ambiance": 5, "organisation": 5, "rapport_qualite_prix": 5 },
    "contenu": "Expérience parfaite. Les djs étaient incroyables.",
    "likes": 8,
    "likes_user_ids": [2, 5],
    "published_at": new Date("2026-07-14T12:00:00Z")
  },
  {
    "event_id": 2,
    "user_id": 7, // Julie_Art
    "pseudo_utilisateur": "Julie_Art",
    "note_globale": 5,
    "notes_detail": { "ambiance": 4, "organisation": 5, "rapport_qualite_prix": 5 },
    "contenu": "Une claque visuelle. Très bien organisé, pas trop de monde grâce aux créneaux.",
    "likes": 15,
    "likes_user_ids": [2, 10, 5],
    "published_at": new Date("2026-06-10T15:00:00Z")
  },
  {
    "event_id": 4,
    "user_id": 4, // Jean_Du_Sud
    "pseudo_utilisateur": "Jean_Du_Sud",
    "note_globale": 3,
    "notes_detail": { "ambiance": 3, "organisation": 2, "rapport_qualite_prix": 4 },
    "contenu": "Sympa mais trop bruyant pour vraiment networker.",
    "likes": 2,
    "likes_user_ids": [5],
    "published_at": new Date("2026-05-26T09:00:00Z"),
    "reponse_organisateur": {
      "contenu": "Désolé Jean, on prévoira une zone 'calme' pour la prochaine édition tech !",
      "published_at": new Date("2026-05-26T14:00:00Z")
    }
  }
]);

print("Initialisation MongoDB terminée avec succès !");

// 4. EXEMPLES D'AGRÉGATIONS (Pour test)

/*
// Calculer la note moyenne par événement
db.avis.aggregate([
  { $group: { _id: "$event_id", avgRating: { $avg: "$note_globale" }, count: { $sum: 1 } } }
]);

// Recherche géospatiale (10km autour de Paris Centre)
db.events_catalog.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [2.35, 48.85] },
      $maxDistance: 10000
    }
  }
});
*/
