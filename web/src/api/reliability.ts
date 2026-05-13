import { api } from "./client";

export interface ReliabilityResult {
  run_id: string;
  cohens_kappa?: number;
  coders?: string[];
  comparison?: { code_id: string; code_name?: string; agreement: number; disagreements: number }[];
  disagreements?: {
    id: string;
    segment_id: string;
    coder_a: string;
    coder_b: string;
    code_a?: string;
    code_b?: string;
    resolved?: boolean;
    note?: string;
  }[];
}

export const reliabilityApi = {
  compute: (runId: string) => api.post<ReliabilityResult>(`/runs/${runId}/reliability`),
  get: (runId: string) => api.get<ReliabilityResult>(`/runs/${runId}/reliability`),
  resolveDisagreement: (runId: string, id: string, body: { resolved: boolean; note?: string }) =>
    api.patch<void>(`/runs/${runId}/reliability/disagreements/${id}`, body),
};
