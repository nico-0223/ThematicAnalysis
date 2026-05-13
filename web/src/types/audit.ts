export interface AuditEntry {
  id: string;
  timestamp: string;
  run_id?: string;
  phase_number?: number;
  action_type: string;
  description?: string;
  before?: unknown;
  after?: unknown;
  actor?: string;
}
