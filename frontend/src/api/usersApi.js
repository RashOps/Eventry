import { apiRequest } from "./client";

/**
 * Récupère les informations publiques d'un utilisateur
 * @param {number} userId 
 */
export function getUserProfile(userId) {
  return apiRequest(`/users/${userId}`);
}

/**
 * Met à jour le profil de l'utilisateur connecté
 * @param {number} userId 
 * @param {Object} payload { pseudo?, avatar_url? }
 */
export function updateUserProfile(userId, payload) {
  return apiRequest(`/users/${userId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

/**
 * Supprime le compte de l'utilisateur
 * @param {number} userId 
 */
export function deleteAccount(userId) {
  return apiRequest(`/users/${userId}`, {
    method: "DELETE",
  });
}
