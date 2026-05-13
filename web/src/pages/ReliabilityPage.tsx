import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { runsApi } from "@/api/runs";
import { reliabilityApi } from "@/api/reliability";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Form";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { DataTable } from "@/components/common/DataTable";

export function ReliabilityPage() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const runs = useQuery({ queryKey: ["runs"], queryFn: () => runsApi.list() });
  const result = useQuery({
    queryKey: ["reliability", runId],
    queryFn: () => reliabilityApi.get(runId!),
    enabled: !!runId,
    retry: false,
  });
  const compute = useMutation({
    mutationFn: () => reliabilityApi.compute(runId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reliability", runId] }),
  });
  const resolve = useMutation({
    mutationFn: ({ id, resolved }: { id: string; resolved: boolean }) =>
      reliabilityApi.resolveDisagreement(runId!, id, { resolved }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reliability", runId] }),
  });

  return (
    <>
      <PageHeader
        title="Reliability & adjudication"
        description="Reliability statistics are optional and depend on the analytic orientation selected for the project."
        actions={
          <Select
            value={runId ?? ""}
            onChange={(e) => navigate(e.target.value ? `/reliability/${e.target.value}` : "/reliability")}
            className="w-56"
          >
            <option value="">Select run…</option>
            {runs.data?.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
          </Select>
        }
      />

      {!runId && <EmptyState title="Select an analysis run" />}
      {runId && (
        <div className="space-y-4">
          <div className="flex gap-2">
            <Button size="sm" disabled={compute.isPending} onClick={() => compute.mutate()}>
              {compute.isPending ? "Computing…" : "Request reliability calculation"}
            </Button>
          </div>
          {result.isLoading && <LoadingState />}
          {result.isError && <ErrorState message={(result.error as Error).message} onRetry={() => result.refetch()} />}
          {result.data && (
            <>
              <Card>
                <CardHeader><CardTitle>Summary</CardTitle></CardHeader>
                <CardContent className="grid gap-2 text-xs sm:grid-cols-3">
                  <div>Cohen's κ: {result.data.cohens_kappa?.toFixed(3) ?? "—"}</div>
                  <div>Coders: {result.data.coders?.join(", ") ?? "—"}</div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle>Coder comparison</CardTitle></CardHeader>
                <CardContent>
                  <DataTable
                    rows={result.data.comparison ?? []}
                    rowKey={(r) => r.code_id}
                    empty={<EmptyState title="No comparison data" />}
                    columns={[
                      { key: "code", header: "Code", cell: (r) => r.code_name || r.code_id },
                      { key: "agreement", header: "Agreement", cell: (r) => r.agreement.toFixed(2) },
                      { key: "dis", header: "Disagreements", cell: (r) => r.disagreements },
                    ]}
                  />
                </CardContent>
              </Card>
              <Card>
                <CardHeader><CardTitle>Disagreements</CardTitle></CardHeader>
                <CardContent>
                  <DataTable
                    rows={result.data.disagreements ?? []}
                    rowKey={(d) => d.id}
                    empty={<EmptyState title="No disagreements" />}
                    columns={[
                      { key: "seg", header: "Segment", cell: (d) => d.segment_id },
                      { key: "a", header: "Coder A", cell: (d) => `${d.coder_a}: ${d.code_a ?? "—"}` },
                      { key: "b", header: "Coder B", cell: (d) => `${d.coder_b}: ${d.code_b ?? "—"}` },
                      { key: "status", header: "Resolved", cell: (d) => d.resolved ? "yes" : "no" },
                      {
                        key: "act", header: "",
                        cell: (d) => (
                          <Button size="sm" variant="outline" onClick={() => resolve.mutate({ id: d.id, resolved: !d.resolved })}>
                            {d.resolved ? "Mark unresolved" : "Mark resolved"}
                          </Button>
                        ),
                      },
                    ]}
                  />
                </CardContent>
              </Card>
            </>
          )}
        </div>
      )}
    </>
  );
}
