import { useQuery } from "@tanstack/react-query";
import { ratingsApi } from "@/api/ratings";
import { recipesApi } from "@/api/recipes";
import StarRating from "@/components/StarRating";
import { Spinner, ErrorBanner, EmptyState } from "@/components/Feedback";

export default function HistoryPage() {
  const ratingsQuery = useQuery({ queryKey: ["ratings"], queryFn: ratingsApi.list });
  const recipesQuery = useQuery({ queryKey: ["recipes"], queryFn: () => recipesApi.list(200) });

  const recipeTitleById = new Map((recipesQuery.data ?? []).map((r) => [r.id, r.title]));

  const isLoading = ratingsQuery.isLoading || recipesQuery.isLoading;
  const error = ratingsQuery.error ?? recipesQuery.error;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-3xl font-semibold">Cooking history</h2>
        <p className="text-ink-soft mt-1">
          Recipes you've rated. This feeds back into your suggestions — Claude leans toward
          ingredients and styles you've rated highly, and away from ones you haven't liked.
        </p>
      </div>

      {isLoading && <Spinner label="Pulling up your ratings..." />}
      {error && <ErrorBanner message={(error as Error).message} />}

      {ratingsQuery.data && ratingsQuery.data.length === 0 && (
        <EmptyState
          title="No ratings yet"
          hint="Rate a recipe from the Suggestions tab after you cook it, and it'll show up here."
        />
      )}

      {ratingsQuery.data && ratingsQuery.data.length > 0 && (
        <div className="card-paper divide-y divide-ink/8">
          {ratingsQuery.data.map((rating) => (
            <div key={rating.id} className="flex items-center justify-between gap-4 px-5 py-4">
              <div>
                <p className="font-medium">{recipeTitleById.get(rating.recipe_id) ?? "Recipe"}</p>
                {rating.notes && <p className="text-sm text-ink-soft mt-0.5">{rating.notes}</p>}
                <p className="text-xs text-ink-soft/60 mt-0.5">
                  {new Date(rating.rated_at).toLocaleDateString(undefined, {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </p>
              </div>
              <StarRating value={rating.stars} readOnly size="sm" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
