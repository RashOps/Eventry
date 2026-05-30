import { apiRequest } from "./client";

export function getEventStats(eventId) {
  return apiRequest(`/events/${eventId}/stats`);
}

export function getDashboard() {
  return apiRequest("/dashboard");
}