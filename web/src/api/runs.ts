import { api } from "./client";
import type { AnalysisRun } from "@/types/run";

export interface CreateRunBody {
  name: string;
  codebook_id: string;
  codebook_version?: string;
  run_type?: string;
  configuration?: Record<string, unknown>;
}

export const runsApi = {
  list: () => api.get<AnalysisRun[]>("/runs"),
  get: (id: string) => api.get<AnalysisRun>(`/runs/${id}`),
  create: (body: CreateRunBody) => api.post<AnalysisRun>("/runs", body),
  start: (id: string) => api.post<AnalysisRun>(`/runs/${id}/start`),
  cancel: (id: string) => api.post<AnalysisRun>(`/runs/${id}/cancel`),
};
