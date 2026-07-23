/**
 * Shared TypeScript types for API communication.
 */

export type UserRole = "admin" | "engineer" | "operator" | "viewer";

export type SpecialistMode =
  | "general"
  | "px4"
  | "ardupilot"
  | "ros2"
  | "ai_ml"
  | "flight_log_analyst"
  | "system_architect"
  | "hardware_integration";

export const SPECIALIST_MODES: Record<SpecialistMode, string> = {
  general: "General UAV Engineer",
  px4: "PX4 Specialist",
  ardupilot: "ArduPilot Specialist",
  ros2: "ROS 2 Engineer",
  ai_ml: "AI/ML Engineer",
  flight_log_analyst: "Flight Log Analyst",
  system_architect: "System Architect",
  hardware_integration: "Hardware Integration Engineer",
};

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface SourceReference {
  document_id?: string;
  title: string;
  chunk_index?: number;
  relevance_score?: number;
  source_type?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: SourceReference[];
  tokens_used?: number;
  model_used?: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  mode: SpecialistMode;
  message_count: number;
  updated_at: string;
}

export interface ConversationDetail {
  id: string;
  title: string;
  mode: SpecialistMode;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  filename: string;
  mime_type: string;
  status: "pending" | "processing" | "ready" | "failed";
  chunk_count: number;
  ingested_at?: string;
  created_at: string;
}

export interface AnomalyFinding {
  category: string;
  problem: string;
  evidence: string;
  probable_cause: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  confidence: "confirmed" | "high" | "medium" | "low" | "insufficient_data";
  recommended_investigation: string;
  corrective_action: string;
}

export interface FlightLog {
  id: string;
  filename: string;
  log_type: string;
  status: "pending" | "processing" | "ready" | "failed";
  analysis_result?: {
    summary: string;
    findings: AnomalyFinding[];
    overall_severity: string;
    analyzed_at: string;
  };
  created_at: string;
  analyzed_at?: string;
}

export interface StreamChunk {
  type: "token" | "sources" | "done" | "error";
  data?: string | SourceReference[];
  conversation_id?: string;
}

export interface ApiError {
  error: string;
  type: string;
}
