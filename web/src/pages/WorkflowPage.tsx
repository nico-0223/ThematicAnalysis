import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { phasesApi } from "@/api/phases";
import { runsApi } from "@/api/runs";
import { PageHeader } from "@/components/common/PageHeader";
import { PhaseTimeline } from "@/components/workflow/PhaseTimeline";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { Select } from "@/components/ui/Form";
import { useNavigate } from "react-router-dom";

export function WorkflowPage() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const runs = useQuery({ queryKey: ["runs"], queryFn: () => runsApi.list() });
  const phases = useQuery({
    queryKey: ["phases", runId],
    queryFn: () => phasesApi.listForRun(runId!),
    enabled: !!runId,
  });

  const update = useMutation({
    mutationFn: ({ n, status }: { n: number; status: any }) => phasesApi.update(runId!, n, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["phases", runId] }),
  });

  return (
    <>
      <PageHeader
        title="Braun & Clarke workflow"
        description="The six phases support the analytic process. Substantive interpretation remains the researcher's responsibility."
        actions={
          <Select
            value={runId ?? ""}
            onChange={(e) => navigate(e.target.value ? `/workflow/${e.target.value}` : "/workflow")}
            className="w-56"
          >
            <option value="">Select run…</option>
            {runs.data?.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
          </Select>
        }
      />
      {!runId && <EmptyState title="Select an analysis run to view phases" />}
      {runId && phases.isLoading && <LoadingState />}
      {runId && phases.isError && <ErrorState message={(phases.error as Error).message} onRetry={() => phases.refetch()} />}
      {runId && (
        <PhaseTimeline
          phases={phases.data ?? []}
          onUpdate={(n, status) => update.mutate({ n, status })}
        />
      )}
    </>
  );
}
