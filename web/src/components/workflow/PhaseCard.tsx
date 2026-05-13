import { Phase } from "@/types/phase";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/lib/utils";

interface Props {
  phase: Phase;
  onUpdate?: (phaseNumber: number, status: Phase["status"]) => void;
  onAddMemo?: (phaseNumber: number) => void;
}

export function PhaseCard({ phase, onUpdate, onAddMemo }: Props) {
  return (
    <Card>
      <CardHeader className="flex-row items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Phase {phase.number}</span>
            <StatusBadge status={phase.status} />
          </div>
          <p className="text-sm font-semibold mt-1">{phase.name}</p>
          <p className="text-xs text-muted-foreground mt-1 max-w-2xl">{phase.description}</p>
        </div>
        <div className="flex gap-2">
          {onUpdate && (
            <>
              <Button size="sm" variant="outline" onClick={() => onUpdate(phase.number, "in_progress")}>
                Mark in progress
              </Button>
              <Button size="sm" onClick={() => onUpdate(phase.number, "completed")}>
                Mark completed
              </Button>
            </>
          )}
          {onAddMemo && (
            <Button size="sm" variant="ghost" onClick={() => onAddMemo(phase.number)}>
              Add memo
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="grid gap-2 text-xs text-muted-foreground sm:grid-cols-2">
        <div>Started: {formatDate(phase.started_at)}</div>
        <div>Completed: {formatDate(phase.completed_at)}</div>
        {phase.notes && <div className="sm:col-span-2 text-foreground">{phase.notes}</div>}
      </CardContent>
    </Card>
  );
}
