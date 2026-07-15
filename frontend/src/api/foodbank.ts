import { api } from "./client";
import type { FoodBankCatalog, FoodBankGenerateRequest, FoodBankGenerateResponse, GenerationLog } from "@/types/api";

export const foodbankApi = {
  items: () => api.get<FoodBankCatalog>("/api/foodbank/items"),
  generate: (payload: FoodBankGenerateRequest) =>
    api.post<FoodBankGenerateResponse>("/api/foodbank/generate", payload),
  history: () => api.get<GenerationLog[]>("/api/foodbank/history"),
};
