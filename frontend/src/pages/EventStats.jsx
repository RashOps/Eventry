import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getEventStats } from "../api/statsApi";

function EventStats() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await getEventStats(id);
        setStats(data);
      } catch (err) {
        setError("Erreur lors du chargement des statistiques.");
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, [id]);

  if (loading) return <p className="page-message">Chargement des analyses...</p>;
  if (error) return <p className="form-error">{error}</p>;

  return (
    <main className="dashboard-page">
      <section className="dashboard-header">
        <div className="dashboard-header-content">
          <p className="badge">Analytics</p>
          <h1>Stats : {stats.title}</h1>
          <p>Analyse croisée des inscriptions (SQL) et des retours d'expérience (NoSQL).</p>
          
          <div className="dashboard-stats">
            <div>
              <strong>{stats.registered_count}</strong>
              <span>Confirmés</span>
            </div>
            <div>
              <strong>{stats.fill_rate}%</strong>
              <span>Taux de remplissage</span>
            </div>
            <div>
              <strong>{stats.reviews.average}/5</strong>
              <span>Note moyenne</span>
            </div>
          </div>
        </div>

        <div className="dashboard-header-card">
          <span>{stats.capacity} places total</span>
          <h2>Distribution des notes</h2>
          <div style={{ marginTop: '10px' }}>
            {Object.entries(stats.reviews.distribution).reverse().map(([note, count]) => (
              <div key={note} style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '5px' }}>
                <span style={{ fontSize: '12px', width: '20px' }}>{note}★</span>
                <div style={{ flex: 1, height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ 
                    width: `${(count / stats.reviews.total) * 100 || 0}%`, 
                    height: '100%', 
                    background: 'var(--red)' 
                  }}></div>
                </div>
                <span style={{ fontSize: '11px' }}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="dashboard-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
        <div className="dashboard-card">
          <h3>Ambiance</h3>
          <strong>{stats.reviews.average_by_criteria.ambiance}/5</strong>
          <p>Basé sur {stats.reviews.total} avis</p>
        </div>
        <div className="dashboard-card">
          <h3>Organisation</h3>
          <strong>{stats.reviews.average_by_criteria.organisation}/5</strong>
          <p>Retours participants</p>
        </div>
        <div className="dashboard-card">
          <h3>Qualité/Prix</h3>
          <strong>{stats.reviews.average_by_criteria.rapport_qualite_prix}/5</strong>
          <p>Satisfaction budgétaire</p>
        </div>
      </section>

      <div style={{ marginTop: '30px', textAlign: 'center' }}>
        <button className="secondary-btn" onClick={() => navigate("/dashboard")}>Retour au Dashboard</button>
      </div>
    </main>
  );
}

export default EventStats;
