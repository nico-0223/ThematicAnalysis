import * as React from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { preprocessingApi, PreprocessingRequest, SegmentationStrategy } from "@/api/preprocessing";
import { conversationsApi } from "@/api/conversations";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input, Label, Select } from "@/components/ui/Form";

const STRATEGIES: SegmentationStrategy[] = ["turn", "sentence", "fixed_size", "custom_placeholder"];

export function PreprocessingPage() {
  const [strategy, setStrategy] = React.useState<SegmentationStrategy>("turn");
  const [fixedSize, setFixedSize] = React.useState(200);
  const [conversationId, setConversationId] = React.useState("");
  const [cleaning, setCleaning] = React.useState({ lowercase: false, strip_urls: true, collapse_whitespace: true });

  const conversations = useQuery({ queryKey: ["conversations"], queryFn: () => conversationsApi.list() });

  const run = useMutation({
    mutationFn: (body: PreprocessingRequest) => preprocessingApi.run(body),
  });

  return (
    <>
      <PageHeader
        title="Preprocessing"
        description="Configure segmentation and conservative cleaning. Processing is performed by the backend."
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Configuration</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div>
              <Label>Segmentation strategy</Label>
              <Select value={strategy} onChange={(e) => setStrategy(e.target.value as SegmentationStrategy)}>
                {STRATEGIES.map((s) => <option key={s} value={s}>{s}</option>)}
              </Select>
            </div>
            {strategy === "fixed_size" && (
              <div>
                <Label>Fixed size (chars)</Label>
                <Input type="number" value={fixedSize} onChange={(e) => setFixedSize(Number(e.target.value))} />
              </div>
            )}
            <fieldset className="space-y-1">
              <legend className="text-xs font-medium">Cleaning</legend>
              {(["lowercase","strip_urls","collapse_whitespace"] as const).map((k) => (
                <label key={k} className="flex items-center gap-2 text-xs">
                  <input
                    type="checkbox"
                    checked={(cleaning as any)[k]}
                    onChange={(e) => setCleaning((c) => ({ ...c, [k]: e.target.checked }))}
                  />
                  {k.replace("_", " ")}
                </label>
              ))}
            </fieldset>
            <div>
              <Label>Scope</Label>
              <Select value={conversationId} onChange={(e) => setConversationId(e.target.value)}>
                <option value="">All conversations</option>
                {conversations.data?.map((c) => <option key={c.id} value={c.id}>{c.title || c.id}</option>)}
              </Select>
            </div>
            <Button
              size="sm"
              disabled={run.isPending}
              onClick={() => run.mutate({
                strategy,
                cleaning,
                conversation_id: conversationId || undefined,
                fixed_size: strategy === "fixed_size" ? fixedSize : undefined,
              })}
            >
              {run.isPending ? "Submitting…" : "Run preprocessing"}
            </Button>
            {run.isError && <p className="text-xs text-destructive">{(run.error as Error).message}</p>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Result</CardTitle></CardHeader>
          <CardContent className="text-xs">
            {!run.data && <p className="text-muted-foreground">Run preprocessing to see segment counts and a preview.</p>}
            {run.data && (
              <div className="space-y-2">
                <p>Conversations processed: {run.data.conversations_processed ?? "—"}</p>
                <p>Segments created: {run.data.segments_created ?? "—"}</p>
                {!!run.data.preview?.length && (
                  <div className="rounded border border-border bg-background max-h-64 overflow-y-auto divide-y divide-border">
                    {run.data.preview.map((p) => (
                      <div key={p.segment_id} className="p-2">
                        <p className="text-[10px] text-muted-foreground">conv {p.conversation_id} · seg {p.segment_id}</p>
                        <p className="whitespace-pre-wrap">{p.text}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
