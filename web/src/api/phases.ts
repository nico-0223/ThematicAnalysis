import { api } from "./client";
import type { Phase, PhaseStatus } from "@/types/phase";

export const phasesApi = {
  listForRun: (runId: string) => api.get<Phase[]>(`/runs/${runId}/phases`),
  update: (runId: string, phaseNumber: number, body: { status?: PhaseStatus; notes?: string }) =>
    api.patch<Phase>(`/runs/${runId}/phases/${phaseNumber}`, body),
};
