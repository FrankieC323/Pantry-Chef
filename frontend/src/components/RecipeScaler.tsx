import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { scalerApi } from "@/api/scaler";
import type { Recipe } from "@/types/api";

export default function RecipeScaler({ recipe }: { recipe: Recipe }) {
  const [servings, setServings] = useState(recipe.servings);

  const scaleMutation = useMutation({
    mutationFn: (targetServings: number) =>
      scalerApi.scaleRecipe(
        recipe.ingredients.map((ing) => ({ name: ing.name, quantity: ing.quantity, unit: ing.unit })),
        recipe.servings,
        targetServings
      ),
  });

  function handleServingsChange(value: number) {
    const clamped = Math.max(1, value);
    setServings(clamped);
    if (clamped !== recipe.servings) {
      scaleMutation.mutate(clamped);
    }
  }

  const displayIngredients = scaleMutation.data?.ingredients ?? recipe.ingredients;

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-display font-semibold">Ingredients</h4>
        <div className="flex items-center gap-2">
          <span className="text-xs text-ink-soft">Servings:</span>
          <button
            onClick={() => handleServingsChange(servings - 1)}
            className="h-6 w-6 rounded-full border border-ink/15 text-sm hover:bg-cookbook-50"
            aria-label="Decrease servings"
          >
            −
          </button>
          <span className="w-6 text-center text-sm font-medium">{servings}</span>
          <button
            onClick={() => handleServingsChange(servings + 1)}
            className="h-6 w-6 rounded-full border border-ink/15 text-sm hover:bg-cookbook-50"
            aria-label="Increase servings"
          >
            +
          </button>
        </div>
      </div>
      <ul className="text-sm text-ink-soft space-y-1">
        {displayIngredients.map((ing, i) => (
          <li key={i}>
            {ing.quantity != null ? `${ing.quantity} ${ing.unit ?? ""} ` : ""}
            {ing.name}
          </li>
        ))}
      </ul>
      {scaleMutation.isPending && <p className="text-xs text-ink-soft/60 mt-1 italic">Recalculating...</p>}
    </div>
  );
}
