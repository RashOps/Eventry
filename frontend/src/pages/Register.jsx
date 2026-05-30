import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { registerUser } from "../api/authApi";

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    pseudo: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
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
    setLoading(true);

    try {
      await registerUser(formData);
      navigate("/login");
    } catch (err) {
      setError(
        err.message || "Impossible de créer le compte. Vérifie les informations."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="badge">Inscription</p>

        <h1>Créer un compte</h1>

        <p className="auth-description">
          Crée ton compte Eventry pour rejoindre des événements et réserver tes
          places.
        </p>

        <form onSubmit={handleSubmit} className="auth-form">
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

          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? "Création..." : "Créer mon compte"}
          </button>
        </form>

        <p className="auth-link">
          Déjà un compte ? <Link to="/login">Se connecter</Link>
        </p>
      </section>
    </main>
  );
}

export default Register;