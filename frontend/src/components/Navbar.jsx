import { Link } from "react-router-dom";

function Navbar() {
  return (
    <header className="navbar">
      <Link to="/" className="logo">
        Eventry
      </Link>

      <nav>
        <Link to="/">Accueil</Link>
        <Link to="/events">Événements</Link>
        <Link to="/create-event">Créer</Link>
        <Link to="/my-reservations">Mes réservations</Link>
        <Link to="/dashboard">Dashboard</Link>
      </nav>

      <Link to="/login" className="login-btn">
        Connexion
      </Link>
    </header>
  );
}

export default Navbar;