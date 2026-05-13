import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { conversationsApi } from "@/api/conversations";
import { Input, Select } from "@/components/ui/Form";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { SegmentList } from "./SegmentList";

export function ConversationViewer({ conversationId }: { conversationId: string }) {
  const [speaker, setSpeaker] = React.useState("");
  const [q, setQ] = React.useState("");

  const conv = useQuery({
    queryKey: ["conversation", conversationId],
    queryFn: () => conversationsApi.get(conversationId),
  });
  const turns = useQuery({
    queryKey: ["conversation", conversationId, "turns"],
    queryFn: () => conversationsApi.turns(conversationId),
  });
  const segments = useQuery({
    queryKey: ["conversation", conversationId, "segments", speaker, q],
    queryFn: () => conversationsApi.segments(conversationId, { speaker: speaker || undefined, q: q || undefined }),
  });

  if (conv.isLoading) return <LoadingState />;
  if (conv.isError) return <ErrorState message={(conv.error as Error).message} onRetry={() => conv.refetch()} />;

  const speakers = conv.data?.speakers ?? [];

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <section>
        <h2 className="text-sm font-semibold mb-2">Original turns</h2>
        <div className="rounded-lg border border-border bg-card divide-y divide-border max-h-[600px] overflow-y-auto">
          {turns.data?.map((t) => (
            <div key={t.id} className="p-3 text-sm">
              <p className="text-xs text-muted-foreground">{t.speaker || "—"}</p>
              <p className="mt-0.5 whitespace-pre-wrap">{t.text}</p>
            </div>
          ))}
          {!turns.data?.length && <p className="p-4 text-xs text-muted-foreground">No turns.</p>}
        </div>
      </section>
      <section>
        <div className="flex items-center gap-2 mb-2">
          <h2 className="text-sm font-semibold flex-1">Segments</h2>
          <Select value={speaker} onChange={(e) => setSpeaker(e.target.value)} className="w-32 h-8">
            <option value="">All speakers</option>
            {speakers.map((s) => <option key={s} value={s}>{s}</option>)}
          </Select>
          <Input
            placeholder="Search segments…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="w-48 h-8"
          />
        </div>
        <SegmentList segments={segments.data ?? []} loading={segments.isLoading} />
      </section>
    </div>
  );
}
