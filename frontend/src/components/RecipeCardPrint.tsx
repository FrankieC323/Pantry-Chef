import type { RecipeCard } from "@/types/api";
import Stamp from "./Stamp";

export default function RecipeCardPrint({ card }: { card: RecipeCard }) {
  return (
    <div className="card-paper break-inside-avoid p-5 space-y-4 print:border-ink/30 print:shadow-none">
      <div className="flex items-start justify-between gap-2 flex-wrap">
        <div>
          <h3 className="font-display text-xl font-semibold">{card.title_en}</h3>
          <p className="font-display text-base italic text-ink-soft">{card.title_es}</p>
        </div>
        <div className="flex gap-1.5 flex-wrap justify-end print:hidden">
          {card.uses_priority_items && <Stamp variant="urgent">Uses priority stock</Stamp>}
          {card.dietary_tags.map((tag) => (
            <Stamp key={tag} variant="warm">
              {tag.replace(/_/g, " ")}
            </Stamp>
          ))}
        </div>
        {/* Print-friendly plain-text tags -- Stamp's rotated styling doesn't reproduce well on paper */}
        <div className="hidden print:block text-xs text-ink-soft">
          {[card.uses_priority_items ? "uses priority stock" : null, ...card.dietary_tags.map((t) => t.replace(/_/g, " "))]
            .filter(Boolean)
            .join(" · ")}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
        <div>
          <p className="font-semibold text-ink-soft uppercase tracking-wide text-xs mb-1">Ingredients</p>
          <ul className="list-disc list-inside space-y-0.5">
            {card.ingredients_en.map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="font-semibold text-ink-soft uppercase tracking-wide text-xs mb-1">Ingredientes</p>
          <ul className="list-disc list-inside space-y-0.5">
            {card.ingredients_es.map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="font-semibold text-ink-soft uppercase tracking-wide text-xs mb-1">Steps</p>
          <ol className="list-decimal list-inside space-y-0.5">
            {card.steps_en.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>
        <div>
          <p className="font-semibold text-ink-soft uppercase tracking-wide text-xs mb-1">Pasos</p>
          <ol className="list-decimal list-inside space-y-0.5">
            {card.steps_es.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>
      </div>

      {(card.notes_en || card.notes_es) && (
        <p className="text-xs text-ink-soft/80 border-t border-ink/10 pt-2">
          {card.notes_en}
          {card.notes_en && card.notes_es && " / "}
          {card.notes_es}
        </p>
      )}
    </div>
  );
}
