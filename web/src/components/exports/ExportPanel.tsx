import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { exportsApi } from "@/api/exports";
import { runsApi } from "@/api/runs";
import { ExportFormat } from "@/types/export";
import { Button } from "@/components/ui/Button";
import { Label, Select } from "@/components/ui/Form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { StatusBadge } from "@/components/common/StatusBadge";

const FORMATS: ExportFormat[] = ["markdown", "html", "json", "csv"];

const REPORT_INCLUDES = [
  "Methodological framework (Braun & Clarke; Nowell et al.; Boyatzis)",
  "Full references",
  "Codebook version",
  "Analysis settings",
  "Braun & Clarke phase status",
  "Number of conversations / turns / segments",
  "Theme summaries",
  "Code summaries",
  "Representative quotes",
  "Co-occurrence matrix",
  "Memos",
  "Audit trail summary",
  "Reliability / adjudication results (if available)",
  "Limitations",
];

export function ExportPanel() {
  const [runId, setRunId] = React.useState("");
  const [format, setFormat] = React.useState<ExportFormat>("markdown");
  const qc = useQueryClient();

  const runs = useQuery({ queryKey: ["runs"], queryFn: () => runsApi.list() });
  const list = useQuery({ queryKey: ["exports", runId], queryFn: () => exportsApi.list(runId || undefined) });

  const create = useMutation({
    mutationFn: () => exportsApi.create(runId, format),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["exports"] }),
  });

  async function download(id: string) {
    const blob = await exportsApi.download(id);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `export-${id}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card className="lg:col-span-2">
        <CardHeader><CardTitle>Generate export</CardTitle></CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-3">
          <div>
            <Label>Analysis run</Label>
            <Select value={runId} onChange={(e) => setRunId(e.target.value)}>
              <option value="">Select…</option>
              {runs.data?.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
            </Select>
          </div>
          <div>
            <Label>Format</Label>
            <Select value={format} onChange={(e) => setFormat(e.target.value as ExportFormat)}>
              {FORMATS.map((f) => <option key={f} value={f}>{f.toUpperCase()}</option>)}
            </Select>
          </div>
          <div className="flex items-end">
            <Button size="sm" disabled={!runId || create.isPending} onClick={() => create.mutate()}>
              {create.isPending ? "Requesting…" : "Generate"}
            </Button>
          </div>
          <div className="md:col-span-3">
            <ul className="mt-2 space-y-1">
              {list.data?.map((e) => (
                <li key={e.id} className="flex items-center justify-between rounded border border-border p-2 text-xs">
                  <div className="flex items-center gap-2">
                    <StatusBadge status={e.status} />
                    <span>{e.format.toUpperCase()}</span>
                    <span className="text-muted-foreground">{e.created_at}</span>
                  </div>
                  <Button size="sm" variant="outline" disabled={e.status !== "ready"} onClick={() => download(e.id)}>
                    Download
                  </Button>
                </li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Report includes</CardTitle></CardHeader>
        <CardContent>
          <ul className="space-y-1 text-xs">
            {REPORT_INCLUDES.map((x) => <li key={x}>• {x}</li>)}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
