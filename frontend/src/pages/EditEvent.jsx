import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getEventById, updateEvent } from "../api/eventsApi";
import { useAuth } from "../context/AuthContext";

function EditEvent() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isOrganizer } = useAuth();
  
  const [formData, setFormData] = useState({
    titre: "",
    description: "",
    prix: "",
    capacite_max: "",
    image_url: "",
    metadata: {}
  });

  const [loading, setLoading] = useState(true);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    async function fetchEvent() {
      try {
        const data = await getEventById(id);
        setFormData({
          titre: data.titre,
          description: data.description,
          prix: data.prix,
          capacite_max: data.capacite_max,
          image_url: data.image_url || "",
          metadata: data.metadata || {}
        });
      } catch (err) {
        setError("Impossible de charger les données de l'événement.");
      } finally {
        setLoading(false);
      }
    }
    fetchEvent();
  }, [id]);

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitLoading(true);
    setError("");
    setSuccess("");

    try {
      const payload = {
        ...formData,
        prix: Number(formData.prix),
        capacite_max: Number(formData.capacite_max)
      };
      await updateEvent(id, payload);
      setSuccess("Événement mis à jour !");
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (err) {
      setError(err.message || "Erreur lors de la mise à jour.");
    } finally {
      setSubmitLoading(false);
    }
  }

  if (loading) return <p className="page-message">Chargement de l'évènement...</p>;

  return (
    <main className="auth-page">
      <section className="auth-card" style={{ maxWidth: '700px' }}>
        <p className="badge">Édition</p>
        <h1>Modifier l'évènement</h1>
        
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Titre</label>
            <input name="titre" value={formData.titre} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea name="description" value={formData.description} onChange={handleChange} required />
          </div>

          <div className="form-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="form-group">
              <label>Prix (€)</label>
              <input type="number" name="prix" value={formData.prix} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Capacité Max</label>
              <input type="number" name="capacite_max" value={formData.capacite_max} onChange={handleChange} required />
            </div>
          </div>

          <div className="form-group">
            <label>URL Image</label>
            <input type="url" name="image_url" value={formData.image_url} onChange={handleChange} />
          </div>

          {error && <p className="form-error">{error}</p>}
          {success && <p className="form-success">{success}</p>}

          <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
            <button type="submit" className="primary-btn" disabled={submitLoading}>
              {submitLoading ? "Mise à jour..." : "Enregistrer les modifications"}
            </button>
            <button type="button" className="secondary-btn" onClick={() => navigate("/dashboard")}>
              Annuler
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

export default EditEvent;
