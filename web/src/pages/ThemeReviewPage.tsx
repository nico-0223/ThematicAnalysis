import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { runsApi } from "@/api/runs";
import { PageHeader } from "@/components/common/PageHeader";
import { CandidateThemeBoard } from "@/components/themes/CandidateThemeBoard";
import { EmptyState } from "@/components/common/EmptyState";
import { Select } from "@/components/ui/Form";

export function ThemeReviewPage() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const runs = useQuery({ queryKey: ["runs"], queryFn: () => runsApi.list() });
  return (
    <>
      <PageHeader
        title="Theme review"
        description="Review candidate themes proposed by the workflow software. Final naming, merging, and rejection are researcher decisions."
        actions={
          <Select
            value={runId ?? ""}
            onChange={(e) => navigate(e.target.value ? `/themes/${e.target.value}` : "/themes")}
            className="w-56"
          >
            <option value="">Select run…</option>
            {runs.data?.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
          </Select>
        }
      />
      {!runId ? <EmptyState title="Select an analysis run" /> : <CandidateThemeBoard runId={runId} />}
    </>
  );
}
