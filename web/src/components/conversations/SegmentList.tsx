import { Segment } from "@/types/conversation";
import { LoadingState } from "@/components/common/LoadingState";

export function SegmentList({ segments, loading }: { segments: Segment[]; loading?: boolean }) {
  if (loading) return <LoadingState />;
  if (!segments.length) return <p className="text-xs text-muted-foreground">No segments match.</p>;
  return (
    <div className="rounded-lg border border-border bg-card divide-y divide-border max-h-[600px] overflow-y-auto">
      {segments.map((s) => (
        <div key={s.id} className="p-3 text-sm">
          <p className="text-xs text-muted-foreground">#{s.index} &middot; {s.speaker || "—"}</p>
          <p className="mt-0.5 whitespace-pre-wrap">{s.text}</p>
        </div>
      ))}
    </div>
  );
}
