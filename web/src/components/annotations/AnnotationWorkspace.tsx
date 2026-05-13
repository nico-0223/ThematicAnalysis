import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { annotationsApi, AnnotationFilters } from "@/api/annotations";
import { conversationsApi } from "@/api/conversations";
import { codebooksApi } from "@/api/codebooks";
import { Annotation } from "@/types/annotation";
import { Input, Select, Label } from "@/components/ui/Form";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { AnnotationForm } from "./AnnotationForm";
import { Badge } from "@/components/ui/Badge";

export function AnnotationWorkspace({ runId }: { runId: string }) {
  const [filters, setFilters] = React.useState<AnnotationFilters>({});
  const qc = useQueryClient();

  const conversations = useQuery({ queryKey: ["conversations"], queryFn: () => conversationsApi.list() });
  const codebooks = useQuery({ queryKey: ["codebooks"], queryFn: () => codebooksApi.list() });
  const annotations = useQuery({
    queryKey: ["annotations", runId, filters],
    queryFn: () => annotationsApi.listForRun(runId, filters),
  });

  const upsert = useMutation({
    mutationFn: (body: Partial<Annotation>) => annotationsApi.upsert(runId, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["annotations", runId] }),
  });

  return (
    <div className="space-y-4">
      <div className="grid gap-3 rounded-lg border border-border bg-card p-3 md:grid-cols-5">
        <div>
          <Label>Conversation</Label>
          <Select value={filters.conversation_id ?? ""} onChange={(e) => setFilters((f) => ({ ...f, conversation_id: e.target.value || undefined }))}>
            <option value="">All</option>
            {conversations.data?.map((c) => <option key={c.id} value={c.id}>{c.title || c.id}</option>)}
          </Select>
        </div>
        <div>
          <Label>Speaker</Label>
          <Input value={filters.speaker ?? ""} onChange={(e) => setFilters((f) => ({ ...f, speaker: e.target.value || undefined }))} />
        </div>
        <div>
          <Label>Code</Label>
          <Input value={filters.code_id ?? ""} onChange={(e) => setFilters((f) => ({ ...f, code_id: e.target.value || undefined }))} placeholder="code id" />
        </div>
        <div className="flex items-end gap-2">
          <label className="flex items-center gap-1 text-xs">
            <input type="checkbox" checked={!!filters.low_confidence} onChange={(e) => setFilters((f) => ({ ...f, low_confidence: e.target.checked || undefined }))} />
            Low confidence
          </label>
        </div>
        <div className="flex items-end gap-2">
          <label className="flex items-center gap-1 text-xs">
            <input type="checkbox" checked={!!filters.uncoded} onChange={(e) => setFilters((f) => ({ ...f, uncoded: e.target.checked || undefined }))} />
            Uncoded only
          </label>
        </div>
      </div>

      {annotations.isLoading && <LoadingState />}
      {annotations.isError && <ErrorState message={(annotations.error as Error).message} onRetry={() => annotations.refetch()} />}
      {annotations.data && annotations.data.length === 0 && <EmptyState title="No annotations match filters" />}

      <ul className="space-y-2">
        {annotations.data?.map((a) => (
          <li key={a.id} className="rounded-lg border border-border bg-card p-3 text-sm">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <Badge tone={a.source === "human" ? "success" : a.source === "rule_based" ? "info" : a.source === "ai_assisted" ? "warning" : "muted"}>
                  {a.source.replace("_", " ")}
                </Badge>
                <span className="text-xs text-muted-foreground">segment {a.segment_id}</span>
              </div>
              <span className="text-xs text-muted-foreground">conf {a.confidence ?? "—"}</span>
            </div>
            <p className="mt-1 text-xs"><span className="font-medium">Code:</span> {a.code_name || a.code_id}</p>
            {a.evidence && <p className="mt-1 text-xs whitespace-pre-wrap">{a.evidence}</p>}
            {a.rationale && <p className="mt-1 text-xs text-muted-foreground">Rationale: {a.rationale}</p>}
          </li>
        ))}
      </ul>

      <div className="rounded-lg border border-border bg-card p-3">
        <h3 className="text-sm font-semibold mb-2">New / edit annotation</h3>
        <AnnotationForm
          codebooks={codebooks.data ?? []}
          onSubmit={(body) => upsert.mutate(body)}
          submitting={upsert.isPending}
        />
        {upsert.isError && <p className="mt-2 text-xs text-destructive">{(upsert.error as Error).message}</p>}
      </div>
    </div>
  );
}
