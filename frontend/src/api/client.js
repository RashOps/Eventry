const API_BASE_URL = "http://localhost:8000/api/v1";

export async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem("eventry_token");

  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

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