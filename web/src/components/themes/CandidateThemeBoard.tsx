import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { themesApi } from "@/api/themes";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { ThemeReviewPanel } from "./ThemeReviewPanel";

export function CandidateThemeBoard({ runId }: { runId: string }) {
  const qc = useQueryClient();
  const themes = useQuery({
    queryKey: ["candidate-themes", runId],
    queryFn: () => themesApi.listCandidates(runId),
  });
  const update = useMutation({
    mutationFn: ({ id, body }: { id: string; body: Parameters<typeof themesApi.update>[2] }) =>
      themesApi.update(runId, id, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["candidate-themes", runId] }),
  });

  if (themes.isLoading) return <LoadingState />;
  if (themes.isError) return <ErrorState message={(themes.error as Error).message} onRetry={() => themes.refetch()} />;
  if (!themes.data?.length)
    return (
      <EmptyState
        title="No candidate themes yet"
        description="Run analysis or generate candidate themes from the backend to begin review."
      />
    );

  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground">
        These are <strong>candidate themes</strong> proposed by the workflow software. They are not final themes — naming,
        merging, splitting, and rejection are researcher decisions.
      </p>
      {themes.data.map((t) => (
        <ThemeReviewPanel
          key={t.id}
          theme={t}
          onUpdate={(body) => update.mutate({ id: t.id, body })}
        />
      ))}
    </div>
  );
}
