import { api } from "./client";
import type { BulkImportResult, PantryItem, PantryItemCreate } from "@/types/api";

export const pantryApi = {
  list: () => api.get<PantryItem[]>("/api/pantry"),
  expiringSoon: () => api.get<PantryItem[]>("/api/pantry/expiring-soon"),
  create: (data: PantryItemCreate) => api.post<PantryItem>("/api/pantry", data),
  update: (id: string, data: Partial<PantryItemCreate>) =>
    api.patch<PantryItem>(`/api/pantry/${id}`, data),
  remove: (id: string) => api.delete<void>(`/api/pantry/${id}`),
  bulkImport: (rawText: string) =>
    api.post<BulkImportResult>("/api/pantry/bulk", { raw_text: rawText }),
};
