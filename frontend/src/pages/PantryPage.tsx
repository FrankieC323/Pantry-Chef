import { useQuery } from "@tanstack/react-query";
import { pantryApi } from "@/api/pantry";
import AddPantryItemForm from "@/components/AddPantryItemForm";
import BulkImportPantry from "@/components/BulkImportPantry";
import PantryItemRow from "@/components/PantryItemRow";
import { Spinner, ErrorBanner, EmptyState } from "@/components/Feedback";

export default function PantryPage() {
  const { data: items, isLoading, isError, error } = useQuery({
    queryKey: ["pantry"],
    queryFn: pantryApi.list,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-3xl font-semibold">Your pantry</h2>
        <p className="text-ink-soft mt-1">
          What's in stock right now. Items closer to their expiration date get priority when we
          suggest what to cook.
        </p>
      </div>

      <AddPantryItemForm />
      <BulkImportPantry />

      {isLoading && <Spinner label="Reading the shelves..." />}
      {isError && <ErrorBanner message={(error as Error).message} />}

      {items && items.length === 0 && (
        <EmptyState
          title="Your pantry is empty"
          hint="Add a few ingredients above to get started."
        />
      )}

      {items && items.length > 0 && (
        <div className="card-paper p-5">
          <h3 className="font-display text-lg font-semibold mb-2">
            {items.length} item{items.length !== 1 ? "s" : ""}
          </h3>
          <div>
            {items.map((item) => (
              <PantryItemRow key={item.id} item={item} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
