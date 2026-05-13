import { Phase, BRAUN_CLARKE_PHASES } from "@/types/phase";
import { PhaseCard } from "./PhaseCard";

interface Props {
  phases?: Phase[];
  onUpdate?: (phaseNumber: number, status: Phase["status"]) => void;
  onAddMemo?: (phaseNumber: number) => void;
}

export function PhaseTimeline({ phases = [], onUpdate, onAddMemo }: Props) {
  const merged = BRAUN_CLARKE_PHASES.map((p) => {
    const existing = phases.find((x) => x.number === p.number);
    return existing ?? { ...p, status: "not_started" as const };
  });
  return (
    <ol className="space-y-3">
      {merged.map((p) => (
        <li key={p.number}>
          <PhaseCard phase={p} onUpdate={onUpdate} onAddMemo={onAddMemo} />
        </li>
      ))}
    </ol>
  );
}
