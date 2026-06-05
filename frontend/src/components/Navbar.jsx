import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, isAuthenticated, isOrganizer, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <header className="navbar">
      <Link to="/" className="logo">
        Eventry
      </Link>

      <nav>
        <Link to="/">Accueil</Link>
        <Link to="/events">Évènements</Link>
        
        {isAuthenticated && (
          <Link to="/my-reservations">Mes réservations</Link>
        )}

        {isOrganizer && (
          <>
            <Link to="/create-event">Créer</Link>
            <Link to="/dashboard">Dashboard</Link>
          </>
        )}
      </nav>

      {isAuthenticated ? (
        <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
          <Link to="/profile" style={{ fontWeight: "700", color: "var(--text)" }}>
            Hello, {user.pseudo}
          </Link>
          <button onClick={handleLogout} className="login-btn" style={{ background: "rgba(198, 40, 74, 0.15)", border: "1px solid var(--red)" }}>
            Déconnexion
          </button>
        </div>
      ) : (
        <div style={{ display: "flex", gap: "10px" }}>
          <Link to="/login" className="login-btn">
            Connexion
          </Link>
          <Link to="/register" className="login-btn" style={{ background: "var(--red)", borderColor: "var(--red)" }}>
            S'inscrire
          </Link>
        </div>
      )}
    </header>
  );
}

export default Navbar;