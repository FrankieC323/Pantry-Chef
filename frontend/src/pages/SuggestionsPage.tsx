import { useMutation, useQuery } from "@tanstack/react-query";
import { matcherApi } from "@/api/matcher";
import { pantryApi } from "@/api/pantry";
import MatchCard from "@/components/MatchCard";
import { Spinner, ErrorBanner, EmptyState } from "@/components/Feedback";

export default function SuggestionsPage() {
  const { data: pantryItems } = useQuery({ queryKey: ["pantry"], queryFn: pantryApi.list });

  const suggestMutation = useMutation({
    mutationFn: matcherApi.suggest,
  });

  const hasPantry = (pantryItems?.length ?? 0) > 0;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h2 className="font-display text-3xl font-semibold">What can I cook?</h2>
          <p className="text-ink-soft mt-1 max-w-xl">
            Claude looks at your pantry — prioritizing what's about to expire — and ranks the best
            matches, with smart substitutions for anything you're missing.
          </p>
        </div>
        <button
          onClick={() => suggestMutation.mutate()}
          disabled={!hasPantry || suggestMutation.isPending}
          className="rounded-md bg-cookbook-600 px-5 py-2.5 text-sm font-medium text-cream hover:bg-cookbook-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
        >
          {suggestMutation.isPending ? "Thinking..." : "Suggest recipes"}
        </button>
      </div>

      {!hasPantry && (
        <EmptyState
          title="Add some pantry items first"
          hint="Head to the Pantry tab and add what you have on hand."
        />
      )}

      {suggestMutation.isPending && <Spinner label="Reading your pantry and thinking it over..." />}

      {suggestMutation.isError && <ErrorBanner message={(suggestMutation.error as Error).message} />}

      {suggestMutation.data && suggestMutation.data.ranked_matches.length === 0 && (
        <EmptyState
          title="No good matches found"
          hint="Try adding a few more pantry staples and suggesting again."
        />
      )}

      {suggestMutation.data && suggestMutation.data.ranked_matches.length > 0 && (
        <div className="space-y-4">
          {suggestMutation.data.ranked_matches
            .slice()
            .sort((a, b) => b.match_score - a.match_score)
            .map((match, i) => (
              <MatchCard key={match.recipe_id ?? `${match.title}-${i}`} match={match} />
            ))}
        </div>
      )}
    </div>
  );
}
