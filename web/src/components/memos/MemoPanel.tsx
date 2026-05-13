import * as React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { memosApi, MemoFilters } from "@/api/memos";
import { Memo } from "@/types/memo";
import { Input, Select, Label } from "@/components/ui/Form";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";
import { MemoEditor } from "./MemoEditor";
import { Button } from "@/components/ui/Button";

export function MemoPanel() {
  const [filters, setFilters] = React.useState<MemoFilters>({});
  const [editing, setEditing] = React.useState<Partial<Memo> | null>(null);
  const qc = useQueryClient();

  const memos = useQuery({ queryKey: ["memos", filters], queryFn: () => memosApi.list(filters) });

  const save = useMutation({
    mutationFn: (m: Partial<Memo>) => (m.id ? memosApi.update(m.id, m) : memosApi.create(m)),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["memos"] });
      setEditing(null);
    },
  });
  const remove = useMutation({
    mutationFn: (id: string) => memosApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["memos"] }),
  });

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <div className="lg:col-span-2 space-y-3">
        <div className="grid gap-3 rounded-lg border border-border bg-card p-3 md:grid-cols-3">
          <div>
            <Label>Type</Label>
            <Select value={filters.type ?? ""} onChange={(e) => setFilters((f) => ({ ...f, type: e.target.value || undefined }))}>
              <option value="">All</option>
              <option value="analytic">Analytic</option>
              <option value="reflexive">Reflexive</option>
              <option value="method">Method</option>
              <option value="phase">Phase</option>
              <option value="general">General</option>
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
            <Label>Search</Label>
            <Input value={filters.q ?? ""} onChange={(e) => setFilters((f) => ({ ...f, q: e.target.value || undefined }))} />
          </div>
        </div>

        {memos.isLoading && <LoadingState />}
        {memos.isError && <ErrorState message={(memos.error as Error).message} onRetry={() => memos.refetch()} />}
        {memos.data && memos.data.length === 0 && <EmptyState title="No memos yet" />}

        <ul className="space-y-2">
          {memos.data?.map((m) => (
            <li key={m.id} className="rounded-lg border border-border bg-card p-3">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-sm font-medium">{m.title || "(untitled)"}</p>
                  <p className="text-xs text-muted-foreground">
                    {m.type}{m.phase_number ? ` · Phase ${m.phase_number}` : ""}
                  </p>
                </div>
                <div className="flex gap-1">
                  <Button size="sm" variant="ghost" onClick={() => setEditing(m)}>Edit</Button>
                  <Button size="sm" variant="ghost" onClick={() => remove.mutate(m.id)}>Delete</Button>
                </div>
              </div>
              <p className="mt-2 whitespace-pre-wrap text-xs">{m.body}</p>
            </li>
          ))}
        </ul>
      </div>

      <div>
        <Button size="sm" className="mb-2" onClick={() => setEditing({ type: "analytic", body: "" })}>
          New memo
        </Button>
        {editing && (
          <MemoEditor
            memo={editing}
            onChange={setEditing}
            onSave={() => editing && save.mutate(editing)}
            onCancel={() => setEditing(null)}
            saving={save.isPending}
          />
        )}
      </div>
    </div>
  );
}
