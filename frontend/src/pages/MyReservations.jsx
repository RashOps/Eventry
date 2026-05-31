import { useEffect, useState } from "react";
import { getUserRegistrations } from "../api/registrationsApi";

const mockReservations = [
  {
    registration_id: 201,
    status: "confirmed",
    places: 2,
    registered_at: "2026-05-15T10:30:00Z",
    event: {
      id: 88,
      title: "Nuit Électro — Warehouse Paris",
      date_start: "2026-07-12T23:00:00Z",
      venue_city: "Paris",
      image_url: "",
    },
  },
  {
    registration_id: 202,
    status: "waiting_list",
    places: 1,
    registered_at: "2026-05-18T14:00:00Z",
    event: {
      id: 89,
      title: "Rooftop Sunset Vibes",
      date_start: "2026-06-22T19:00:00Z",
      venue_city: "Paris",
      image_url: "",
    },
  },
];

function MyReservations() {
  const [reservations, setReservations] = useState(mockReservations);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchReservations() {
      const userId = localStorage.getItem("eventry_user_id");

      if (!userId) {
        return;
      }

      try {
        setLoading(true);
        setError("");

        const response = await getUserRegistrations(userId, {
          page: 1,
          limit: 10,
        });

        setReservations(response.data || []);
      } catch (err) {
        setError(
          err.message ||
            "Impossible de récupérer les réservations pour le moment."
        );
      } finally {
        setLoading(false);
      }
    }

    fetchReservations();
  }, []);

  return (
    <main className="reservations-page">
     <section className="reservations-header">
  <div className="reservations-header-content">
    <p className="badge">Espace participant</p>

    <h1>Gère tes réservations et retrouve tous tes événements.</h1>

    <p>
      Consulte les événements que tu as rejoints, vérifie ton statut
      d’inscription et accède rapidement aux détails de chaque réservation.
    </p>

    <div className="reservations-stats">
      <div>
        <strong>02</strong>
        <span>Réservations</span>
      </div>

      <div>
        <strong>01</strong>
        <span>Confirmée</span>
      </div>

      <div>
        <strong>01</strong>
        <span>En attente</span>
      </div>
    </div>
  </div>

  <div className="reservations-header-card">
    <span>Suivi rapide</span>
    <h2>Tout ton planning événementiel au même endroit</h2>
    <p>
      Eventry centralise tes places réservées, les statuts d’inscription et les
      informations importantes liées à tes événements.
    </p>
  </div>
</section>

      {loading && <p className="page-message">Chargement des réservations...</p>}

      {error && <p className="form-error">{error}</p>}

      <section className="reservations-grid">
        {reservations.map((reservation) => (
          <article className="reservation-card" key={reservation.registration_id}>
            <div className="reservation-image"></div>

            <div className="reservation-content">
              <div className="reservation-top">
                <span
                  className={
                    reservation.status === "confirmed"
                      ? "status-badge confirmed"
                      : "status-badge waiting"
                  }
                >
                  {reservation.status === "confirmed"
                    ? "Confirmée"
                    : "Liste d’attente"}
                </span>

                <span className="reservation-places">
                  {reservation.places} place(s)
                </span>
              </div>

              <h2>{reservation.event.title}</h2>

              <p>
                {reservation.event.venue_city} •{" "}
                {new Date(reservation.event.date_start).toLocaleDateString(
                  "fr-FR"
                )}
              </p>

              <p>
                Réservé le{" "}
                {new Date(reservation.registered_at).toLocaleDateString(
                  "fr-FR"
                )}
              </p>

              <div className="reservation-actions">
                <button className="primary-btn">Voir l’événement</button>
                <button className="secondary-btn">Annuler</button>
              </div>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}

export default MyReservations;