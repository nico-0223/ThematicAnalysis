import { api } from "./client";
import type { AuditEntry } from "@/types/audit";

export interface AuditFilters {
  run_id?: string;
  phase_number?: number;
  action_type?: string;
  from?: string;
  to?: string;
  q?: string;
}

export const auditApi = {
  list: (filters?: AuditFilters) => api.get<AuditEntry[]>("/audit", { query: filters as any }),
};
