import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { updateUserProfile, deleteAccount } from "../api/usersApi";
import { useNavigate } from "react-router-dom";

function Profile() {
  const { user, login, logout } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    pseudo: user?.pseudo || "",
    avatar_url: user?.avatar_url || "",
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  if (!user) return <p className="page-message">Veuillez vous connecter.</p>;

  function handleChange(e) {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setSuccess("");
    setError("");

    try {
      const updatedUser = await updateUserProfile(user.id, formData);
      // Mettre à jour le contexte global sans changer le token
      login(localStorage.getItem("eventry_token"), updatedUser);
      setSuccess("Profil mis à jour avec succès !");
    } catch (err) {
      setError(err.message || "Erreur lors de la mise à jour.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteAccount() {
    if (window.confirm("Es-tu sûr de vouloir supprimer ton compte ? Cette action est irréversible.")) {
      try {
        await deleteAccount(user.id);
        logout();
        navigate("/");
      } catch (err) {
        alert("Erreur lors de la suppression du compte.");
      }
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="badge">Espace Personnel</p>
        <h1>Mon Profil</h1>
        <p className="auth-description">
          Gère tes informations personnelles et ton identité sur Eventry.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email (Non modifiable)</label>
            <input type="email" value={user.email} disabled style={{ opacity: 0.6 }} />
          </div>

          <div className="form-group">
            <label>Pseudonyme</label>
            <input
              type="text"
              name="pseudo"
              value={formData.pseudo}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>URL de l'avatar</label>
            <input
              type="url"
              name="avatar_url"
              placeholder="https://mon-image.jpg"
              value={formData.avatar_url}
              onChange={handleChange}
            />
          </div>

          <div className="form-group">
            <label>Rôle</label>
            <span className="event-category" style={{ alignSelf: 'flex-start' }}>{user.role}</span>
          </div>

          <p style={{ fontSize: '13px', color: 'var(--muted)' }}>
            Membre depuis le : {new Date(user.date_inscription).toLocaleDateString("fr-FR")}
          </p>

          {success && <p className="form-success">{success}</p>}
          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? "Enregistrement..." : "Sauvegarder les modifications"}
          </button>
        </form>

        {user.role === "participant" && (
          <div style={{ marginTop: '40px', padding: '25px', background: 'rgba(198, 40, 74, 0.08)', borderRadius: '20px', border: '1px solid var(--red)' }}>
            <h3 style={{ margin: '0 0 15px' }}>🚀 Devenir Organisateur</h3>
            <p className="auth-description" style={{ fontSize: '14px' }}>
              Tu souhaites créer tes propres événements ? Remplis ces informations pour activer ton profil professionnel.
            </p>
            <div className="form-group">
              <label>Nom de l'organisation</label>
              <input 
                name="nom_organisation" 
                placeholder="Ex: My Event Studio" 
                value={formData.nom_organisation || ""} 
                onChange={handleChange} 
              />
            </div>
            <div className="form-group">
              <label>Description (optionnel)</label>
              <textarea 
                name="description_organisation" 
                placeholder="Décris ton activité..." 
                value={formData.description_organisation || ""} 
                onChange={handleChange} 
                style={{ minHeight: '80px' }}
              />
            </div>
            <button 
              onClick={async () => {
                if (!formData.nom_organisation) return alert("Le nom de l'organisation est requis.");
                setLoading(true);
                try {
                  const updatedUser = await updateUserProfile(user.id, { 
                    role: "organisateur",
                    nom_organisation: formData.nom_organisation,
                    description_organisation: formData.description_organisation
                  });
                  login(localStorage.getItem("eventry_token"), updatedUser);
                  setSuccess("Félicitations ! Tu es maintenant organisateur.");
                } catch (err) {
                  setError("Échec de l'élévation de rôle.");
                } finally {
                  setLoading(false);
                }
              }}
              className="primary-btn" 
              style={{ marginTop: '10px', background: 'var(--red)' }}
              disabled={loading}
            >
              Passer Organisateur
            </button>
          </div>
        )}

        <div style={{ marginTop: '40px', paddingTop: '20px', borderTop: '1px solid var(--border)' }}>
          <h3 style={{ color: '#ff4f76', marginBottom: '10px' }}>Zone de danger</h3>
          <p className="auth-description" style={{ fontSize: '14px' }}>
            La suppression du compte entraînera la perte de toutes tes réservations et avis.
          </p>
          <button onClick={handleDeleteAccount} className="secondary-btn" style={{ borderColor: '#ff4f76', color: '#ff4f76' }}>
            Supprimer mon compte
          </button>
        </div>
      </section>
    </main>
  );
}

export default Profile;
