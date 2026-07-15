import { api } from "./client";
import type { Unit } from "@/types/api";

interface IngredientQty {
  name: string;
  quantity: number | null;
  unit: string | null;
}

export const scalerApi = {
  scaleRecipe: (ingredients: IngredientQty[], originalServings: number, targetServings: number) =>
    api.post<{ ingredients: IngredientQty[] }>("/api/scaler/scale-recipe", {
      ingredients,
      original_servings: originalServings,
      target_servings: targetServings,
    }),
  convertUnit: (quantity: number, fromUnit: Unit, toUnit: Unit) =>
    api.post<{ quantity: number; unit: Unit }>("/api/scaler/convert-unit", {
      quantity,
      from_unit: fromUnit,
      to_unit: toUnit,
    }),
};
