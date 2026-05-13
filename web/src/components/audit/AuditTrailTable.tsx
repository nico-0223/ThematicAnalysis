import { AuditEntry } from "@/types/audit";
import { DataTable } from "@/components/common/DataTable";
import { EmptyState } from "@/components/common/EmptyState";
import { formatDate } from "@/lib/utils";

export function AuditTrailTable({ rows }: { rows: AuditEntry[] }) {
  return (
    <DataTable
      rows={rows}
      rowKey={(r) => r.id}
      empty={<EmptyState title="No audit entries" />}
      columns={[
        { key: "ts", header: "Timestamp", cell: (r) => formatDate(r.timestamp) },
        { key: "run", header: "Run", cell: (r) => r.run_id ?? "—" },
        { key: "phase", header: "Phase", cell: (r) => r.phase_number ?? "—" },
        { key: "action", header: "Action", cell: (r) => r.action_type },
        { key: "desc", header: "Description", cell: (r) => r.description ?? "—" },
        {
          key: "diff",
          header: "Before / After",
          cell: (r) => (
            <details>
              <summary className="cursor-pointer text-xs text-muted-foreground">view</summary>
              <pre className="mt-1 max-w-md overflow-auto rounded bg-muted p-2 text-[10px]">
                {JSON.stringify({ before: r.before, after: r.after }, null, 2)}
              </pre>
            </details>
          ),
        },
      ]}
    />
  );
}
