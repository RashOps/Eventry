import { useState } from "react";
import { events } from "../data/mockEvents";
import EventCard from "../components/EventCard";

function Events() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [city, setCity] = useState("");
  const [sort, setSort] = useState("date_asc");

  const filteredEvents = events
    .filter((event) => {
      const matchSearch = event.title
        .toLowerCase()
        .includes(search.toLowerCase());

      const matchCategory = category ? event.category === category : true;
      const matchCity = city ? event.venue.city === city : true;

      return matchSearch && matchCategory && matchCity;
    })
    .sort((a, b) => {
      if (sort === "price_asc") return a.price - b.price;
      if (sort === "rating_desc") return b.average_rating - a.average_rating;
      if (sort === "date_desc") return new Date(b.date_start) - new Date(a.date_start);
      return new Date(a.date_start) - new Date(b.date_start);
    });

  return (
    <main>
      <section className="page-hero">
        <p className="badge">Catalogue Eventry</p>
        <h1>Découvrir les événements</h1>
        <p>
          Recherche une soirée, un festival ou une rencontre près de chez toi,
          puis réserve ta place directement depuis l’application.
        </p>
      </section>

      <section className="filters-section">
        <input
          type="text"
          placeholder="Rechercher un événement..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">Toutes les catégories</option>
          <option value="boite_de_nuit">Boîte de nuit</option>
          <option value="afterwork">Afterwork</option>
          <option value="festival">Festival</option>
        </select>

        <select value={city} onChange={(e) => setCity(e.target.value)}>
          <option value="">Toutes les villes</option>
          <option value="Paris">Paris</option>
          <option value="Lyon">Lyon</option>
        </select>

        <select value={sort} onChange={(e) => setSort(e.target.value)}>
          <option value="date_asc">Date croissante</option>
          <option value="date_desc">Date décroissante</option>
          <option value="price_asc">Prix croissant</option>
          <option value="rating_desc">Meilleures notes</option>
        </select>
      </section>

      <section className="events-section">
        <div className="section-title">
          <h2>{filteredEvents.length} événement(s) trouvé(s)</h2>
          <p>
            Les filtres correspondent aux paramètres prévus par l’API :
            catégorie, ville, tri et recherche.
          </p>
        </div>

        <div className="events-grid">
          {filteredEvents.map((event) => (
            <EventCard event={event} key={event.id} />
          ))}
        </div>
      </section>
    </main>
  );
}

export default Events;