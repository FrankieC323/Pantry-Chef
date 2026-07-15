import { useMutation, useQueryClient } from "@tanstack/react-query";
import { pantryApi } from "@/api/pantry";
import type { PantryItem } from "@/types/api";
import { categoryLabels, formatExpiration, unitLabels } from "./format";
import Stamp from "./Stamp";

export default function PantryItemRow({ item }: { item: PantryItem }) {
  const queryClient = useQueryClient();
  const expiration = formatExpiration(item.days_until_expiration);

  const deleteMutation = useMutation({
    mutationFn: () => pantryApi.remove(item.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pantry"] }),
  });

  return (
    <div className="flex items-center justify-between gap-4 border-b border-ink/8 py-3 last:border-0">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="font-medium text-ink capitalize">{item.name}</span>
          <span className="text-xs text-ink-soft">
            {item.quantity} {unitLabels[item.unit]}
          </span>
        </div>
        <span className="text-xs text-ink-soft/70">{categoryLabels[item.category]}</span>
      </div>

      <Stamp variant={expiration.variant}>{expiration.label}</Stamp>

      <button
        onClick={() => deleteMutation.mutate()}
        disabled={deleteMutation.isPending}
        aria-label={`Remove ${item.name}`}
        className="text-ink-soft/50 hover:text-terracotta-600 transition-colors text-sm px-2"
      >
        ✕
      </button>
    </div>
  );
}
