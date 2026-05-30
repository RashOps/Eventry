import { events } from "../data/mockEvents";
import EventCard from "../components/EventCard";
import Button from "../components/Button";

function Home() {
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
            <Button>Découvrir les événements</Button>
            <Button variant="secondary">Créer un événement</Button>
          </div>
        </div>

        <div className="hero-card">
          <p className="card-label">À la une</p>
          <h2>Soirée Midnight Pulse</h2>
          <p>Paris • 18 juin 2026</p>
          <span>85 places restantes</span>
        </div>
      </section>

      <section className="search-section">
        <input type="text" placeholder="Rechercher un événement..." />

        <select>
          <option>Catégorie</option>
          <option>Musique</option>
          <option>Soirée</option>
          <option>Anniversaire</option>
          <option>Festival</option>
        </select>

        <select>
          <option>Ville</option>
          <option>Paris</option>
          <option>Lyon</option>
          <option>Marseille</option>
        </select>

        <button className="primary-btn">Rechercher</button>
      </section>

      <section className="events-section">
        <div className="section-title">
          <h2>Événements populaires</h2>
          <p>Découvre les événements disponibles et réserve ta place.</p>
        </div>

        <div className="events-grid">
          {events.map((event) => (
            <EventCard event={event} key={event.id} />
          ))}
        </div>
      </section>
    </main>
  );
}

export default Home;