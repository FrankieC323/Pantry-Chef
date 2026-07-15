import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { pantryApi } from "@/api/pantry";
import type { IngredientCategory, PantryItemCreate, Unit } from "@/types/api";
import { categoryLabels, unitLabels } from "./format";

const initialForm: PantryItemCreate = {
  name: "",
  quantity: 1,
  unit: "piece",
  category: "other",
  expiration_date: null,
};

export default function AddPantryItemForm() {
  const [form, setForm] = useState<PantryItemCreate>(initialForm);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (data: PantryItemCreate) => pantryApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
      setForm(initialForm);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    mutation.mutate(form);
  }

  return (
    <form onSubmit={handleSubmit} className="card-paper p-5">
      <h3 className="font-display text-lg font-semibold mb-4">Add to pantry</h3>
      <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
        <input
          type="text"
          placeholder="Ingredient name"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          className="col-span-2 sm:col-span-2 rounded-md border border-ink/15 bg-white px-3 py-2 text-sm focus:border-cookbook-600 focus:outline-none"
          required
        />
        <input
          type="number"
          min={0.01}
          step="any"
          placeholder="Qty"
          value={form.quantity}
          onChange={(e) => setForm({ ...form, quantity: parseFloat(e.target.value) || 0 })}
          className="rounded-md border border-ink/15 bg-white px-3 py-2 text-sm focus:border-cookbook-600 focus:outline-none"
          required
        />
        <select
          value={form.unit}
          onChange={(e) => setForm({ ...form, unit: e.target.value as Unit })}
          className="rounded-md border border-ink/15 bg-white px-3 py-2 text-sm focus:border-cookbook-600 focus:outline-none"
        >
          {Object.entries(unitLabels).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <select
          value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value as IngredientCategory })}
          className="rounded-md border border-ink/15 bg-white px-3 py-2 text-sm focus:border-cookbook-600 focus:outline-none"
        >
          {Object.entries(categoryLabels).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <input
          type="date"
          value={form.expiration_date ?? ""}
          onChange={(e) => setForm({ ...form, expiration_date: e.target.value || null })}
          className="rounded-md border border-ink/15 bg-white px-3 py-2 text-sm focus:border-cookbook-600 focus:outline-none"
        />
      </div>

      <div className="mt-4 flex items-center gap-3">
        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-md bg-cookbook-600 px-4 py-2 text-sm font-medium text-cream hover:bg-cookbook-700 transition-colors disabled:opacity-50"
        >
          {mutation.isPending ? "Adding..." : "Add item"}
        </button>
        {mutation.isError && (
          <span className="text-xs text-terracotta-600">{(mutation.error as Error).message}</span>
        )}
      </div>
    </form>
  );
}
