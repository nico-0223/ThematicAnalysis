export function LoadingState({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-card p-6">
      <div className="h-3 w-3 animate-pulse rounded-full bg-primary/60" />
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  );
}
