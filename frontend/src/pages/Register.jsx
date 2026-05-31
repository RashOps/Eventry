import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/authApi";

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    pseudo: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setFormData({
      ...formData,
      [name]: value,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      await registerUser(formData);

      setSuccess("Compte créé avec succès. Tu peux maintenant te connecter.");
      navigate("/login");
    } catch (err) {
      console.error(err);
      setError(
        err.message ||
          "Inscription impossible. Vérifie les informations renseignées."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="badge">Inscription</p>

        <h1>Crée ton compte Eventry.</h1>

        <p className="auth-description">
          Rejoins la plateforme pour découvrir des événements, réserver tes
          places et suivre tes inscriptions.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Pseudo</label>
            <input
              type="text"
              name="pseudo"
              placeholder="Lucas_B"
              value={formData.pseudo}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              name="email"
              placeholder="lucas@example.com"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Mot de passe</label>
            <input
              type="password"
              name="password"
              placeholder="MotDePasse123!"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          {success && <p className="form-success">{success}</p>}
          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? "Création..." : "Créer mon compte"}
          </button>
        </form>

        <p className="auth-link">
          Déjà inscrit ? <Link to="/login">Se connecter</Link>
        </p>
      </section>
    </main>
  );
}

export default Register;