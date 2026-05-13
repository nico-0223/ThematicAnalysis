import { api } from "./client";
import type { CandidateTheme, CandidateThemeStatus } from "@/types/theme";

export const themesApi = {
  listCandidates: (runId: string) => api.get<CandidateTheme[]>(`/runs/${runId}/candidate-themes`),
  update: (runId: string, id: string, body: Partial<CandidateTheme> & { status?: CandidateThemeStatus }) =>
    api.patch<CandidateTheme>(`/runs/${runId}/candidate-themes/${id}`, body),
  merge: (runId: string, ids: string[], name: string) =>
    api.post<CandidateTheme>(`/runs/${runId}/candidate-themes/merge`, { ids, name }),
  split: (runId: string, id: string, parts: { name: string; supporting_code_ids?: string[] }[]) =>
    api.post<CandidateTheme[]>(`/runs/${runId}/candidate-themes/${id}/split`, { parts }),
};
