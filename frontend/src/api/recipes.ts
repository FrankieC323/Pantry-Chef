import { api } from "./client";
import type { Recipe } from "@/types/api";

export const recipesApi = {
  list: (limit = 50) => api.get<Recipe[]>(`/api/recipes?limit=${limit}`),
  get: (id: string) => api.get<Recipe>(`/api/recipes/${id}`),
  searchAndCache: (query: string, maxResults = 5) =>
    api.post<Recipe[]>(
      `/api/recipes/search-and-cache?query=${encodeURIComponent(query)}&max_results=${maxResults}`
    ),
};
