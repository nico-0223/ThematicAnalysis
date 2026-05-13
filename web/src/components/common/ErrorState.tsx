import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { env } from "@/lib/env";

interface Props {
  title?: string;
  message?: string;
  onRetry?: () => void;
  showApiUrl?: boolean;
}

export function ErrorState({ title = "Backend unavailable", message, onRetry, showApiUrl = true }: Props) {
  return (
    <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-6">
      <div className="flex items-start gap-3">
        <AlertTriangle className="h-5 w-5 text-destructive mt-0.5" />
        <div className="flex-1">
          <p className="text-sm font-semibold text-destructive">{title}</p>
          {message && <p className="mt-1 text-xs text-muted-foreground">{message}</p>}
          {showApiUrl && (
            <p className="mt-2 text-xs text-muted-foreground">
              Configured API base URL: <code className="rounded bg-muted px-1 py-0.5">{env.apiBaseUrl}</code>
            </p>
          )}
          <p className="mt-2 text-xs text-muted-foreground">
            Make sure the backend is running and reachable from this origin (CORS).
          </p>
          {onRetry && (
            <div className="mt-3">
              <Button size="sm" variant="outline" onClick={onRetry}>
                Retry
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
