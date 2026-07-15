import { api } from "./client";
import type { Rating, RatingCreate } from "@/types/api";

export const ratingsApi = {
  list: () => api.get<Rating[]>("/api/ratings"),
  rate: (data: RatingCreate) => api.post<Rating>("/api/ratings", data),
};
