import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import { getEventById } from "../api/eventsApi";
import { registerToEvent, getUserRegistrations } from "../api/registrationsApi";
import { getEventReviews, createReview, deleteReview, replyToReview } from "../api/reviewsApi";
import { useAuth } from "../context/AuthContext";
import { events as mockEvents } from "../data/mockEvents";
import Button from "../components/Button";

function EventDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, user, isOrganizer } = useAuth();

  const [event, setEvent] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [isRegistered, setIsRegistered] = useState(false);
  
  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  
  const [error, setError] = useState("");
  const [registerMessage, setRegisterMessage] = useState("");
  const [registerError, setRegisterError] = useState("");

  // État pour le dépôt d'avis
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewData, setReviewData] = useState({
    note_globale: 5,
    ambiance: 5,
    organisation: 5,
    rapport_qualite_prix: 5,
    contenu: ""
  });
  const [reviewSubmitLoading, setReviewSubmitLoading] = useState(false);

  // État pour la réponse organisateur
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyText, setReplyText] = useState("");

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await getEventById(id);
      setEvent(response);

      if (isAuthenticated && user?.id) {
        const userRegs = await getUserRegistrations(user.id);
        const already = userRegs.data?.some(reg => String(reg.event.id) === String(id) && reg.status === "confirmee");
        setIsRegistered(already);
      }
    } catch (err) {
      console.error(err);
      const fallbackEvent = mockEvents.find((m) => String(m.id) === String(id)) || mockEvents[0];
      setEvent(fallbackEvent);
      setError("API indisponible.");
    } finally {
      setLoading(false);
    }
  };

  const fetchReviews = async () => {
    try {
      setReviewsLoading(true);
      const response = await getEventReviews(id);
      setReviews(Array.isArray(response) ? response : []);
    } catch (err) {
      console.error(err);
    } finally {
      setReviewsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    fetchReviews();
  }, [id, isAuthenticated, user]);

  const handleRegister = async () => {
    if (!isAuthenticated) return navigate("/login");
    setRegisterMessage(""); setRegisterError(""); setRegisterLoading(true);
    try {
      const response = await registerToEvent(id, 1);
      if (response?.statut === "liste_attente") {
        setRegisterMessage("Événement complet : ajouté à la liste d'attente.");
      } else {
        setRegisterMessage("Réservation confirmée !");
        setIsRegistered(true);
      }
      fetchData();
    } catch (err) {
      setRegisterError(err.message || "Erreur de réservation.");
    } finally {
      setRegisterLoading(false);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    setReviewSubmitLoading(true);
    try {
      const payload = {
        note_globale: Number(reviewData.note_globale),
        notes_detail: {
          ambiance: Number(reviewData.ambiance),
          organisation: Number(reviewData.organisation),
          rapport_qualite_prix: Number(reviewData.rapport_qualite_prix)
        },
        contenu: reviewData.contenu
      };
      await createReview(id, payload);
      setShowReviewForm(false);
      setReviewData({ note_globale: 5, ambiance: 5, organisation: 5, rapport_qualite_prix: 5, contenu: "" });
      fetchReviews();
    } catch (err) {
      alert(err.message || "Erreur lors du dépôt de l'avis.");
    } finally {
      setReviewSubmitLoading(false);
    }
  };

  const handleDeleteReview = async (reviewId) => {
    if (!window.confirm("Supprimer cet avis ?")) return;
    try {
      await deleteReview(reviewId);
      fetchReviews();
    } catch (err) {
      alert("Erreur lors de la suppression.");
    }
  };

  const handleReplySubmit = async (reviewId) => {
    if (!replyText.trim()) return;
    try {
      await replyToReview(reviewId, { contenu: replyText });
      setReplyingTo(null);
      setReplyText("");
      fetchReviews();
    } catch (err) {
      alert("Erreur lors de la réponse.");
    }
  };

  if (loading && !event) return <main className="event-detail-hero"><p className="page-message">Chargement...</p></main>;
  if (!event) return <main className="event-detail-hero"><p className="form-error">Événement introuvable.</p></main>;

  const isEventOver = new Date(event.date_end) < new Date();
  const canReview = isRegistered && isEventOver && !reviews.some(r => r.user.id === user?.id);

  return (
    <main>
      <section className="event-detail-hero">
        <div className="event-detail-content">
          <span className="event-category">{event.categorie_name}</span>
          <h1>{event.titre}</h1>
          <p className="event-detail-description">{event.description}</p>

          <div className="metadata-display" style={{ marginTop: '20px', padding: '15px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px' }}>
            {event.metadata?.lineup && <p>🎵 <strong>Lineup :</strong> {event.metadata.lineup.join(", ")}</p>}
            {event.metadata?.artistes_exposes && <p>🎨 <strong>Artistes :</strong> {event.metadata.artistes_exposes.join(", ")}</p>}
            {event.metadata?.genres_musicaux && <p>🎹 <strong>Genres :</strong> {event.metadata.genres_musicaux.join(", ")}</p>}
            {event.metadata?.dress_code && <p>👕 <strong>Dress Code :</strong> {event.metadata.dress_code}</p>}
            {event.metadata?.age_minimum && <p>🔞 <strong>Âge minimum :</strong> {event.metadata.age_minimum} ans</p>}
          </div>

          <div className="event-detail-info" style={{ marginTop: '30px' }}>
            <div><strong>Ville</strong><span>{event.venue?.ville}</span></div>
            <div><strong>Date</strong><span>{new Date(event.date_debut).toLocaleDateString("fr-FR")}</span></div>
            <div><strong>Prix</strong><span>{event.prix} €</span></div>
            <div><strong>Places</strong><span>{event.capacite_max}</span></div>
          </div>

          <div className="event-detail-actions" style={{ marginTop: '30px' }}>
            {!isEventOver ? (
              <button 
                className="primary-btn" 
                onClick={handleRegister} 
                disabled={isRegistered || registerLoading}
              >
                {registerLoading ? "Chargement..." : isRegistered ? "Déjà inscrit" : "Réserver ma place"}
              </button>
            ) : (
              canReview && !showReviewForm && (
                <button className="primary-btn" onClick={() => setShowReviewForm(true)}>Déposer un avis</button>
              )
            )}
          </div>

          {showReviewForm && (
            <form onSubmit={handleReviewSubmit} className="auth-form" style={{ marginTop: '30px', padding: '25px', background: 'var(--card)', borderRadius: '20px' }}>
              <h3>Ton avis sur l'événement</h3>
              <div className="form-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px', marginBottom: '15px' }}>
                <div className="form-group"><label>Note globale /5</label><input type="number" min="1" max="5" value={reviewData.note_globale} onChange={e => setReviewData({...reviewData, note_globale: e.target.value})} /></div>
                <div className="form-group"><label>Ambiance /5</label><input type="number" min="1" max="5" value={reviewData.ambiance} onChange={e => setReviewData({...reviewData, ambiance: e.target.value})} /></div>
                <div className="form-group"><label>Organisation /5</label><input type="number" min="1" max="5" value={reviewData.organisation} onChange={e => setReviewData({...reviewData, organisation: e.target.value})} /></div>
                <div className="form-group"><label>Qualité/Prix /5</label><input type="number" min="1" max="5" value={reviewData.rapport_qualite_prix} onChange={e => setReviewData({...reviewData, rapport_qualite_prix: e.target.value})} /></div>
              </div>
              <div className="form-group"><label>Commentaire</label><textarea value={reviewData.contenu} onChange={e => setReviewData({...reviewData, contenu: e.target.value})} placeholder="Raconte-nous ton expérience..." required /></div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button type="submit" className="primary-btn" disabled={reviewSubmitLoading}>Publier</button>
                <button type="button" className="secondary-btn" onClick={() => setShowReviewForm(false)}>Annuler</button>
              </div>
            </form>
          )}
        </div>

        <div className="event-detail-card">
          <p className="card-label">À propos</p>
          <h2>{event.venue?.name}</h2>
          <p>Capacité : {event.capacity} pers.<br />Note : {event.average_rating || "N/A"}/5</p>
          <div className="tags-list">{(event.tags || []).map(tag => <span key={tag}>#{tag}</span>)}</div>
        </div>
      </section>

      <section className="reviews-section">
        <div className="section-title"><h2>Avis des participants ({reviews.length})</h2></div>
        <div className="reviews-grid">
          {reviews.map((review) => (
            <article className="review-card" key={review.id} style={{ position: 'relative' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <strong>{review.user?.pseudo}</strong>
                {review.user?.id === user?.id && (
                  <button onClick={() => handleDeleteReview(review.id)} style={{ background: 'none', border: 'none', color: '#ff4f76', cursor: 'pointer', fontSize: '12px' }}>Supprimer</button>
                )}
              </div>
              <p>{review.contenu}</p>
              <div style={{ fontSize: '13px', color: '#ff7b9a', fontWeight: 'bold' }}>Note : {review.note_globale}/5</div>
              
              {review.reponse_organisateur ? (
                <div style={{ marginTop: '15px', padding: '10px', background: 'rgba(255,255,255,0.05)', borderRadius: '10px', borderLeft: '3px solid var(--red)' }}>
                  <small style={{ color: 'var(--red-soft)', fontWeight: '800' }}>Réponse de l'organisateur :</small>
                  <p style={{ margin: '5px 0 0', fontSize: '14px' }}>{review.reponse_organisateur.contenu}</p>
                </div>
              ) : (
                isOrganizer && event.id_organisateur === user?.organisateur_profil?.id && (
                  <div style={{ marginTop: '15px' }}>
                    {replyingTo === review.id ? (
                      <div>
                        <textarea style={{ minHeight: '60px', fontSize: '13px' }} value={replyText} onChange={e => setReplyText(e.target.value)} placeholder="Ta réponse..." />
                        <div style={{ display: 'flex', gap: '5px', marginTop: '5px' }}>
                          <button className="primary-btn" style={{ padding: '5px 10px', fontSize: '11px' }} onClick={() => handleReplySubmit(review.id)}>Envoyer</button>
                          <button className="secondary-btn" style={{ padding: '5px 10px', fontSize: '11px' }} onClick={() => setReplyingTo(null)}>Annuler</button>
                        </div>
                      </div>
                    ) : (
                      <button className="secondary-btn" style={{ padding: '5px 10px', fontSize: '11px' }} onClick={() => setReplyingTo(review.id)}>Répondre</button>
                    )}
                  </div>
                )
              )}
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

export default EventDetail;