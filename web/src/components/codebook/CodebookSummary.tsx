import { Codebook } from "@/types/codebook";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

export function CodebookSummary({ codebook }: { codebook: Codebook }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{codebook.name}</CardTitle>
        <p className="text-xs text-muted-foreground">Version {codebook.version}</p>
      </CardHeader>
      <CardContent className="grid gap-2 text-xs sm:grid-cols-2">
        <div>Framework: {codebook.framework ?? "—"}</div>
        <div>Themes: {codebook.themes_count ?? codebook.themes?.length ?? 0}</div>
        <div>Codes: {codebook.codes_count ?? "—"}</div>
        <div>Updated: {codebook.updated_at ?? "—"}</div>
      </CardContent>
    </Card>
  );
}
