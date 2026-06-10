import { useEffect, useState } from "react";
import { getEvents } from "../api/eventsApi";
import EventCard from "../components/EventCard";
import Button from "../components/Button";
import { Link, useNavigate } from "react-router-dom";
import { useRefData } from "../context/RefContext";

function Home() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchCategory, setSearchCategory] = useState("");
  const [searchCity, setSearchCity] = useState("");
  const { venues, categories } = useRefData();
  const navigate = useNavigate();

  const cities = [...new Set(venues.map((v) => v.ville))].sort();

  useEffect(() => {
    async function fetchPopularEvents() {
      try {
        setLoading(true);
        // On récupère les événements réels (limité à 3 pour la home)
        const response = await getEvents({ limit: 3, sort: "date_asc" });
        if (Array.isArray(response?.data)) {
          setEvents(response.data);
        }
      } catch (err) {
        console.error("Home API error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchPopularEvents();
  }, []);

  const handleQuickSearch = (e) => {
    if (e) e.preventDefault();
    const params = new URLSearchParams();
    if (searchQuery) params.append("q", searchQuery);
    if (searchCategory) params.append("category", searchCategory);
    if (searchCity) params.append("city", searchCity);
    
    navigate(`/events?${params.toString()}`);
  };

  return (
    <main>
      <section className="hero">
        <div className="hero-content">
          <p className="badge">Plateforme évènementielle</p>

          <h1>Crée, découvre et rejoins des évènements près de chez toi.</h1>

          <p>
            Eventry permet aux utilisateurs de créer des soirées, fêtes ou
            rencontres, puis de réserver leur place directement depuis
            l’application.
          </p>

          <div className="hero-actions">
            <Link to="/events"><Button>Découvrir les évènements</Button></Link>
            <Link to="/create-event"><Button variant="secondary">Créer un évènement</Button></Link>
          </div>
        </div>

        <div className="hero-card">
          <p className="card-label">À la une</p>
          <h2>{events[0]?.titre || "Nuit Électro"}</h2>
          <p>{events[0]?.venue?.ville || "Paris"} • {events[0] ? new Date(events[0].date_debut).toLocaleDateString("fr-FR") : "12 Juillet 2026"}</p>
          <span>{events[0]?.capacite_max || 400} places total</span>
        </div>
      </section>

      <section className="search-section">
        <form onSubmit={handleQuickSearch} style={{ display: 'contents' }}>
          <input 
            type="text" 
            placeholder="Rechercher un événement..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />

          <select value={searchCategory} onChange={(e) => setSearchCategory(e.target.value)}>
            <option value="">Catégorie</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.nom}>
                {cat.nom.replace("_", " ").toUpperCase()}
              </option>
            ))}
          </select>

          <select value={searchCity} onChange={(e) => setSearchCity(e.target.value)}>
            <option value="">Ville</option>
            {cities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          <button type="submit" className="primary-btn">Rechercher</button>
        </form>
      </section>

      <section className="events-section">
        <div className="section-title">
          <h2>Événements populaires</h2>
          <p>Découvre les évènements réels synchronisés depuis le backend.</p>
        </div>

        {loading ? (
          <p className="page-message">Chargement des évènements...</p>
        ) : (
          <div className="events-grid">
            {events.map((event) => (
              <EventCard event={event} key={event.id} />
            ))}
            {events.length === 0 && <p className="page-message">Aucun évènement disponible pour le moment.</p>}
          </div>
        )}
      </section>
    </main>
  );
}

export default Home;
