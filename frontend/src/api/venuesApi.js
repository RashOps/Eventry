import { apiRequest } from "./client";

export function getVenues() {
  return apiRequest("/venues/");
}
