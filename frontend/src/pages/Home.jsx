import { useEffect, useState } from "react";
import { getEvents } from "../api/eventsApi";
import EventCard from "../components/EventCard";
import Button from "../components/Button";
import { Link } from "react-router-dom";

function Home() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

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

  return (
    <main>
      <section className="hero">
        <div className="hero-content">
          <p className="badge">Plateforme événementielle</p>

          <h1>Crée, découvre et rejoins des événements près de chez toi.</h1>

          <p>
            Eventry permet aux utilisateurs de créer des soirées, fêtes ou
            rencontres, puis de réserver leur place directement depuis
            l’application.
          </p>

          <div className="hero-actions">
            <Link to="/events"><Button>Découvrir les événements</Button></Link>
            <Link to="/create-event"><Button variant="secondary">Créer un événement</Button></Link>
          </div>
        </div>

        <div className="hero-card">
          <p className="card-label">À la une</p>
          <h2>{events[0]?.titre || "Nuit Électro"}</h2>
          <p>{events[0]?.venue.city || "Paris"} • {events[0] ? new Date(events[0].date_debut).toLocaleDateString("fr-FR") : "12 Juillet 2026"}</p>
          <span>{events[0]?.capacite_max || 400} places total</span>
        </div>
      </section>

      <section className="events-section">
        <div className="section-title">
          <h2>Événements populaires</h2>
          <p>Découvre les événements réels synchronisés depuis le backend.</p>
        </div>

        {loading ? (
          <p className="page-message">Chargement des événements...</p>
        ) : (
          <div className="events-grid">
            {events.map((event) => (
              <EventCard event={event} key={event.id} />
            ))}
            {events.length === 0 && <p className="page-message">Aucun événement disponible pour le moment.</p>}
          </div>
        )}
      </section>
    </main>
  );
}

export default Home;