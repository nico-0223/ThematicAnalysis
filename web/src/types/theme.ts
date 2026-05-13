export type CandidateThemeStatus = "candidate" | "flagged" | "renamed" | "rejected" | "merged" | "split";

export interface CandidateTheme {
  id: string;
  run_id: string;
  name: string;
  description?: string;
  status: CandidateThemeStatus;
  supporting_code_ids?: string[];
  supporting_segment_ids?: string[];
  representative_quotes?: string[];
  review_rationale?: string;
}
