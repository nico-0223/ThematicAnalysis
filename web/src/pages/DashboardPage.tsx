import { useQuery } from "@tanstack/react-query";
import { conversationsApi } from "@/api/conversations";
import { codebooksApi } from "@/api/codebooks";
import { runsApi } from "@/api/runs";
import { auditApi } from "@/api/audit";
import { exportsApi } from "@/api/exports";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { StatusBadge } from "@/components/common/StatusBadge";
import { BRAUN_CLARKE_PHASES } from "@/types/phase";
import { formatDate } from "@/lib/utils";

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <Card>
      <CardContent className="py-4">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="mt-1 text-2xl font-semibold">{value}</p>
      </CardContent>
    </Card>
  );
}

export function DashboardPage() {
  const conversations = useQuery({ queryKey: ["conversations"], queryFn: () => conversationsApi.list() });
  const codebooks = useQuery({ queryKey: ["codebooks"], queryFn: () => codebooksApi.list() });
  const runs = useQuery({ queryKey: ["runs"], queryFn: () => runsApi.list() });
  const audit = useQuery({ queryKey: ["audit"], queryFn: () => auditApi.list() });
  const exportsQ = useQuery({ queryKey: ["exports"], queryFn: () => exportsApi.list() });

  const anyError =
    conversations.isError || codebooks.isError || runs.isError || audit.isError || exportsQ.isError;

  if (anyError) {
    return (
      <>
        <PageHeader title="Dashboard" description="Overview of the thematic-analysis workspace." />
        <ErrorState
          message="The frontend could not reach one or more backend endpoints."
          onRetry={() => {
            conversations.refetch(); codebooks.refetch(); runs.refetch(); audit.refetch(); exportsQ.refetch();
          }}
        />
      </>
    );
  }

  const loading = conversations.isLoading || codebooks.isLoading || runs.isLoading;
  if (loading) {
    return (
      <>
        <PageHeader title="Dashboard" />
        <LoadingState />
      </>
    );
  }

  const totalTurns = conversations.data?.reduce((s, c) => s + (c.turns_count ?? 0), 0) ?? 0;
  const totalSegments = conversations.data?.reduce((s, c) => s + (c.segments_count ?? 0), 0) ?? 0;
  const activeCodebook = codebooks.data?.[0];
  const latestRun = runs.data?.[0];

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Software supports the workflow; researchers provide the substantive interpretation."
      />

      <div className="grid gap-3 md:grid-cols-3 lg:grid-cols-5 mb-6">
        <Stat label="Conversations" value={conversations.data?.length ?? 0} />
        <Stat label="Turns" value={totalTurns} />
        <Stat label="Segments" value={totalSegments} />
        <Stat label="Analysis runs" value={runs.data?.length ?? 0} />
        <Stat
          label="Active codebook"
          value={activeCodebook ? `${activeCodebook.name} v${activeCodebook.version}` : "—"}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Latest run</CardTitle></CardHeader>
          <CardContent className="text-sm">
            {latestRun ? (
              <div className="space-y-1">
                <p className="font-medium">{latestRun.name}</p>
                <div><StatusBadge status={latestRun.status} /></div>
                <p className="text-xs text-muted-foreground">Updated {formatDate(latestRun.updated_at)}</p>
              </div>
            ) : <p className="text-xs text-muted-foreground">No runs yet.</p>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Braun &amp; Clarke phase summary</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-1 text-xs">
              {BRAUN_CLARKE_PHASES.map((p) => (
                <li key={p.number} className="flex items-center justify-between">
                  <span>Phase {p.number}: {p.name}</span>
                  <StatusBadge status="not_started" />
                </li>
              ))}
            </ul>
            <p className="mt-2 text-[11px] text-muted-foreground">
              Per-run phase status is shown on the run detail and workflow pages.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Recent audit entries</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-1 text-xs">
              {(audit.data ?? []).slice(0, 6).map((a) => (
                <li key={a.id} className="flex items-center justify-between">
                  <span>{a.action_type}</span>
                  <span className="text-muted-foreground">{formatDate(a.timestamp)}</span>
                </li>
              ))}
              {!audit.data?.length && <li className="text-muted-foreground">No entries.</li>}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Recent exports</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-1 text-xs">
              {(exportsQ.data ?? []).slice(0, 6).map((e) => (
                <li key={e.id} className="flex items-center justify-between">
                  <span>{e.format.toUpperCase()} &middot; {e.run_id}</span>
                  <StatusBadge status={e.status} />
                </li>
              ))}
              {!exportsQ.data?.length && <li className="text-muted-foreground">No exports yet.</li>}
            </ul>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
