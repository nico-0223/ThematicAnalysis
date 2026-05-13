import { api } from "./client";
import type { Conversation, Segment, Turn } from "@/types/conversation";

export const conversationsApi = {
  list: () => api.get<Conversation[]>("/conversations"),
  get: (id: string) => api.get<Conversation>(`/conversations/${id}`),
  turns: (id: string) => api.get<Turn[]>(`/conversations/${id}/turns`),
  segments: (id: string, query?: { speaker?: string; q?: string }) =>
    api.get<Segment[]>(`/conversations/${id}/segments`, { query }),
  upload: (file: File) => api.upload<{ imported: number; conversation_ids: string[] }>("/conversations/import", file),
};
