import { useQuery } from "@tanstack/react-query";
import { ping } from "@/api/client";
import { Badge } from "@/components/ui/Badge";
import { env } from "@/lib/env";

export function Header() {
  const { data: online } = useQuery({
    queryKey: ["ping"],
    queryFn: ping,
    refetchInterval: 15000,
  });
  return (
    <header className="h-14 border-b border-border bg-card flex items-center justify-between px-6">
      <div className="text-sm text-muted-foreground">
        Conversation thematic analysis &middot; researcher interface
      </div>
      <div className="flex items-center gap-3">
        <span className="text-xs text-muted-foreground hidden md:inline">{env.apiBaseUrl}</span>
        <Badge tone={online ? "success" : "danger"}>{online ? "Backend online" : "Backend offline"}</Badge>
      </div>
    </header>
  );
}
