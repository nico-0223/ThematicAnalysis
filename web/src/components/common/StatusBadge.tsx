import { Badge } from "@/components/ui/Badge";

type Status = string | undefined | null;

const map: Record<string, "default" | "success" | "warning" | "danger" | "info" | "muted"> = {
  draft: "muted",
  not_started: "muted",
  pending: "muted",
  in_progress: "info",
  running: "info",
  completed: "success",
  ready: "success",
  failed: "danger",
  cancelled: "warning",
  flagged: "warning",
  rejected: "danger",
  candidate: "info",
};

export function StatusBadge({ status }: { status: Status }) {
  const tone = (status && map[status]) || "default";
  return <Badge tone={tone}>{status ? status.replace(/_/g, " ") : "unknown"}</Badge>;
}
