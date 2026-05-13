import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { runsApi } from "@/api/runs";
import { PageHeader } from "@/components/common/PageHeader";
import { AnnotationWorkspace } from "@/components/annotations/AnnotationWorkspace";
import { EmptyState } from "@/components/common/EmptyState";
import { Select } from "@/components/ui/Form";

export function AnnotationPage() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const runs = useQuery({ queryKey: ["runs"], queryFn: () => runsApi.list() });
  return (
    <>
      <PageHeader
        title="Annotation workspace"
        description="Human, imported, and rule-based annotations are visually distinguished."
        actions={
          <Select
            value={runId ?? ""}
            onChange={(e) => navigate(e.target.value ? `/annotation/${e.target.value}` : "/annotation")}
            className="w-56"
          >
            <option value="">Select run…</option>
            {runs.data?.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
          </Select>
        }
      />
      {!runId ? <EmptyState title="Select an analysis run" /> : <AnnotationWorkspace runId={runId} />}
    </>
  );
}
