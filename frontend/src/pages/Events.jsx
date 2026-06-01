import { useEffect, useState } from "react";
import { getEvents } from "../api/eventsApi";
import { events as mockEvents } from "../data/mockEvents";
import EventCard from "../components/EventCard";

function Events() {
  const [events, setEvents] = useState([]); // Initialise à vide au lieu des mocks
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [city, setCity] = useState("");
  const [sort, setSort] = useState("date_asc");
  const [priceMax, setPriceMax] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchEvents() {
    try {
      setLoading(true);
      setError("");

      const params = {
        page: 1,
        limit: 20,
        sort,
      };

      if (category) params.category = category;
      if (city) params.city = city;
      if (priceMax) params.price_max = priceMax;

      const response = await getEvents(params);

      if (Array.isArray(response?.data)) {
        setEvents(response.data);
      } else {
        setEvents([]);
      }
    } catch (err) {
      console.error(err);
      setError("Erreur de connexion à l'API. Affichage des données de secours.");
      setEvents(mockEvents);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchEvents();
  }, [category, city, sort, priceMax]);

  const displayedEvents = events.filter((event) => {
    if (!search) return true;

    const title = event.title?.toLowerCase() || "";
    const query = search.toLowerCase();

    return title.includes(query);
  });

  return (
    <main>
      <section className="events-header">
  <div className="events-header-content">
    <p className="badge">Catalogue Eventry</p>

    <h1>Trouve l’événement qui correspond à ton ambiance.</h1>

    <p>
      Explore les soirées, festivals, afterworks et sorties disponibles autour
      de toi. Filtre par ville, catégorie ou prix, puis réserve ta place en
      quelques clics.
    </p>

    <div className="events-header-stats">
      

      <div>
        <strong>5</strong>
        <span>Catégories</span>
      </div>

     
    </div>
  </div>

  <div className="events-header-card">
    <span>Recherche intelligente</span>
    <h2>Un catalogue connecté aux filtres de l’API Eventry</h2>
    <p>
      La page utilise les paramètres prévus par l’API : catégorie, ville, prix
      maximum, tri et pagination.
    </p>
  </div>
</section>

      <section className="filters-section">
        <input
          type="text"
          placeholder="Rechercher un événement..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />

        <select value={category} onChange={(event) => setCategory(event.target.value)}>
          <option value="">Toutes les catégories</option>
          <option value="boite_de_nuit">Boîte de nuit</option>
          <option value="afterwork">Afterwork</option>
          <option value="festival">Festival</option>
          <option value="expo">Expo</option>
          <option value="sortie">Sortie</option>
        </select>

        <select value={city} onChange={(event) => setCity(event.target.value)}>
          <option value="">Toutes les villes</option>
          <option value="Paris">Paris</option>
          <option value="Lyon">Lyon</option>
          <option value="Marseille">Marseille</option>
        </select>

        <input
          type="number"
          placeholder="Prix max"
          value={priceMax}
          onChange={(event) => setPriceMax(event.target.value)}
        />

        <select value={sort} onChange={(event) => setSort(event.target.value)}>
          <option value="date_asc">Date croissante</option>
          <option value="date_desc">Date décroissante</option>
          <option value="price_asc">Prix croissant</option>
          <option value="rating_desc">Meilleures notes</option>
        </select>
      </section>

      <section className="events-section">
        <div className="section-title">
          <h2>{displayedEvents.length} événement(s) trouvé(s)</h2>

          <p>
            Les filtres utilisés correspondent aux paramètres prévus par l’API :
            catégorie, ville, prix maximum et tri.
          </p>
        </div>

        {loading && <p className="page-message">Chargement des événements...</p>}

        {error && <p className="form-error">{error}</p>}

        <div className="events-grid">
          {displayedEvents.map((event) => (
            <EventCard event={event} key={event.id} />
          ))}
        </div>
      </section>
    </main>
  );
}

export default Events;