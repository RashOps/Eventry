import { apiRequest } from "./client";

export function registerToEvent(eventId, places = 1) {
  return apiRequest(`/events/${eventId}/register`, {
    method: "POST",
    body: JSON.stringify({ places }),
  });
}

export function cancelRegistration(eventId) {
  return apiRequest(`/events/${eventId}/register`, {
    method: "DELETE",
  });
}

export function getUserRegistrations(userId, params = {}) {
  const query = new URLSearchParams(params).toString();

  return apiRequest(
    `/users/${userId}/registrations${query ? `?${query}` : ""}`
  );
}