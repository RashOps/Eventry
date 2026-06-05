import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createEvent } from "../api/eventsApi";
import { useAuth } from "../context/AuthContext";

function CreateEvent() {
  const { isOrganizer } = useAuth();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    category: "boite_de_nuit",
    date_start: "",
    date_end: "",
    price: "",
    capacity: "",
    venue_id: "",
    tags: "",
    image_url: "",
    city: "",
    longitude: "",
    latitude: "",
    genres_musicaux: "",
    dress_code: "",
    age_minimum: "",
    table_vip_disponible: false,
  });

  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    
    if (!isOrganizer) {
      setError("Seuls les organisateurs peuvent créer des événements.");
      return;
    }

    setSuccess("");
    setError("");
    setLoading(true);

    const payload = {
      titre: formData.title, // Backend attend 'titre'
      description: formData.description,
      id_categorie: Number(formData.category === "boite_de_nuit" ? 2 : 1), // Mapping temporaire pour le seed, idéalement dynamique via API categories
      date_debut: new Date(formData.date_start).toISOString(),
      date_fin: new Date(formData.date_end).toISOString(),
      prix: Number(formData.price),
      capacite_max: Number(formData.capacity),
      id_lieu: Number(formData.venue_id),
      tags: formData.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
      image_url: formData.image_url,
      metadata: {
        genres_musicaux: formData.genres_musicaux
          .split(",")
          .map((genre) => genre.trim())
          .filter(Boolean),
        dress_code: formData.dress_code,
        age_minimum: Number(formData.age_minimum),
        table_vip_disponible: formData.table_vip_disponible,
      },
      location: {
        type: "Point",
        coordinates: [Number(formData.longitude), Number(formData.latitude)],
      },
    };

    try {
      await createEvent(payload);
      setSuccess("Événement créé avec succès ! Redirection vers le dashboard...");
      
      setTimeout(() => {
        navigate("/dashboard");
      }, 2000);

    } catch (err) {
      console.error(err);
      setError(
        err.message ||
          "Impossible de créer l’événement. Vérifie les informations."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="create-event-page">
      <section className="create-event-header">
        <div className="create-event-header-content">
          <p className="badge">Espace organisateur</p>

          <h1>Crée ton évènement et fais-le découvrir à la communauté Eventry.</h1>

          <p>
            Renseigne les informations principales, les dates, le lieu et les
            métadonnées afin que les participants puissent trouver ton évènement
            et réserver leur place facilement.
          </p>

          <div className="create-event-stats">
            <div>
              <strong>01</strong>
              <span>Informations</span>
            </div>

            <div>
              <strong>02</strong>
              <span>Lieu & date</span>
            </div>

            <div>
              <strong>03</strong>
              <span>Publication</span>
            </div>
          </div>
        </div>

        <div className="create-event-header-card">
          <span>Création rapide</span>

          <h2>Un formulaire complet aligné avec l’API Eventry</h2>

          <p>
            Les champs respectent le contrat de données : titre, catégorie,
            dates, prix, capacité, lieu, tags, métadonnées et géolocalisation.
          </p>
        </div>
      </section>

      <section className="create-event-layout">
        <form className="create-event-form" onSubmit={handleSubmit}>
          <div className="form-section">
            <h2>Informations principales</h2>

            <div className="form-group">
              <label>Titre de l’événement</label>
              <input
                type="text"
                name="title"
                placeholder="Nuit Électro — Warehouse Paris"
                value={formData.title}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                name="description"
                placeholder="Décris l’ambiance, le programme et les informations importantes."
                value={formData.description}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label>Catégorie</label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                >
                  <option value="boite_de_nuit">Boîte de nuit</option>
                  <option value="festival">Festival</option>
                  <option value="afterwork">Afterwork</option>
                  <option value="expo">Expo</option>
                  <option value="sortie">Sortie</option>
                </select>
              </div>

              <div className="form-group">
                <label>Image URL</label>
                <input
                  type="url"
                  name="image_url"
                  placeholder="https://cdn.eventry.fr/events/88.jpg"
                  value={formData.image_url}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Date, prix et capacité</h2>

            <div className="form-grid">
              <div className="form-group">
                <label>Date de début</label>
                <input
                  type="datetime-local"
                  name="date_start"
                  value={formData.date_start}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Date de fin</label>
                <input
                  type="datetime-local"
                  name="date_end"
                  value={formData.date_end}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Prix</label>
                <input
                  type="number"
                  name="price"
                  placeholder="15"
                  value={formData.price}
                  onChange={handleChange}
                  min="0"
                  required
                />
              </div>

              <div className="form-group">
                <label>Capacité</label>
                <input
                  type="number"
                  name="capacity"
                  placeholder="400"
                  value={formData.capacity}
                  onChange={handleChange}
                  min="1"
                  required
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Lieu et géolocalisation</h2>

            <div className="form-grid">
              <div className="form-group">
                <label>ID du lieu</label>
                <input
                  type="number"
                  name="venue_id"
                  placeholder="8"
                  value={formData.venue_id}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Ville</label>
                <input
                  type="text"
                  name="city"
                  placeholder="Paris"
                  value={formData.city}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Longitude</label>
                <input
                  type="number"
                  step="0.0001"
                  name="longitude"
                  placeholder="2.3522"
                  value={formData.longitude}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label>Latitude</label>
                <input
                  type="number"
                  step="0.0001"
                  name="latitude"
                  placeholder="48.8566"
                  value={formData.latitude}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h2>Métadonnées</h2>

            <div className="form-group">
              <label>Tags</label>
              <input
                type="text"
                name="tags"
                placeholder="techno, house, soiree"
                value={formData.tags}
                onChange={handleChange}
              />
            </div>

            <div className="form-grid">
              <div className="form-group">
                <label>Genres musicaux</label>
                <input
                  type="text"
                  name="genres_musicaux"
                  placeholder="Techno, House"
                  value={formData.genres_musicaux}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Dress code</label>
                <input
                  type="text"
                  name="dress_code"
                  placeholder="Tenue correcte exigée"
                  value={formData.dress_code}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label>Âge minimum</label>
                <input
                  type="number"
                  name="age_minimum"
                  placeholder="18"
                  value={formData.age_minimum}
                  onChange={handleChange}
                  min="0"
                />
              </div>

              <label className="checkbox-line">
                <input
                  type="checkbox"
                  name="table_vip_disponible"
                  checked={formData.table_vip_disponible}
                  onChange={handleChange}
                />
                Table VIP disponible
              </label>
            </div>
          </div>

          {success && <p className="form-success">{success}</p>}
          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? "Création..." : "Créer l’événement"}
          </button>
        </form>

        <aside className="create-event-preview">
          <p className="card-label">Aperçu</p>

          <h2>{formData.title || "Nom de l’événement"}</h2>

          <p>
            {formData.city || "Ville"} • {formData.category}
          </p>

          <p>
            {formData.description ||
              "La description de l’événement apparaîtra ici."}
          </p>

          <div className="preview-details">
            <span>{formData.capacity || 0} places</span>
            <strong>{formData.price || 0} €</strong>
          </div>
        </aside>
      </section>
    </main>
  );
}

export default CreateEvent;