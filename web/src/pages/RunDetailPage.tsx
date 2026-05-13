import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { runsApi } from "@/api/runs";
import { phasesApi } from "@/api/phases";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/common/StatusBadge";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { formatDate } from "@/lib/utils";

export function RunDetailPage() {
  const { id } = useParams();
  const qc = useQueryClient();
  const run = useQuery({ queryKey: ["run", id], queryFn: () => runsApi.get(id!), enabled: !!id });
  const phases = useQuery({ queryKey: ["phases", id], queryFn: () => phasesApi.listForRun(id!), enabled: !!id });
  const start = useMutation({
    mutationFn: () => runsApi.start(id!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["run", id] }),
  });

  if (!id) return <ErrorState title="Missing run id" />;
  if (run.isLoading) return <LoadingState />;
  if (run.isError) return <ErrorState message={(run.error as Error).message} onRetry={() => run.refetch()} />;
  if (!run.data) return null;

  const r = run.data;
  return (
    <>
      <PageHeader
        title={r.name}
        description={`Run · ${r.run_type ?? "default"}`}
        actions={
          <>
            <Button size="sm" disabled={start.isPending} onClick={() => start.mutate()}>
              {start.isPending ? "Starting…" : "Run analysis"}
            </Button>
            <Link to={`/workflow/${r.id}`}><Button size="sm" variant="outline">Open workflow</Button></Link>
            <Link to={`/annotation/${r.id}`}><Button size="sm" variant="outline">Annotations</Button></Link>
            <Link to={`/themes/${r.id}`}><Button size="sm" variant="outline">Theme review</Button></Link>
            <Link to={`/exports`}><Button size="sm" variant="outline">Export report</Button></Link>
          </>
        }
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Summary</CardTitle></CardHeader>
          <CardContent className="grid gap-2 text-xs sm:grid-cols-2">
            <div>Codebook: {r.codebook_id ?? "—"} {r.codebook_version ? `v${r.codebook_version}` : ""}</div>
            <div>Status: <StatusBadge status={r.status} /></div>
            <div>Created: {formatDate(r.created_at)}</div>
            <div>Updated: {formatDate(r.updated_at)}</div>
            <div>Annotations: {r.annotation_count ?? 0}</div>
            <div>Candidate themes: {r.candidate_theme_count ?? 0}</div>
            <div>Memos: {r.memo_count ?? 0}</div>
            <div>Export: {r.export_status ?? "—"}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Configuration</CardTitle></CardHeader>
          <CardContent>
            <pre className="max-h-64 overflow-auto rounded bg-muted p-2 text-[10px]">
              {JSON.stringify(r.configuration ?? {}, null, 2)}
            </pre>
          </CardContent>
        </Card>
      </div>

      <div className="mt-4">
        <Card>
          <CardHeader><CardTitle>Phase status</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-1 text-xs">
              {(phases.data ?? []).map((p) => (
                <li key={p.number} className="flex items-center justify-between">
                  <span>Phase {p.number}: {p.name}</span>
                  <StatusBadge status={p.status} />
                </li>
              ))}
              {!phases.data?.length && <li className="text-muted-foreground">No phase data yet.</li>}
            </ul>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
