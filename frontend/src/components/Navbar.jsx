import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Navbar() {
  const { user, isAuthenticated, isOrganizer, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  function handleLogout() {
    setMenuOpen(false);
    logout();
    navigate("/");
  }

  return (
    <header className="navbar">
      <Link to="/" className="logo" onClick={() => setMenuOpen(false)}>
        Eventry
      </Link>

      <button 
        className={`menu-toggle ${menuOpen ? "open" : ""}`} 
        onClick={() => setMenuOpen(!menuOpen)}
        aria-label="Toggle menu"
      >
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
        <span className="hamburger-line"></span>
      </button>

      <div className={`nav-container ${menuOpen ? "open" : ""}`}>
        <nav onClick={() => setMenuOpen(false)}>
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
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }} className="nav-actions">
            <Link to="/profile" style={{ fontWeight: "700", color: "var(--text)" }} onClick={() => setMenuOpen(false)}>
              Hello, {user.pseudo}
            </Link>
            <button onClick={handleLogout} className="login-btn" style={{ background: "rgba(198, 40, 74, 0.15)", border: "1px solid var(--red)" }}>
              Déconnexion
            </button>
          </div>
        ) : (
          <div style={{ display: "flex", gap: "10px" }} className="nav-actions" onClick={() => setMenuOpen(false)}>
            <Link to="/login" className="login-btn">
              Connexion
            </Link>
            <Link to="/register" className="login-btn" style={{ background: "var(--red)", borderColor: "var(--red)" }}>
              S'inscrire
            </Link>
          </div>
        )}
      </div>
    </header>
  );
}

export default Navbar;