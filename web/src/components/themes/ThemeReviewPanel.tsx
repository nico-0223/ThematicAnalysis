import * as React from "react";
import { CandidateTheme } from "@/types/theme";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Label, Textarea } from "@/components/ui/Form";
import { StatusBadge } from "@/components/common/StatusBadge";

interface Props {
  theme: CandidateTheme;
  onUpdate: (body: Partial<CandidateTheme>) => void;
}

export function ThemeReviewPanel({ theme, onUpdate }: Props) {
  const [name, setName] = React.useState(theme.name);
  const [rationale, setRationale] = React.useState(theme.review_rationale ?? "");

  return (
    <Card>
      <CardHeader className="flex-row items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Candidate theme</span>
            <StatusBadge status={theme.status} />
          </div>
          <Input value={name} onChange={(e) => setName(e.target.value)} className="mt-2" />
          {theme.description && <p className="mt-2 text-xs text-muted-foreground">{theme.description}</p>}
        </div>
        <div className="flex flex-col gap-1.5">
          <Button size="sm" onClick={() => onUpdate({ name, status: "renamed" })}>Save rename</Button>
          <Button size="sm" variant="outline" onClick={() => onUpdate({ status: "flagged" })}>Flag weak</Button>
          <Button size="sm" variant="destructive" onClick={() => onUpdate({ status: "rejected" })}>Reject</Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3 text-xs">
        <div className="grid gap-2 md:grid-cols-3">
          <div>
            <p className="font-medium">Supporting codes</p>
            <ul className="mt-1 list-disc pl-4">
              {(theme.supporting_code_ids ?? []).map((id) => <li key={id}>{id}</li>)}
              {!theme.supporting_code_ids?.length && <li className="text-muted-foreground">none</li>}
            </ul>
          </div>
          <div>
            <p className="font-medium">Supporting segments</p>
            <p className="mt-1">{theme.supporting_segment_ids?.length ?? 0} segment(s)</p>
          </div>
          <div>
            <p className="font-medium">Representative quotes</p>
            <ul className="mt-1 space-y-1">
              {(theme.representative_quotes ?? []).slice(0, 3).map((q, i) => (
                <li key={i} className="italic text-muted-foreground">“{q}”</li>
              ))}
              {!theme.representative_quotes?.length && <li className="text-muted-foreground">—</li>}
            </ul>
          </div>
        </div>
        <div>
          <Label>Review rationale</Label>
          <Textarea rows={2} value={rationale} onChange={(e) => setRationale(e.target.value)} />
          <Button size="sm" variant="outline" className="mt-2" onClick={() => onUpdate({ review_rationale: rationale })}>
            Save rationale
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
