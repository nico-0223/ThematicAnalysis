import * as React from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { runsApi } from "@/api/runs";
import { codebooksApi } from "@/api/codebooks";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Label, Select } from "@/components/ui/Form";
import { DataTable } from "@/components/common/DataTable";
import { StatusBadge } from "@/components/common/StatusBadge";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";

export function AnalysisRunsPage() {
  const [name, setName] = React.useState("");
  const [codebookId, setCodebookId] = React.useState("");
  const qc = useQueryClient();

  const runs = useQuery({ queryKey: ["runs"], queryFn: () => runsApi.list() });
  const codebooks = useQuery({ queryKey: ["codebooks"], queryFn: () => codebooksApi.list() });

  const create = useMutation({
    mutationFn: () => runsApi.create({ name, codebook_id: codebookId }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["runs"] });
      setName("");
    },
  });

  return (
    <>
      <PageHeader title="Analysis runs" description="Each run pairs a codebook version with a configuration." />

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader><CardTitle>New run</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div>
              <Label>Name</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div>
              <Label>Codebook</Label>
              <Select value={codebookId} onChange={(e) => setCodebookId(e.target.value)}>
                <option value="">Select…</option>
                {codebooks.data?.map((c) => <option key={c.id} value={c.id}>{c.name} v{c.version}</option>)}
              </Select>
            </div>
            <Button size="sm" disabled={!name || !codebookId || create.isPending} onClick={() => create.mutate()}>
              {create.isPending ? "Creating…" : "Create run"}
            </Button>
            {create.isError && <p className="text-xs text-destructive">{(create.error as Error).message}</p>}
          </CardContent>
        </Card>

        <div className="lg:col-span-2">
          {runs.isLoading && <LoadingState />}
          {runs.isError && <ErrorState message={(runs.error as Error).message} onRetry={() => runs.refetch()} />}
          {runs.data && (
            <DataTable
              rows={runs.data}
              rowKey={(r) => r.id}
              empty={<EmptyState title="No runs yet" />}
              columns={[
                {
                  key: "name", header: "Name",
                  cell: (r) => <Link to={`/runs/${r.id}`} className="font-medium hover:underline">{r.name}</Link>,
                },
                { key: "codebook", header: "Codebook", cell: (r) => `${r.codebook_id ?? "—"}${r.codebook_version ? ` v${r.codebook_version}` : ""}` },
                { key: "status", header: "Status", cell: (r) => <StatusBadge status={r.status} /> },
                { key: "created", header: "Created", cell: (r) => formatDate(r.created_at) },
              ]}
            />
          )}
        </div>
      </div>
    </>
  );
}
