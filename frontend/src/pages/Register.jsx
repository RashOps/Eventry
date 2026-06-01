import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/authApi";

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    pseudo: "",
    email: "",
    password: "",
    role: "participant",
    nom_organisation: "",
    description_organisation: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData({ ...formData, [name]: value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    
    if (formData.role === "organisateur" && !formData.nom_organisation) {
      setError("Le nom de l'organisation est obligatoire pour les organisateurs.");
      return;
    }

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await registerUser(formData);
      setSuccess("Compte créé avec succès ! Redirection vers la connexion...");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(err.message || "Erreur lors de l'inscription.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="badge">Inscription</p>
        <h1>Crée ton compte Eventry.</h1>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Pseudo</label>
            <input name="pseudo" placeholder="Lucas_B" value={formData.pseudo} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input type="email" name="email" placeholder="lucas@example.com" value={formData.email} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label>Mot de passe</label>
            <input type="password" name="password" placeholder="••••••••" value={formData.password} onChange={handleChange} required />
          </div>

          <div className="form-group">
            <label>Type de compte</label>
            <select name="role" value={formData.role} onChange={handleChange} style={{ background: 'rgba(255,255,255,0.08)', color: 'white', padding: '15px', borderRadius: '14px', border: '1px solid var(--border)' }}>
              <option value="participant">Participant (Je cherche des événements)</option>
              <option value="organisateur" style={{ color: 'black' }}>Organisateur (Je crée des événements)</option>
            </select>
          </div>

          {formData.role === "organisateur" && (
            <div style={{ marginTop: '10px', padding: '15px', background: 'rgba(198, 40, 74, 0.1)', borderRadius: '15px', border: '1px solid var(--red)' }}>
              <div className="form-group">
                <label>Nom de l'organisation</label>
                <input name="nom_organisation" placeholder="Collectif RAVE" value={formData.nom_organisation} onChange={handleChange} required />
              </div>
              <div className="form-group">
                <label>Description de l'activité</label>
                <textarea name="description_organisation" placeholder="Décris tes événements..." value={formData.description_organisation} onChange={handleChange} />
              </div>
            </div>
          )}

          {success && <p className="form-success">{success}</p>}
          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? "Création..." : "Créer mon compte"}
          </button>
        </form>

        <p className="auth-link">Déjà inscrit ? <Link to="/login">Se connecter</Link></p>
      </section>
    </main>
  );
}

export default Register;