import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser, getCurrentUser } from "../api/authApi";
import { useAuth } from "../context/AuthContext";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

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
      // 1. Authentification pour obtenir le token
      const authResponse = await loginUser(formData);
      
      // Stockage temporaire du token pour l'appel suivant (le client API le récupérera du localStorage dans AuthContext.login plus tard, mais ici on a besoin qu'il soit dispo pour getCurrentUser si on ne passe pas le token explicitement)
      localStorage.setItem("eventry_token", authResponse.access_token);

      // 2. Récupération immédiate du profil complet (pour le rôle)
      const userData = await getCurrentUser();

      // 3. Mise à jour de l'état global
      login(authResponse.access_token, userData);

      setSuccess("Connexion réussie.");
      navigate("/events");
    } catch (err) {
      console.error(err);
      // Nettoyage en cas d'échec
      localStorage.removeItem("eventry_token");
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