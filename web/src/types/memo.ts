export type MemoType = "analytic" | "reflexive" | "method" | "phase" | "general";
export type MemoLinkType = "run" | "phase" | "conversation" | "segment" | "code" | "theme";

export interface Memo {
  id: string;
  type: MemoType;
  title?: string;
  body: string;
  link_type?: MemoLinkType;
  link_id?: string;
  phase_number?: number;
  created_at?: string;
  updated_at?: string;
}
