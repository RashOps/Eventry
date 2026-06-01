import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getDashboard } from "../api/statsApi";
import { deleteEvent } from "../api/eventsApi";
import { useAuth } from "../context/AuthContext";

function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [eventsStats, setEventsStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await getDashboard();

      if (Array.isArray(response?.data)) {
        setEventsStats(response.data);
      }
    } catch (err) {
      setError(
        err.message ||
          "Impossible de récupérer le dashboard pour le moment."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleDelete = async (eventId) => {
    if (!window.confirm("Voulez-vous vraiment annuler/supprimer cet événement ?")) return;
    try {
      await deleteEvent(eventId);
      fetchDashboard();
    } catch (err) {
      alert("Erreur lors de la suppression : " + err.message);
    }
  };

  const totalEvents = eventsStats.length;
  const totalRegistered = eventsStats.reduce(
    (total, event) => total + event.places_occupees,
    0
  );
  const averageFillRate = totalEvents > 0 
    ? eventsStats.reduce((total, event) => total + event.taux_remplissage, 0) / totalEvents 
    : 0;

  return (
    <main className="dashboard-page">
      <section className="dashboard-header">
        <div className="dashboard-header-content">
          <p className="badge">Espace {user?.pseudo}</p>

          <h1>Pilote tes événements et suis leurs performances.</h1>

          <p>
            Consulte le remplissage, le nombre d’inscrits et les performances de tes
            événements afin de suivre leur évolution depuis un espace centralisé.
          </p>

          <div className="dashboard-stats">
            <div>
              <strong>{totalEvents}</strong>
              <span>Événements</span>
            </div>

            <div>
              <strong>{totalRegistered}</strong>
              <span>Inscrits total</span>
            </div>

            <div>
              <strong>{averageFillRate.toFixed(1)}%</strong>
              <span>Remplissage moyen</span>
            </div>
          </div>
        </div>

        <div className="dashboard-header-card">
          <span>Analyse SQL + NoSQL</span>
          <h2>Vue consolidée</h2>
          <p>
            Les données transactionnelles viennent de PostgreSQL et les avis /
            agrégations analytiques reposent sur MongoDB.
          </p>
        </div>
      </section>

      {loading && <p className="page-message">Chargement du dashboard...</p>}
      {!loading && eventsStats.length === 0 && !error && <p className="page-message">Tu n'as pas encore créé d'événements.</p>}
      {error && <p className="form-error">{error}</p>}

      <section className="dashboard-grid">
        {eventsStats.map((event, index) => (
          <article className="dashboard-card" key={index}>
            <div className="dashboard-card-top">
              <span className="event-category">{event.categorie}</span>
              <strong>{event.taux_remplissage.toFixed(1)}%</strong>
            </div>

            <h2>{event.evenement}</h2>

            <div className="progress-wrapper">
              <div className="progress-bar">
                <span style={{ width: `${event.taux_remplissage}%` }}></span>
              </div>
            </div>

            <div className="dashboard-details">
              <div>
                <strong>{event.places_occupees}</strong>
                <span>Inscrits</span>
              </div>

              <div>
                <strong>{event.capacite_max}</strong>
                <span>Capacité</span>
              </div>

              <div>
                <strong>{event.ville}</strong>
                <span>Lieu</span>
              </div>

              <div>
                <strong>{event.taux_remplissage > 80 ? "🔥" : "📈"}</strong>
                <span>Tendance</span>
              </div>
            </div>

            <div className="dashboard-actions" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '15px' }}>
              <button className="primary-btn" style={{ padding: '8px' }} onClick={() => navigate(`/events/${index+1}/stats`)}>Stats</button>
              <button className="secondary-btn" style={{ padding: '8px' }} onClick={() => navigate(`/events/${index+1}/edit`)}>Editer</button>
              <button className="secondary-btn" style={{ padding: '8px', borderColor: '#ff4f76', color: '#ff4f76', gridColumn: 'span 2' }} onClick={() => handleDelete(index+1)}>
                Annuler l'événement
              </button>
            </div>
          </article>
        ))}
      </section>
    </main>
  );
}

export default Dashboard;