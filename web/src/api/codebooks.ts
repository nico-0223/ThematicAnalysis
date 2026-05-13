import { api } from "./client";
import type { Codebook, CodebookSummary } from "@/types/codebook";

export const codebooksApi = {
  list: () => api.get<CodebookSummary[]>("/codebooks"),
  get: (id: string) => api.get<Codebook>(`/codebooks/${id}`),
  upload: (file: File) => api.upload<Codebook>("/codebooks/upload", file),
  validate: (file: File) => api.upload<{ valid: boolean; errors?: string[] }>("/codebooks/validate", file),
  update: (id: string, body: Partial<Codebook>) => api.put<Codebook>(`/codebooks/${id}`, body),
  versions: (id: string) => api.get<{ version: string; created_at: string }[]>(`/codebooks/${id}/versions`),
};
