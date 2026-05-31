import { Link } from "react-router-dom";

function EventCard({ event }) {
  return (
    <article className="event-card">
      <div className="event-image"></div>

      <div className="event-content">
        <span className="event-category">{event.category}</span>

        <h3>{event.title}</h3>

        <p>
          {event.venue.city} •{" "}
          {new Date(event.date_start).toLocaleDateString("fr-FR")}
        </p>

        <p>{event.description}</p>

        <div className="event-footer">
          <span>{event.spots_remaining} places restantes</span>
          <strong>{event.price} €</strong>
        </div>

        <Link to={`/events/${event.id}`} className="card-btn">
          Voir l’événement
        </Link>
      </div>
    </article>
  );
}

export default EventCard;