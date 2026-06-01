import { apiRequest } from "./client";

export function registerUser(payload) {
  return apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function loginUser(payload) {
  // FastAPI OAuth2PasswordRequestForm attend du x-www-form-urlencoded
  // Le champ 'username' du backend correspond à l'email de l'utilisateur
  const formData = new URLSearchParams();
  formData.append("username", payload.email);
  formData.append("password", payload.password);

  return apiRequest("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData.toString(),
  });
}

export function logoutUser() {
  return apiRequest("/auth/logout", {
    method: "POST",
  });
}

export function getCurrentUser() {
  return apiRequest("/auth/me");
}