import { api } from "./client";
import type { Annotation } from "@/types/annotation";

export interface AnnotationFilters {
  conversation_id?: string;
  speaker?: string;
  code_id?: string;
  low_confidence?: boolean;
  uncoded?: boolean;
}

export const annotationsApi = {
  listForRun: (runId: string, filters?: AnnotationFilters) =>
    api.get<Annotation[]>(`/runs/${runId}/annotations`, { query: filters as any }),
  upsert: (runId: string, body: Partial<Annotation>) =>
    api.post<Annotation>(`/runs/${runId}/annotations`, body),
  remove: (runId: string, id: string) => api.del<void>(`/runs/${runId}/annotations/${id}`),
  suggestions: (runId: string, segmentId: string) =>
    api.get<Annotation[]>(`/runs/${runId}/segments/${segmentId}/suggestions`),
};
