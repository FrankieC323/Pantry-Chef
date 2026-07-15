export function Spinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-ink-soft">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-cookbook-600 border-t-transparent" />
      <span className="font-display italic text-sm">{label}</span>
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="card-paper border-terracotta-500/40 bg-terracotta-400/10 px-4 py-3 text-sm text-terracotta-600">
      <span className="font-semibold">Something went wrong:</span> {message}
    </div>
  );
}

export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="card-paper border-dashed px-6 py-12 text-center">
      <p className="font-display text-lg text-ink-soft">{title}</p>
      {hint && <p className="mt-1 text-sm text-ink-soft/70">{hint}</p>}
    </div>
  );
}
