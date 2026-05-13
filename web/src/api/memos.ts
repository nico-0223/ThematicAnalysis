import { api } from "./client";
import type { Memo } from "@/types/memo";

export interface MemoFilters {
  type?: string;
  phase_number?: number;
  q?: string;
  link_type?: string;
  link_id?: string;
}

export const memosApi = {
  list: (filters?: MemoFilters) => api.get<Memo[]>("/memos", { query: filters as any }),
  create: (body: Partial<Memo>) => api.post<Memo>("/memos", body),
  update: (id: string, body: Partial<Memo>) => api.put<Memo>(`/memos/${id}`, body),
  remove: (id: string) => api.del<void>(`/memos/${id}`),
};
