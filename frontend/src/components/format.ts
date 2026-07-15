import type { IngredientCategory, Unit } from "@/types/api";

export const categoryLabels: Record<IngredientCategory, string> = {
  produce: "Produce",
  dairy: "Dairy",
  meat_seafood: "Meat & Seafood",
  grain_starch: "Grains & Starches",
  spice_condiment: "Spices & Condiments",
  canned_jarred: "Canned & Jarred",
  frozen: "Frozen",
  baking: "Baking",
  beverage: "Beverages",
  other: "Other",
};

export const unitLabels: Record<Unit, string> = {
  g: "g",
  kg: "kg",
  ml: "ml",
  l: "L",
  tsp: "tsp",
  tbsp: "tbsp",
  cup: "cup",
  fl_oz: "fl oz",
  oz: "oz",
  lb: "lb",
  piece: "pc",
  pinch: "pinch",
};

export function formatExpiration(days: number | null): { label: string; variant: "urgent" | "warm" | "neutral" } {
  if (days === null) return { label: "No expiration", variant: "neutral" };
  if (days < 0) return { label: `Expired ${Math.abs(days)}d ago`, variant: "urgent" };
  if (days === 0) return { label: "Expires today", variant: "urgent" };
  if (days <= 3) return { label: `${days}d left`, variant: "urgent" };
  if (days <= 7) return { label: `${days}d left`, variant: "warm" };
  return { label: `${days}d left`, variant: "neutral" };
}
