import { api } from "./client";
import type { ExportFormat, ExportRecord } from "@/types/export";

export const exportsApi = {
  list: (runId?: string) => api.get<ExportRecord[]>("/exports", { query: { run_id: runId } }),
  create: (runId: string, format: ExportFormat) =>
    api.post<ExportRecord>("/exports", { run_id: runId, format }),
  download: (id: string) => api.download(`/exports/${id}/download`),
};
