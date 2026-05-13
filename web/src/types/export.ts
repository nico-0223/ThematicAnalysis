export type ExportFormat = "markdown" | "html" | "json" | "csv";

export interface ExportRecord {
  id: string;
  run_id: string;
  format: ExportFormat;
  status: "pending" | "ready" | "failed";
  file_url?: string;
  created_at?: string;
}
