import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { auditApi, AuditFilters } from "@/api/audit";
import { runsApi } from "@/api/runs";
import { PageHeader } from "@/components/common/PageHeader";
import { AuditTrailTable } from "@/components/audit/AuditTrailTable";
import { Input, Label, Select } from "@/components/ui/Form";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";

export function AuditTrailPage() {
  const [filters, setFilters] = React.useState<AuditFilters>({});
  const runs = useQuery({ queryKey: ["runs"], queryFn: () => runsApi.list() });
  const audit = useQuery({ queryKey: ["audit", filters], queryFn: () => auditApi.list(filters) });

  return (
    <>
      <PageHeader
        title="Audit trail"
        description="Chronological record of analysis decisions and configuration changes (Nowell et al., trustworthiness)."
      />
      <div className="grid gap-3 rounded-lg border border-border bg-card p-3 mb-4 md:grid-cols-5">
        <div>
          <Label>Run</Label>
          <Select value={filters.run_id ?? ""} onChange={(e) => setFilters((f) => ({ ...f, run_id: e.target.value || undefined }))}>
            <option value="">All</option>
            {runs.data?.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
          </Select>
        </div>
        <div>
          <Label>Phase</Label>
          <Select value={filters.phase_number?.toString() ?? ""} onChange={(e) => setFilters((f) => ({ ...f, phase_number: e.target.value ? Number(e.target.value) : undefined }))}>
            <option value="">All</option>
            {[1,2,3,4,5,6].map((n) => <option key={n} value={n}>Phase {n}</option>)}
          </Select>
        </div>
        <div>
          <Label>Action type</Label>
          <Input value={filters.action_type ?? ""} onChange={(e) => setFilters((f) => ({ ...f, action_type: e.target.value || undefined }))} />
        </div>
        <div>
          <Label>From</Label>
          <Input type="date" value={filters.from ?? ""} onChange={(e) => setFilters((f) => ({ ...f, from: e.target.value || undefined }))} />
        </div>
        <div>
          <Label>To</Label>
          <Input type="date" value={filters.to ?? ""} onChange={(e) => setFilters((f) => ({ ...f, to: e.target.value || undefined }))} />
        </div>
        <div className="md:col-span-5">
          <Label>Search</Label>
          <Input value={filters.q ?? ""} onChange={(e) => setFilters((f) => ({ ...f, q: e.target.value || undefined }))} />
        </div>
      </div>
      {audit.isLoading && <LoadingState />}
      {audit.isError && <ErrorState message={(audit.error as Error).message} onRetry={() => audit.refetch()} />}
      {audit.data && <AuditTrailTable rows={audit.data} />}
    </>
  );
}
