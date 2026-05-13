export interface Conversation {
  id: string;
  title?: string;
  source?: string;
  speakers?: string[];
  turns_count?: number;
  segments_count?: number;
  imported_at?: string;
}

export interface Turn {
  id: string;
  conversation_id: string;
  index: number;
  speaker?: string;
  text: string;
}

export interface Segment {
  id: string;
  conversation_id: string;
  turn_id?: string;
  index: number;
  text: string;
  speaker?: string;
  start?: number;
  end?: number;
}
