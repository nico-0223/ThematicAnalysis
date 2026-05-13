import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { env } from "@/lib/env";

export function SettingsPage() {
  return (
    <>
      <PageHeader title="Settings" description="Frontend configuration. Backend is the source of truth for analysis." />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Environment</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-xs">
            <div><span className="text-muted-foreground">App name:</span> {env.appName}</div>
            <div><span className="text-muted-foreground">API base URL:</span> <code>{env.apiBaseUrl}</code></div>
            <div><span className="text-muted-foreground">Auth mode:</span> {env.authMode}</div>
          </CardContent>
        </Card>
        {env.authMode === "disabled" && (
          <Card>
            <CardHeader><CardTitle>Authentication</CardTitle></CardHeader>
            <CardContent className="text-xs text-muted-foreground">
              Authentication disabled. Use only in trusted local or protected deployments.
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
