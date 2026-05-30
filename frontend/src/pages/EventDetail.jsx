import { events } from "../data/mockEvents";
import Button from "../components/Button";

function EventDetail() {
  const event = events[0];

  function handleRegister() {
    alert(
      "Réservation simulée : cet écran sera ensuite relié à POST /events/:id/register"
    );
  }

  return (
    <main>
      <section className="event-detail-hero">
        <div className="event-detail-content">
          <span className="event-category">{event.category}</span>

          <h1>{event.title}</h1>

          <p className="event-detail-description">{event.description}</p>

          <div className="event-detail-info">
            <div>
              <strong>Ville</strong>
              <span>{event.venue.city}</span>
            </div>

            <div>
              <strong>Date</strong>
              <span>
                {new Date(event.date_start).toLocaleDateString("fr-FR")}
              </span>
            </div>

            <div>
              <strong>Prix</strong>
              <span>{event.price} €</span>
            </div>

            <div>
              <strong>Places restantes</strong>
              <span>{event.spots_remaining}</span>
            </div>
          </div>

          <div className="event-detail-actions">
            <Button onClick={handleRegister}>Réserver ma place</Button>
            <Button variant="secondary">Ajouter aux favoris</Button>
          </div>
        </div>

        <div className="event-detail-card">
          <p className="card-label">À propos</p>
          <h2>{event.venue.name}</h2>
          <p>
            Capacité : {event.capacity} personnes
            <br />
            Note moyenne : {event.average_rating}/5
          </p>

          <div className="tags-list">
            {event.tags.map((tag) => (
              <span key={tag}>#{tag}</span>
            ))}
          </div>
        </div>
      </section>

      <section className="reviews-section">
        <div className="section-title">
          <h2>Avis des participants</h2>
          <p>
            Les avis seront récupérés depuis MongoDB via l’endpoint
            GET /events/:id/reviews.
          </p>
        </div>

        <div className="reviews-grid">
          <article className="review-card">
            <strong>Lucas_B</strong>
            <p>Super soirée, ambiance au top et organisation propre.</p>
            <span>Note : 4/5</span>
          </article>

          <article className="review-card">
            <strong>Sarah_M</strong>
            <p>Lieu sympa, musique excellente, je recommande.</p>
            <span>Note : 5/5</span>
          </article>
        </div>
      </section>
    </main>
  );
}

export default EventDetail;