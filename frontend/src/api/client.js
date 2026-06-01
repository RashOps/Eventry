const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("eventry_token");

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Ne pas écraser le Content-Type s'il est déjà défini (ex: pour le login x-www-form-urlencoded)
  if (options.headers && options.headers["Content-Type"]) {
    headers["Content-Type"] = options.headers["Content-Type"];
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Gestion automatique de l'expiration du token
  if (response.status === 401) {
    localStorage.removeItem("eventry_token");
    // On pourrait déclencher un événement ou rediriger ici si besoin
  }

  if (response.status === 204) {
    return null;
  }

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    throw (
      data || {
        status: response.status,
        error: "API_ERROR",
        message: "Une erreur est survenue.",
      }
    );
  }

  return data;
}