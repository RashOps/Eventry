import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUserRegistrations, cancelRegistration } from "../api/registrationsApi";
import { useAuth } from "../context/AuthContext";

function MyReservations() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMessage, setActionMessage] = useState("");

  const fetchReservations = async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await getUserRegistrations(user.id, {
        page: 1,
        limit: 20,
      });
      setReservations(response.data || []);
    } catch (err) {
      setError(err.message || "Impossible de récupérer tes réservations.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReservations();
  }, [user]);

  const handleCancel = async (eventId) => {
    if (!window.confirm("Veux-tu vraiment annuler cette réservation ?")) return;

    try {
      await cancelRegistration(eventId);
      setActionMessage("Réservation annulée avec succès.");
      // Rafraîchir la liste pour voir le statut 'annulee' (ou la disparition selon ton choix API)
      fetchReservations();
      setTimeout(() => setActionMessage(""), 3000);
    } catch (err) {
      alert("Erreur lors de l'annulation.");
    }
  };

  const confirmedCount = reservations.filter(r => r.status === "confirmee").length;
  const waitingCount = reservations.filter(r => r.status === "liste_attente").length;

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
        <strong>{reservations.length}</strong>
        <span>Réservations</span>
      </div>

      <div>
        <strong>{confirmedCount}</strong>
        <span>Confirmée(s)</span>
      </div>

      <div>
        <strong>{waitingCount}</strong>
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

      {loading && <p className="page-message">Chargement de tes réservations...</p>}
      {!loading && reservations.length === 0 && !error && <p className="page-message">Tu n'as pas encore de réservations.</p>}
      {error && <p className="form-error">{error}</p>}

      <section className="reservations-grid">
        {reservations.map((reservation) => (
          <article className="reservation-card" key={reservation.registration_id}>
            <div className="reservation-image"></div>

            <div className="reservation-content">
              <div className="reservation-top">
                <span
                  className={`status-badge ${
                    reservation.status === "confirmee"
                      ? "confirmed"
                      : reservation.status === "annulee"
                      ? "cancelled"
                      : "waiting"
                  }`}
                  style={reservation.status === "annulee" ? { borderColor: "#ff4f76", color: "#ff4f76", background: "rgba(198, 40, 74, 0.1)" } : {}}
                >
                  {reservation.status === "confirmee"
                    ? "Confirmée"
                    : reservation.status === "annulee"
                    ? "Annulée"
                    : "Liste d’attente"}
                </span>

                <span className="reservation-places">
                  {reservation.places} place(s)
                </span>
              </div>

              <h2>{reservation.event.titre}</h2>

              <p>
                {reservation.event.venue.ville} •{" "}
                {new Date(reservation.event.date_debut).toLocaleDateString(
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
                <button 
                  className="primary-btn" 
                  onClick={() => navigate(`/events/${reservation.event.id}`)}
                >
                  Voir l’événement
                </button>
                <button 
                  className="secondary-btn" 
                  onClick={() => handleCancel(reservation.event.id)}
                  disabled={reservation.status === "annulee"}
                >
                  {reservation.status === "annulee" ? "Annulée" : "Annuler"}
                </button>
              </div>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}

export default MyReservations;