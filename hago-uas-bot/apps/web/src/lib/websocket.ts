/**
 * WebSocket client for streaming AI responses.
 */

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

export interface StreamOptions {
  token: string;
  message: string;
  mode: string;
  conversationId?: string;
  onToken: (token: string) => void;
  onSources: (sources: unknown[]) => void;
  onDone: (conversationId?: string) => void;
  onError: (error: string) => void;
}

export function openChatStream({
  token,
  message,
  mode,
  conversationId,
  onToken,
  onSources,
  onDone,
  onError,
}: StreamOptions): WebSocket {
  const ws = new WebSocket(`${WS_BASE}/api/v1/ws/chat`);

  ws.onopen = () => {
    ws.send(
      JSON.stringify({ token, message, mode, conversation_id: conversationId ?? null })
    );
  };

  ws.onmessage = (event) => {
    try {
      const chunk = JSON.parse(event.data as string) as {
        type: string;
        data?: unknown;
        conversation_id?: string;
      };
      if (chunk.type === "token") {
        onToken(chunk.data as string);
      } else if (chunk.type === "sources") {
        onSources(chunk.data as unknown[]);
      } else if (chunk.type === "done") {
        onDone(chunk.conversation_id);
        ws.close();
      } else if (chunk.type === "error") {
        onError(chunk.data as string);
        ws.close();
      }
    } catch {
      onError("Failed to parse server message.");
    }
  };

  ws.onerror = () => {
    onError("WebSocket connection error.");
  };

  return ws;
}
