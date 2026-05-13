export type AnnotationSource = "human" | "imported" | "rule_based" | "ai_assisted";

export interface Annotation {
  id: string;
  run_id: string;
  segment_id: string;
  conversation_id?: string;
  code_id: string;
  code_name?: string;
  source: AnnotationSource;
  confidence?: number;
  rationale?: string;
  evidence?: string;
  decision_note?: string;
  created_at?: string;
  updated_at?: string;
}
