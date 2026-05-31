import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getEventById } from "../api/eventsApi";
import { registerToEvent } from "../api/registrationsApi";
import { getEventReviews } from "../api/reviewsApi";
import { events as mockEvents } from "../data/mockEvents";
import Button from "../components/Button";

const mockReviews = [
  {
    id: "review-1",
    user: {
      pseudo: "Lucas_B",
    },
    note_globale: 4,
    contenu: "Super soirée, ambiance au top et organisation propre.",
  },
  {
    id: "review-2",
    user: {
      pseudo: "Sarah_M",
    },
    note_globale: 5,
    contenu: "Lieu sympa, musique excellente, je recommande.",
  },
];

function EventDetail() {
  const { id } = useParams();

  const [event, setEvent] = useState(null);
  const [reviews, setReviews] = useState(mockReviews);
  const [loading, setLoading] = useState(false);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [error, setError] = useState("");
  const [registerMessage, setRegisterMessage] = useState("");
  const [registerError, setRegisterError] = useState("");

  useEffect(() => {
    async function fetchEvent() {
      try {
        setLoading(true);
        setError("");

        const response = await getEventById(id);
        setEvent(response);
      } catch (err) {
        console.error(err);

        const fallbackEvent =
          mockEvents.find((mockEvent) => String(mockEvent.id) === String(id)) ||
          mockEvents[0];

        setEvent(fallbackEvent);
        setError("API indisponible : affichage des données de démonstration.");
      } finally {
        setLoading(false);
      }
    }

    async function fetchReviews() {
      try {
        setReviewsLoading(true);

        const response = await getEventReviews(id);

        if (Array.isArray(response?.data)) {
          setReviews(response.data);
        } else if (Array.isArray(response)) {
          setReviews(response);
        }
      } catch (err) {
        console.error(err);
        setReviews(mockReviews);
      } finally {
        setReviewsLoading(false);
      }
    }

    fetchEvent();
    fetchReviews();
  }, [id]);

  async function handleRegister() {
    setRegisterMessage("");
    setRegisterError("");

    try {
      const response = await registerToEvent(id, 1);

      if (response?.status === "waiting_list") {
        setRegisterMessage(
          "L’événement est complet : tu as été ajouté à la liste d’attente."
        );
      } else {
        setRegisterMessage("Réservation confirmée avec succès.");
      }
    } catch (err) {
      console.error(err);
      setRegisterError(
        err.message ||
          "Impossible de réserver pour le moment. Connecte-toi ou réessaie plus tard."
      );
    }
  }

  if (loading && !event) {
    return (
      <main className="event-detail-hero">
        <p className="page-message">Chargement de l’événement...</p>
      </main>
    );
  }

  if (!event) {
    return (
      <main className="event-detail-hero">
        <p className="form-error">Événement introuvable.</p>
      </main>
    );
  }

  const venue = event.venue || {
    name: "Lieu non renseigné",
    city: "Ville non renseignée",
  };

  const tags = event.tags || [];

  return (
    <main>
      <section className="event-detail-hero">
        <div className="event-detail-content">
          <span className="event-category">{event.category}</span>

          <h1>{event.title}</h1>

          <p className="event-detail-description">{event.description}</p>

          {error && <p className="form-error">{error}</p>}
          {registerMessage && <p className="form-success">{registerMessage}</p>}
          {registerError && <p className="form-error">{registerError}</p>}

          <div className="event-detail-info">
            <div>
              <strong>Ville</strong>
              <span>{venue.city}</span>
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

          <h2>{venue.name}</h2>

          <p>
            Capacité : {event.capacity} personnes
            <br />
            Note moyenne : {event.average_rating || "Non noté"}/5
          </p>

          <div className="tags-list">
            {tags.map((tag) => (
              <span key={tag}>#{tag}</span>
            ))}
          </div>
        </div>
      </section>

      <section className="reviews-section">
        <div className="section-title">
          <h2>Avis des participants</h2>
          <p>
            Les avis sont récupérés depuis MongoDB via l’endpoint
            GET /events/:id/reviews.
          </p>
        </div>

        {reviewsLoading && <p className="page-message">Chargement des avis...</p>}

        <div className="reviews-grid">
          {reviews.map((review) => (
            <article className="review-card" key={review.id}>
              <strong>{review.user?.pseudo || "Utilisateur"}</strong>
              <p>{review.contenu}</p>
              <span>Note : {review.note_globale}/5</span>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default EventDetail;