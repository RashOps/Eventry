import { apiRequest } from "./client";

export function getCategories() {
  return apiRequest("/categories/");
}
