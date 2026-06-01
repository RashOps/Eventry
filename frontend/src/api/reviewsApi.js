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

export function updateReview(reviewId, payload) {
  return apiRequest(`/reviews/${reviewId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteReview(reviewId) {
  return apiRequest(`/reviews/${reviewId}`, {
    method: "DELETE",
  });
}

export function replyToReview(reviewId, payload) {
  return apiRequest(`/reviews/${reviewId}/reply`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}