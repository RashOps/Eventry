import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getEvents, getNearbyEvents, searchEvents } from "../api/eventsApi";
import { events as mockEvents } from "../data/mockEvents";
import EventCard from "../components/EventCard";

function Events() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [events, setEvents] = useState([]);
  const [search, setSearch] = useState(searchParams.get("q") || "");
  const [category, setCategory] = useState(searchParams.get("category") || "");
  const [city, setCity] = useState(searchParams.get("city") || "");
  const [sort, setSort] = useState("date_asc");
  const [priceMax, setPriceMax] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // États pour les modes de recherche avancés
  const [isGeoMode, setIsGeoMode] = useState(false);
  const [isSearchMode, setIsSearchMode] = useState(!!searchParams.get("q"));
  const [geoLoading, setGeoLoading] = useState(false);

  async function fetchEvents() {
    try {
      setLoading(true);
      setError("");
      // Ne pas reset isSearchMode si on a un paramètre q
      if (!searchParams.get("q")) setIsSearchMode(false);
      setIsGeoMode(false);

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

  // --- RECHERCHE FULL-TEXT (MongoDB Index Text) ---
  async function handleSearchSubmit(e) {
    if (e) e.preventDefault();
    
    // Mettre à jour l'URL
    const newParams = new URLSearchParams(searchParams);
    if (search) newParams.set("q", search); else newParams.delete("q");
    setSearchParams(newParams);

    if (search.length < 3) return fetchEvents();

    try {
      setLoading(true);
      setError("");
      setIsGeoMode(false);
      
      const response = await searchEvents(search);
      setEvents(response || []);
      setIsSearchMode(true);
      
      setCity("");
      setCategory("");
    } catch (err) {
      setError("Erreur lors de la recherche textuelle.");
    } finally {
      setLoading(false);
    }
  }

  // --- RECHERCHE GÉOSPATIALE (MongoDB Index 2dsphere) ---
  async function handleNearbySearch() {
    if (!navigator.geolocation) {
      alert("La géolocalisation n'est pas supportée par ton navigateur.");
      return;
    }

    setGeoLoading(true);
    setError("");
    setSearch(""); // Vider la recherche textuelle

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          const response = await getNearbyEvents({
            lat: latitude,
            lng: longitude,
            radius: 10000 // 10km par défaut
          });

          setEvents(response || []);
          setIsGeoMode(true);
          setIsSearchMode(false);
          setCity("");
          setCategory("");
        } catch (err) {
          setError("Impossible de récupérer les événements à proximité.");
        } finally {
          setGeoLoading(false);
        }
      },
      (err) => {
        setGeoLoading(false);
        alert("Permission de géolocalisation refusée.");
      }
    );
  }

  function handleReset() {
    setSearch("");
    setCategory("");
    setCity("");
    setPriceMax("");
    setSort("date_asc");
    fetchEvents();
  }

  useEffect(() => {
    // Si on n'est pas en mode recherche textuelle ou géo, on charge la liste normale
    if (!isSearchMode && !isGeoMode) {
      fetchEvents();
    }
  }, [category, city, sort, priceMax]);

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
        <strong>{events.length}</strong>
        <span>Disponibles</span>
      </div>
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
        <form onSubmit={handleSearchSubmit} style={{ display: 'contents' }}>
          <input
            type="text"
            placeholder="Rechercher un événement... (Entrée)"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </form>

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

        <button 
          className="primary-btn" 
          onClick={handleNearbySearch} 
          disabled={geoLoading}
          style={{ background: isGeoMode ? 'var(--red)' : 'rgba(255,255,255,0.1)', minWidth: '160px' }}
        >
          {geoLoading ? "📍 Recherche..." : isGeoMode ? "📍 Autour de moi (10km)" : "📍 Autour de moi"}
        </button>
      </section>

      <section className="events-section">
        <div className="section-title">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2>{events.length} événement(s) trouvé(s) {isGeoMode ? "à proximité" : isSearchMode ? "correspondant" : ""}</h2>
            <button onClick={handleReset} style={{ background: 'none', border: 'none', color: '#ff7b9a', cursor: 'pointer', fontWeight: '800' }}>
              Réinitialiser les filtres
            </button>
          </div>

          <p>
            {isGeoMode 
              ? "Les résultats sont triés par distance (Rayon de 10km via MongoDB 2dsphere)." 
              : isSearchMode
              ? "Recherche effectuée sur le titre, la description et les métadonnées (Index Text MongoDB)."
              : "Les filtres utilisés correspondent aux paramètres prévus par l’API : catégorie, ville, prix maximum et tri."}
          </p>
        </div>

        {loading && <p className="page-message">Chargement des événements...</p>}

        {error && <p className="form-error">{error}</p>}

        <div className="events-grid">
          {events.map((event) => (
            <EventCard event={event} key={event.id} />
          ))}
        </div>
      </section>
    </main>
  );
}

export default Events;