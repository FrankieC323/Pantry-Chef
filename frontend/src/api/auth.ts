import { api, authToken, ApiError } from "./client";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface StaffUser {
  id: string;
  username: string;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export const authApi = {
  // OAuth2PasswordRequestForm on the backend expects
  // application/x-www-form-urlencoded, not JSON -- can't reuse api.post here.
  login: async (username: string, password: string): Promise<Token> => {
    const body = new URLSearchParams({ username, password });
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) {
      let detail = res.statusText;
      try {
        const data = await res.json();
        detail = typeof data.detail === "string" ? data.detail : detail;
      } catch {
        // ignore, fall back to statusText
      }
      throw new ApiError(res.status, detail);
    }
    return res.json();
  },

  register: (username: string, password: string) =>
    api.post<StaffUser>("/api/auth/register", { username, password }),

  me: () => api.get<StaffUser>("/api/auth/me"),

  logout: () => authToken.clear(),
};
