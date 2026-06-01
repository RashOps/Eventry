import { apiRequest } from "./client";

export function getEvents(params = {}) {
  const query = new URLSearchParams(params).toString();

  return apiRequest(`/events${query ? `?${query}` : ""}`);
}

export function getNearbyEvents({ lat, lng, radius = 10000, limit = 20 }) {
  return apiRequest(
    `/events/nearby?lat=${lat}&lng=${lng}&radius=${radius}&limit=${limit}`
  );
}

export function searchEvents(query) {
  return apiRequest(`/events/search?q=${encodeURIComponent(query)}`);
}

export function getEventById(id) {
  return apiRequest(`/events/${id}`);
}

export function createEvent(payload) {
  return apiRequest("/events", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateEvent(id, payload) {
  return apiRequest(`/events/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteEvent(id) {
  return apiRequest(`/events/${id}`, {
    method: "DELETE",
  });
}