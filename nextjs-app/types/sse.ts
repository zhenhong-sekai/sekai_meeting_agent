export interface SSEEvent {
  event: string;
  data: any;
}

export interface StartEvent {
  message: string;
  query: string;
  timestamp: number;
}

export interface NodeUpdateEvent {
  node: string;
  payload: any;
  timestamp: number;
}

export interface CompletionEvent {
  message: string;
  final_summary?: string;
  total_steps: number;
  timestamp: number;
}

export interface ErrorEvent {
  error: string;
  timestamp: number;
}

export interface TestEvent {
  message: string;
  timestamp: number;
}
