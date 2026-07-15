import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ratingsApi } from "@/api/ratings";
import { matcherApi } from "@/api/matcher";
import type { RankedMatch } from "@/types/api";
import Stamp from "./Stamp";
import StarRating from "./StarRating";
import RecipeScaler from "./RecipeScaler";

export default function MatchCard({ match }: { match: RankedMatch }) {
  const [expanded, setExpanded] = useState(false);
  const [stars, setStars] = useState(0);
  const [substitutionFor, setSubstitutionFor] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const rateMutation = useMutation({
    mutationFn: (value: number) => {
      if (!match.recipe_id) throw new Error("Recipe not yet saved");
      return ratingsApi.rate({ recipe_id: match.recipe_id, stars: value });
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["ratings"] }),
  });

  const substituteMutation = useMutation({
    mutationFn: (ingredient: string) => matcherApi.substitute(ingredient),
  });

  function handleRate(value: number) {
    setStars(value);
    rateMutation.mutate(value);
  }

  function handleAskSubstitution(ingredient: string) {
    setSubstitutionFor(ingredient);
    substituteMutation.mutate(ingredient);
  }

  const scoreVariant = match.match_score >= 75 ? "neutral" : match.match_score >= 50 ? "warm" : "urgent";

  return (
    <div className="card-paper p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-display text-xl font-semibold">{match.title}</h3>
            {match.uses_expiring_items && <Stamp variant="urgent">uses expiring items</Stamp>}
          </div>
          <p className="text-sm text-ink-soft mt-1">{match.reasoning}</p>
        </div>
        <Stamp variant={scoreVariant}>{match.match_score}% match</Stamp>
      </div>

      <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm">
        {match.have_ingredients.length > 0 && (
          <div>
            <span className="font-medium text-cookbook-700">Have: </span>
            <span className="text-ink-soft">{match.have_ingredients.join(", ")}</span>
          </div>
        )}
        {match.missing_ingredients.length > 0 && (
          <div>
            <span className="font-medium text-terracotta-600">Missing: </span>
            {match.missing_ingredients.map((ing, i) => (
              <span key={ing}>
                <button
                  className="text-ink-soft underline decoration-dotted hover:text-cookbook-700"
                  onClick={() => handleAskSubstitution(ing)}
                >
                  {ing}
                </button>
                {i < match.missing_ingredients.length - 1 ? ", " : ""}
              </span>
            ))}
          </div>
        )}
      </div>

      {match.substitution_notes && (
        <p className="mt-2 text-sm italic text-ink-soft border-l-2 border-gold-500 pl-3">
          {match.substitution_notes}
        </p>
      )}

      {substitutionFor && (
        <div className="mt-2 text-sm border-l-2 border-cookbook-400 pl-3">
          {substituteMutation.isPending && <span className="text-ink-soft italic">Thinking...</span>}
          {substituteMutation.data && (
            <span className="text-ink-soft">{substituteMutation.data.suggestion}</span>
          )}
        </div>
      )}

      <div className="mt-4 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-3">
          <span className="text-xs text-ink-soft">Rate this:</span>
          <StarRating value={stars} onChange={handleRate} size="sm" />
        </div>
        {match.recipe && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm font-medium text-cookbook-700 hover:text-cookbook-600"
          >
            {expanded ? "Hide recipe" : "View recipe →"}
          </button>
        )}
      </div>

      {expanded && match.recipe && (
        <div className="mt-4 border-t border-ink/10 pt-4 space-y-4">
          <RecipeScaler recipe={match.recipe} />
          <div>
            <h4 className="font-display font-semibold mb-2">Instructions</h4>
            <p className="text-sm text-ink-soft whitespace-pre-line">{match.recipe.instructions}</p>
          </div>
          {match.recipe.source_url && (
            <a
              href={match.recipe.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-cookbook-700 underline"
            >
              View original source
            </a>
          )}
        </div>
      )}
    </div>
  );
}
