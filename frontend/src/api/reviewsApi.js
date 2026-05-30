import { apiRequest } from "./client";

export function getEventReviews(eventId) {
  return apiRequest(`/events/${eventId}/reviews`);
}

export function createReview(eventId, payload) {
  return apiRequest(`/events/${eventId}/reviews`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateReview(eventId, reviewId, payload) {
  return apiRequest(`/events/${eventId}/reviews/${reviewId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteReview(eventId, reviewId) {
  return apiRequest(`/events/${eventId}/reviews/${reviewId}`, {
    method: "DELETE",
  });
}

export function replyToReview(eventId, reviewId, payload) {
  return apiRequest(`/events/${eventId}/reviews/${reviewId}/reply`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}