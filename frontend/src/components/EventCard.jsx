import { Link } from "react-router-dom";

function EventCard({ event }) {
  return (
    <article className="event-card">
      <div 
        className="event-image" 
        style={{ 
          backgroundImage: event.image_url ? `url(${event.image_url})` : 'none',
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      ></div>

      <div className="event-content">
        <span className="event-category">{event.categorie_name}</span>

        <h3>{event.titre}</h3>

        <p>
          {event.venue.ville} •{" "}
          {new Date(event.date_debut).toLocaleDateString("fr-FR")}
        </p>

        <p style={{ 
          display: '-webkit-box', 
          WebkitLineClamp: '2', 
          WebkitBoxOrient: 'vertical', 
          overflow: 'hidden', 
          fontSize: '14px' 
        }}>
          {event.description}
        </p>

        <div className="event-footer">
          <div>
            <strong>{event.price} €</strong>
            {event.average_rating > 0 && (
              <span style={{ marginLeft: '10px', color: '#facc15', fontWeight: 'bold' }}>
                ⭐ {event.average_rating}
              </span>
            )}
          </div>
          <span style={{ fontSize: '12px' }}>{event.capacite_max} places max</span>
        </div>

        <Link to={`/events/${event.id}`} className="card-btn">
          Détails & Réservation
        </Link>
      </div>
    </article>
  );
}

export default EventCard;