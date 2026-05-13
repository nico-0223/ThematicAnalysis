export type PhaseStatus = "not_started" | "in_progress" | "completed";

export interface Phase {
  id?: string;
  run_id?: string;
  number: 1 | 2 | 3 | 4 | 5 | 6;
  name: string;
  description: string;
  status: PhaseStatus;
  notes?: string;
  started_at?: string;
  completed_at?: string;
}

export const BRAUN_CLARKE_PHASES: Pick<Phase, "number" | "name" | "description">[] = [
  { number: 1, name: "Familiarisation with the data", description: "Reading and re-reading data; noting initial ideas." },
  { number: 2, name: "Generating initial codes", description: "Coding interesting features systematically across the data set." },
  { number: 3, name: "Searching for themes", description: "Collating codes into potential candidate themes." },
  { number: 4, name: "Reviewing themes", description: "Checking themes against coded extracts and the entire data set." },
  { number: 5, name: "Defining and naming themes", description: "Refining the specifics of each theme; generating clear definitions and names." },
  { number: 6, name: "Producing the report", description: "Final analysis, selection of extracts, relating analysis to research question." },
];
