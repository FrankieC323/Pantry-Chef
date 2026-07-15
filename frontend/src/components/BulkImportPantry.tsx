import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { pantryApi } from "@/api/pantry";
import { ErrorBanner } from "@/components/Feedback";

export default function BulkImportPantry() {
  const [isOpen, setIsOpen] = useState(false);
  const [rawText, setRawText] = useState("");
  const queryClient = useQueryClient();

  const importMutation = useMutation({
    mutationFn: pantryApi.bulkImport,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pantry"] });
    },
  });

  const handleImport = () => {
    if (!rawText.trim()) return;
    importMutation.mutate(rawText);
  };

  const handleClear = () => {
    setRawText("");
    importMutation.reset();
  };

  return (
    <div className="card-paper p-4">
      <button
        type="button"
        onClick={() => setIsOpen((o) => !o)}
        className="flex items-center justify-between w-full text-left"
      >
        <span className="font-display font-semibold text-sm">
          Paste from a list or spreadsheet
        </span>
        <span className="text-ink-soft text-sm">{isOpen ? "hide" : "open"}</span>
      </button>

      {isOpen && (
        <div className="mt-3 space-y-3">
          <p className="text-xs text-ink-soft/80">
            Paste a range copied from Excel or Google Sheets (name, quantity, unit, category,
            expiration), a comma-separated table, or just a plain list of item names -- one per
            line. Missing or unrecognized fields fall back to sensible defaults.
          </p>
          <textarea
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            placeholder={"canned black beans\t12\tcan\tcanned\t2027-01-01\nrice\t20\tlbs\tgrain\nbananas"}
            rows={6}
            className="w-full rounded-md border border-ink/20 px-3 py-2 text-sm font-mono"
          />
          <div className="flex items-center gap-2">
            <button
              onClick={handleImport}
              disabled={!rawText.trim() || importMutation.isPending}
              className="rounded-md bg-cookbook-600 px-4 py-2 text-sm font-medium text-cream hover:bg-cookbook-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {importMutation.isPending ? "Importing..." : "Import"}
            </button>
            {(rawText || importMutation.data) && (
              <button
                onClick={handleClear}
                className="text-sm text-ink-soft hover:text-cookbook-700 transition-colors"
              >
                Clear
              </button>
            )}
          </div>

          {importMutation.isError && (
            <ErrorBanner message={(importMutation.error as Error).message} />
          )}

          {importMutation.data && (
            <div className="text-sm space-y-2 border-t border-ink/10 pt-3">
              <p className="font-medium">
                Added {importMutation.data.created.length} item
                {importMutation.data.created.length !== 1 ? "s" : ""}.
              </p>
              {importMutation.data.warnings.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-ink-soft">
                    Added, but check these:
                  </p>
                  <ul className="text-xs text-ink-soft/80 list-disc list-inside space-y-0.5 mt-1">
                    {importMutation.data.warnings.map((w, i) => (
                      <li key={i}>{w.reason}</li>
                    ))}
                  </ul>
                </div>
              )}
              {importMutation.data.skipped.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-terracotta-600">Skipped:</p>
                  <ul className="text-xs text-ink-soft/80 list-disc list-inside space-y-0.5 mt-1">
                    {importMutation.data.skipped.map((s, i) => (
                      <li key={i}>
                        "{s.line}" -- {s.reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
