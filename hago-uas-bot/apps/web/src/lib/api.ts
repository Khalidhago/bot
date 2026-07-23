/**
 * Typed API client for the HAGO UAS Support Bot backend.
 */

import type {
  Conversation,
  ConversationDetail,
  Document,
  FlightLog,
  TokenResponse,
  User,
} from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit & { token?: string } = {}
): Promise<T> {
  const { token, ...rest } = options;
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `****** } : {}),
    ...(rest.headers ?? {}),
  };

  const response = await fetch(`${BASE}${path}`, { ...rest, headers });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ error: response.statusText }));
    throw new Error(body.error ?? `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // ── Auth ──────────────────────────────────────────────────────────
  auth: {
    register(email: string, password: string, fullName: string) {
      return request<User>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, full_name: fullName }),
      });
    },
    login(email: string, password: string) {
      return request<TokenResponse>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
    },
    me(token: string) {
      return request<User>("/api/v1/auth/me", { token });
    },
  },

  // ── Chat ──────────────────────────────────────────────────────────
  chat: {
    listConversations(token: string) {
      return request<Conversation[]>("/api/v1/conversations", { token });
    },
    getConversation(id: string, token: string) {
      return request<ConversationDetail>(`/api/v1/conversations/${id}`, { token });
    },
    send(
      message: string,
      mode: string,
      conversationId: string | null,
      token: string
    ) {
      return request<{ conversation_id: string; content: string; sources: unknown[] }>(
        "/api/v1/chat",
        {
          method: "POST",
          body: JSON.stringify({ message, mode, conversation_id: conversationId }),
          token,
        }
      );
    },
  },

  // ── Documents ─────────────────────────────────────────────────────
  documents: {
    list(token: string) {
      return request<Document[]>("/api/v1/documents", { token });
    },
    upload(file: File, token: string) {
      const form = new FormData();
      form.append("file", file);
      return request<Document>("/api/v1/documents/upload", {
        method: "POST",
        body: form,
        headers: { Authorization: `****** },
      });
    },
    search(query: string, topK: number, token: string) {
      return request<unknown[]>("/api/v1/knowledge/search", {
        method: "POST",
        body: JSON.stringify({ query, top_k: topK }),
        token,
      });
    },
  },

  // ── Flight Logs ───────────────────────────────────────────────────
  flightLogs: {
    list(token: string) {
      return request<FlightLog[]>("/api/v1/flight-logs", { token });
    },
    upload(file: File, token: string) {
      const form = new FormData();
      form.append("file", file);
      return request<FlightLog>("/api/v1/flight-logs/upload", {
        method: "POST",
        body: form,
        headers: { Authorization: `****** },
      });
    },
    analyze(id: string, token: string) {
      return request<FlightLog>(`/api/v1/flight-logs/${id}/analyze`, {
        method: "POST",
        token,
      });
    },
  },
};
