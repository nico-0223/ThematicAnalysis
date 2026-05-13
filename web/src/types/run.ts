export type RunStatus = "draft" | "running" | "completed" | "failed" | "cancelled";

export interface AnalysisRun {
  id: string;
  name: string;
  codebook_id?: string;
  codebook_version?: string;
  run_type?: string;
  status: RunStatus;
  configuration?: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
  annotation_count?: number;
  candidate_theme_count?: number;
  memo_count?: number;
  export_status?: string;
}
