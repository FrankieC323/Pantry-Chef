import { api } from "./client";
import type { MatcherResponse } from "@/types/api";

export const matcherApi = {
  suggest: () => api.post<MatcherResponse>("/api/matcher/suggest"),
  substitute: (missingIngredient: string) =>
    api.post<{ suggestion: string }>("/api/matcher/substitute", {
      missing_ingredient: missingIngredient,
    }),
};
