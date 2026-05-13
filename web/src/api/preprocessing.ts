import { api } from "./client";

export type SegmentationStrategy = "turn" | "sentence" | "fixed_size" | "custom_placeholder";

export interface PreprocessingRequest {
  strategy: SegmentationStrategy;
  cleaning?: { lowercase?: boolean; strip_urls?: boolean; collapse_whitespace?: boolean };
  conversation_id?: string;
  fixed_size?: number;
}

export interface PreprocessingResult {
  job_id?: string;
  segments_created?: number;
  conversations_processed?: number;
  preview?: { conversation_id: string; segment_id: string; text: string }[];
}

export const preprocessingApi = {
  run: (body: PreprocessingRequest) => api.post<PreprocessingResult>("/preprocessing", body),
};
