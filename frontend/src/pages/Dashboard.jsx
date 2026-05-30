import { useEffect, useState } from "react";
import { getDashboard } from "../api/statsApi";

const mockDashboard = [
  {
    event_id: 88,
    title: "Nuit Électro — Warehouse Paris",
    capacity: 400,
    registered_count: 257,
    fill_rate: 64.25,
    reviews: {
      total: 38,
      average: 4.2,
    },
  },
  {
    event_id: 89,
    title: "Rooftop Sunset Vibes",
    capacity: 120,
    registered_count: 98,
    fill_rate: 81.67,
    reviews: {
      total: 21,
      average: 4.5,
    },
  },
  {
    event_id: 90,
    title: "Festival Neon Night",
    capacity: 800,
    registered_count: 300,
    fill_rate: 37.5,
    reviews: {
      total: 12,
      average: 4.7,
    },
  },
];

function Dashboard() {
  const [eventsStats, setEventsStats] = useState(mockDashboard);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const totalEvents = eventsStats.length;
  const totalRegistered = eventsStats.reduce(
    (total, event) => total + event.registered_count,
    0
  );
  const averageFillRate =
    eventsStats.reduce((total, event) => total + event.fill_rate, 0) /
    eventsStats.length;

  useEffect(() => {
    async function fetchDashboard() {
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
    }

    fetchDashboard();
  }, []);

  return (
    <main className="dashboard-page">
      <section className="dashboard-header">
        <div className="dashboard-header-content">
          <p className="badge">Dashboard organisateur</p>

          <h1>Pilote tes événements et suis leurs performances.</h1>

          <p>
            Consulte le remplissage, le nombre d’inscrits et les avis de tes
            événements afin de suivre leur évolution depuis un espace centralisé.
          </p>

          <div className="dashboard-stats">
            <div>
              <strong>{totalEvents}</strong>
              <span>Événements</span>
            </div>

            <div>
              <strong>{totalRegistered}</strong>
              <span>Inscrits</span>
            </div>

            <div>
              <strong>{averageFillRate.toFixed(1)}%</strong>
              <span>Remplissage moyen</span>
            </div>
          </div>
        </div>

        <div className="dashboard-header-card">
          <span>Analyse SQL + NoSQL</span>
          <h2>Une vue globale pour l’organisateur</h2>
          <p>
            Les données transactionnelles viennent de PostgreSQL et les avis /
            agrégations analytiques reposent sur MongoDB.
          </p>
        </div>
      </section>

      {loading && <p className="page-message">Chargement du dashboard...</p>}
      {error && <p className="form-error">{error}</p>}

      <section className="dashboard-grid">
        {eventsStats.map((event) => (
          <article className="dashboard-card" key={event.event_id}>
            <div className="dashboard-card-top">
              <span className="event-category">Event #{event.event_id}</span>
              <strong>{event.fill_rate.toFixed(1)}%</strong>
            </div>

            <h2>{event.title}</h2>

            <div className="progress-wrapper">
              <div className="progress-bar">
                <span style={{ width: `${event.fill_rate}%` }}></span>
              </div>
            </div>

            <div className="dashboard-details">
              <div>
                <strong>{event.registered_count}</strong>
                <span>Inscrits</span>
              </div>

              <div>
                <strong>{event.capacity}</strong>
                <span>Capacité</span>
              </div>

              <div>
                <strong>{event.reviews.average}/5</strong>
                <span>Note moyenne</span>
              </div>

              <div>
                <strong>{event.reviews.total}</strong>
                <span>Avis</span>
              </div>
            </div>

            <button className="card-btn">Voir les statistiques</button>
          </article>
        ))}
      </section>
    </main>
  );
}

export default Dashboard;