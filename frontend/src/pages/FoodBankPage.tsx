import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { foodbankApi } from "@/api/foodbank";
import RecipeCardPrint from "@/components/RecipeCardPrint";
import { Spinner, ErrorBanner, EmptyState } from "@/components/Feedback";
import Stamp from "@/components/Stamp";
import type { GenerationLog } from "@/types/api";

function toggleInSet<T>(set: Set<T>, value: T): Set<T> {
  const next = new Set(set);
  if (next.has(value)) {
    next.delete(value);
  } else {
    next.add(value);
  }
  return next;
}

export default function FoodBankPage() {
  const queryClient = useQueryClient();

  const { data: catalog, isLoading: catalogLoading } = useQuery({
    queryKey: ["foodbank-items"],
    queryFn: foodbankApi.items,
  });

  const historyQuery = useQuery({
    queryKey: ["foodbank-history"],
    queryFn: foodbankApi.history,
  });

  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [priority, setPriority] = useState<Set<string>>(new Set());
  const [dietaryFlags, setDietaryFlags] = useState<Set<string>>(new Set());
  const [equipment, setEquipment] = useState<Set<string>>(new Set());
  const [cardCount, setCardCount] = useState(4);

  // When set, the "cards" section below shows this past batch instead of a
  // fresh generation -- lets staff glance back at a prior day for free.
  const [viewedLog, setViewedLog] = useState<GenerationLog | null>(null);

  const generateMutation = useMutation({
    mutationFn: foodbankApi.generate,
    onSuccess: () => {
      setViewedLog(null);
      queryClient.invalidateQueries({ queryKey: ["foodbank-history"] });
    },
  });

  const handleGenerate = () => {
    generateMutation.mutate({
      available_items: Array.from(selected),
      priority_items: Array.from(priority).filter((item) => selected.has(item)),
      dietary_flags: Array.from(dietaryFlags),
      equipment_constraints: Array.from(equipment),
      card_count: cardCount,
    });
  };

  const displayedCards = viewedLog ? viewedLog.cards : generateMutation.data?.cards;
  const displayedWasMocked = viewedLog ? viewedLog.was_mocked : generateMutation.data?.was_mocked;

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between flex-wrap gap-4 print:hidden">
        <div>
          <h2 className="font-display text-3xl font-semibold">Today's shelf check</h2>
          <p className="text-ink-soft mt-1 max-w-xl">
            Check off what's in stock today. Claude builds a batch of bilingual recipe cards using
            only those items — print and send home with the boxes.
          </p>
        </div>
      </div>

      {catalogLoading && <Spinner label="Loading today's stock list..." />}

      {catalog && (
        <div className="space-y-6 print:hidden">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(catalog.categories).map(([category, items]) => (
              <div key={category} className="card-paper p-4">
                <p className="font-display font-semibold text-sm mb-2">{category}</p>
                <div className="space-y-1.5">
                  {items.map((item) => {
                    const isSelected = selected.has(item);
                    const isPriority = priority.has(item);
                    return (
                      <div key={item} className="flex items-center justify-between gap-2 text-sm">
                        <label className="flex items-center gap-2 cursor-pointer flex-1">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={() => setSelected((s) => toggleInSet(s, item))}
                            className="rounded border-ink/30 text-cookbook-600 focus:ring-cookbook-600"
                          />
                          <span className="capitalize">{item}</span>
                        </label>
                        {isSelected && (
                          <button
                            type="button"
                            onClick={() => setPriority((s) => toggleInSet(s, item))}
                            title="Mark as near-expiry / overstocked -- prioritize using this up"
                            className={[
                              "text-xs px-1.5 py-0.5 rounded-sm border shrink-0 transition-colors",
                              isPriority
                                ? "border-terracotta-500 bg-terracotta-400/10 text-terracotta-600"
                                : "border-ink/15 text-ink-soft/50 hover:text-ink-soft",
                            ].join(" ")}
                          >
                            priority
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="card-paper p-4 space-y-4">
            <div>
              <p className="font-display font-semibold text-sm mb-2">Dietary flags</p>
              <div className="flex flex-wrap gap-2">
                {catalog.dietary_flags.map((flag) => (
                  <button
                    type="button"
                    key={flag}
                    onClick={() => setDietaryFlags((s) => toggleInSet(s, flag))}
                    className={[
                      "text-xs px-2.5 py-1 rounded-sm border capitalize transition-colors",
                      dietaryFlags.has(flag)
                        ? "border-cookbook-600 bg-cookbook-50 text-cookbook-700"
                        : "border-ink/15 text-ink-soft hover:border-ink/30",
                    ].join(" ")}
                  >
                    {flag.replace(/_/g, " ")}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <p className="font-display font-semibold text-sm mb-2">Equipment constraints</p>
              <div className="flex flex-wrap gap-2">
                {catalog.equipment_constraints.map((constraint) => (
                  <button
                    type="button"
                    key={constraint}
                    onClick={() => setEquipment((s) => toggleInSet(s, constraint))}
                    className={[
                      "text-xs px-2.5 py-1 rounded-sm border capitalize transition-colors",
                      equipment.has(constraint)
                        ? "border-cookbook-600 bg-cookbook-50 text-cookbook-700"
                        : "border-ink/15 text-ink-soft hover:border-ink/30",
                    ].join(" ")}
                  >
                    {constraint.replace(/_/g, " ")}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <label className="text-sm font-medium">Number of recipe cards</label>
              <input
                type="number"
                min={1}
                max={8}
                value={cardCount}
                onChange={(e) => setCardCount(Number(e.target.value))}
                className="w-16 rounded-md border border-ink/20 px-2 py-1 text-sm"
              />
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={selected.size === 0 || generateMutation.isPending}
            className="rounded-md bg-cookbook-600 px-5 py-2.5 text-sm font-medium text-cream hover:bg-cookbook-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {generateMutation.isPending ? "Generating..." : "Generate today's cards"}
          </button>
          {selected.size === 0 && (
            <p className="text-xs text-ink-soft/70 -mt-4">Check off at least one item first.</p>
          )}
        </div>
      )}

      {generateMutation.isPending && <Spinner label="Building today's recipe cards..." />}
      {generateMutation.isError && <ErrorBanner message={(generateMutation.error as Error).message} />}

      {displayedCards && displayedCards.length === 0 && (
        <EmptyState
          title="No recipes fit those constraints"
          hint="Try checking off a few more items, or loosen a dietary/equipment flag."
        />
      )}

      {displayedCards && displayedCards.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between print:hidden flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <h3 className="font-display text-xl font-semibold">
                {viewedLog ? "Viewing past batch" : "Today's cards"}
              </h3>
              {viewedLog && (
                <span className="text-xs text-ink-soft/70">
                  {new Date(viewedLog.created_at).toLocaleString(undefined, {
                    month: "short",
                    day: "numeric",
                    hour: "numeric",
                    minute: "2-digit",
                  })}
                </span>
              )}
              {displayedWasMocked && <Stamp variant="neutral">mock data</Stamp>}
            </div>
            <div className="flex items-center gap-2">
              {viewedLog && (
                <button
                  onClick={() => setViewedLog(null)}
                  className="rounded-md border border-ink/15 px-4 py-2 text-sm font-medium text-ink-soft hover:border-ink/30 transition-colors"
                >
                  Back to shelf check
                </button>
              )}
              <button
                onClick={() => window.print()}
                className="rounded-md border border-cookbook-600 px-4 py-2 text-sm font-medium text-cookbook-700 hover:bg-cookbook-50 transition-colors"
              >
                Print cards
              </button>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 print:grid-cols-1 print:gap-6">
            {displayedCards.map((card, i) => (
              <RecipeCardPrint key={i} card={card} />
            ))}
          </div>
        </div>
      )}

      <div className="print:hidden space-y-3">
        <h3 className="font-display text-xl font-semibold">Past batches</h3>
        {historyQuery.isLoading && <Spinner label="Loading past batches..." />}
        {historyQuery.data && historyQuery.data.length === 0 && (
          <EmptyState title="No batches generated yet" hint="Your first generated batch will show up here." />
        )}
        {historyQuery.data && historyQuery.data.length > 0 && (
          <div className="card-paper divide-y divide-ink/8">
            {historyQuery.data.map((log) => (
              <div key={log.id} className="flex items-center justify-between gap-4 px-5 py-3 text-sm">
                <div>
                  <p className="font-medium">
                    {log.cards.length} card{log.cards.length !== 1 ? "s" : ""} ·{" "}
                    {log.available_items.length} items checked
                    {log.was_mocked && <span className="text-ink-soft/60"> · mock</span>}
                  </p>
                  <p className="text-xs text-ink-soft/60 mt-0.5">
                    {new Date(log.created_at).toLocaleString(undefined, {
                      month: "short",
                      day: "numeric",
                      hour: "numeric",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
                <button
                  onClick={() => setViewedLog(log)}
                  className="rounded-md border border-ink/15 px-3 py-1.5 text-xs font-medium text-ink-soft hover:border-ink/30 transition-colors shrink-0"
                >
                  View
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
