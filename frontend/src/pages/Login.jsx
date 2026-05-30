import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser } from "../api/authApi";

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
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
      const response = await loginUser(formData);

      localStorage.setItem("eventry_token", response.access_token);
      localStorage.setItem("eventry_token_type", response.token_type);

      setSuccess("Connexion réussie.");
      navigate("/events");
    } catch (err) {
      console.error(err);
      setError(
        err.message ||
          "Connexion impossible. Vérifie ton email et ton mot de passe."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="badge">Connexion</p>

        <h1>Connecte-toi à Eventry.</h1>

        <p className="auth-description">
          Accède à tes réservations, réserve tes places et retrouve tes
          événements depuis ton espace personnel.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
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
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </form>

        <p className="auth-link">
          Pas encore de compte ? <Link to="/register">Créer un compte</Link>
        </p>
      </section>
    </main>
  );
}

export default Login;