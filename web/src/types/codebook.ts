export interface CodebookSummary {
  id: string;
  name: string;
  version: string;
  framework?: string;
  themes_count?: number;
  codes_count?: number;
  updated_at?: string;
}

export interface Codebook extends CodebookSummary {
  metadata?: Record<string, unknown>;
  framework_settings?: Record<string, unknown>;
  themes?: Theme[];
  memo_prompts?: string[];
}

export interface Theme {
  id: string;
  name: string;
  description?: string;
  codes?: Code[];
}

export interface Code {
  id: string;
  name: string;
  description?: string;
  indicators?: string[];
  inclusion_criteria?: string[];
  exclusion_criteria?: string[];
  examples?: string[];
  counterexamples?: string[];
  features?: Feature[];
  subcodes?: Code[];
}

export interface Feature {
  id?: string;
  name: string;
  type?: string;
  pattern?: string;
}
