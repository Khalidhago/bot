"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Paperclip, Loader2, ChevronDown } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { SPECIALIST_MODES, type SpecialistMode } from "@/types";
import { openChatStream } from "@/lib/websocket";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
  sources?: { title: string; relevance_score?: number }[];
}

interface ChatInterfaceProps {
  token: string;
  conversationId?: string;
  initialMessages?: Message[];
  onConversationCreated?: (id: string) => void;
}

export function ChatInterface({
  token,
  conversationId,
  initialMessages = [],
  onConversationCreated,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<SpecialistMode>("general");
  const [streaming, setStreaming] = useState(false);
  const [showModeMenu, setShowModeMenu] = useState(false);
  const [activeConversationId, setActiveConversationId] = useState(conversationId);
  const bottomRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = () => {
    const text = input.trim();
    if (!text || streaming) return;

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
    };
    const assistantId = crypto.randomUUID();
    const assistantMsg: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      streaming: true,
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setInput("");
    setStreaming(true);

    let accumulated = "";

    wsRef.current = openChatStream({
      token,
      message: text,
      mode,
      conversationId: activeConversationId,
      onToken: (t) => {
        accumulated += t;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: accumulated } : m
          )
        );
      },
      onSources: (sources) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, sources: sources as Message["sources"] }
              : m
          )
        );
      },
      onDone: (convId) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, streaming: false } : m
          )
        );
        setStreaming(false);
        if (convId && !activeConversationId) {
          setActiveConversationId(convId);
          onConversationCreated?.(convId);
        }
      },
      onError: (err) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: `Error: ${err}`, streaming: false }
              : m
          )
        );
        setStreaming(false);
      },
    });
  };

  return (
    <div className="flex flex-col h-full bg-hago-dark">
      {/* Mode selector */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-hago-border bg-hago-panel">
        <span className="text-xs text-hago-text/50 uppercase tracking-wider">Mode</span>
        <div className="relative">
          <button
            onClick={() => setShowModeMenu((p) => !p)}
            className="flex items-center gap-2 bg-hago-dark border border-hago-border rounded-lg px-3 py-1.5 text-sm text-hago-text hover:border-hago-blue transition"
          >
            <span className="text-hago-accent">●</span>
            {SPECIALIST_MODES[mode]}
            <ChevronDown className="w-3 h-3 opacity-60" />
          </button>
          {showModeMenu && (
            <div className="absolute top-full left-0 mt-1 w-64 bg-hago-panel border border-hago-border rounded-xl shadow-xl z-50">
              {(Object.keys(SPECIALIST_MODES) as SpecialistMode[]).map((m) => (
                <button
                  key={m}
                  onClick={() => {
                    setMode(m);
                    setShowModeMenu(false);
                  }}
                  className={cn(
                    "w-full text-left px-4 py-2.5 text-sm hover:bg-hago-border/30 transition first:rounded-t-xl last:rounded-b-xl",
                    mode === m ? "text-hago-accent" : "text-hago-text"
                  )}
                >
                  {SPECIALIST_MODES[m]}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {messages.length === 0 && (
          <WelcomeMessage mode={mode} onPromptClick={(p) => setInput(p)} />
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-hago-border bg-hago-panel px-4 py-4">
        <div className="flex items-end gap-3 max-w-4xl mx-auto">
          <div className="flex-1 bg-hago-dark border border-hago-border rounded-xl overflow-hidden focus-within:border-hago-blue transition">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder={`Ask a ${SPECIALIST_MODES[mode]} question… (Shift+Enter for new line)`}
              rows={3}
              className="w-full bg-transparent text-hago-text placeholder-hago-text/30 px-4 py-3 resize-none focus:outline-none text-sm"
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!input.trim() || streaming}
            className="bg-hago-blue hover:bg-hago-blue-light text-white rounded-xl p-3 transition disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
          >
            {streaming ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
        <p className="text-center text-xs text-hago-text/30 mt-2">
          HAGO UAS Bot may make mistakes. Always verify critical engineering decisions.
        </p>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex gap-3 max-w-4xl mx-auto", isUser && "flex-row-reverse")}>
      {/* Avatar */}
      <div
        className={cn(
          "w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 mt-1",
          isUser
            ? "bg-hago-blue text-white"
            : "bg-hago-accent/20 text-hago-accent border border-hago-accent/30"
        )}
      >
        {isUser ? "U" : "H"}
      </div>

      {/* Content */}
      <div className={cn("flex-1", isUser && "flex flex-col items-end")}>
        <div
          className={cn(
            "rounded-xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "bg-hago-blue/20 border border-hago-blue/30 text-white max-w-2xl"
              : "bg-hago-panel border border-hago-border text-hago-text w-full"
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <MarkdownContent content={message.content} streaming={message.streaming} />
          )}
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {message.sources.map((src, i) => (
              <span
                key={i}
                className="text-xs bg-hago-border/30 border border-hago-border rounded-full px-2 py-0.5 text-hago-text/60"
              >
                📄 {src.title}
                {src.relevance_score !== undefined && (
                  <span className="ml-1 text-hago-accent/60">
                    {(src.relevance_score * 100).toFixed(0)}%
                  </span>
                )}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MarkdownContent({
  content,
  streaming,
}: {
  content: string;
  streaming?: boolean;
}) {
  return (
    <div className="prose prose-invert prose-sm max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className ?? "");
            const isBlock = match !== null;
            const lang = match?.[1] ?? "";

            if (isBlock) {
              if (lang === "mermaid") {
                return <MermaidBlock code={String(children).trim()} />;
              }
              return (
                <SyntaxHighlighter
                  style={vscDarkPlus}
                  language={lang}
                  PreTag="div"
                  className="rounded-lg text-xs"
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              );
            }
            return (
              <code
                className="bg-hago-dark border border-hago-border rounded px-1 py-0.5 text-hago-accent text-xs font-mono"
                {...props}
              >
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
      {streaming && (
        <span className="inline-block w-2 h-4 bg-hago-accent animate-pulse ml-0.5 align-middle" />
      )}
    </div>
  );
}

function MermaidBlock({ code }: { code: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    import("mermaid").then((mod) => {
      if (cancelled || !ref.current) return;
      const mermaid = mod.default;
      mermaid.initialize({ startOnLoad: false, theme: "dark" });
      const id = `mermaid-${Math.random().toString(36).slice(2)}`;
      mermaid
        .render(id, code)
        .then(({ svg }) => {
          if (!cancelled && ref.current) {
            ref.current.innerHTML = svg;
          }
        })
        .catch(() => {
          if (!cancelled && ref.current) {
            ref.current.innerHTML = `<pre class="text-xs text-red-400">Diagram render error</pre>`;
          }
        });
    });
    return () => {
      cancelled = true;
    };
  }, [code]);

  return <div ref={ref} className="my-4 flex justify-center" />;
}

const WELCOME_PROMPTS: Record<SpecialistMode, string[]> = {
  general: [
    "What are the main differences between PX4 and ArduPilot?",
    "How do I design a VTOL UAV power system?",
    "Explain MAVLink communication architecture",
  ],
  px4: [
    "How do I configure EKF2_AID_MASK in PX4?",
    "Explain the PX4 uORB messaging system",
    "How do I set up PX4 SITL with Gazebo?",
  ],
  ardupilot: [
    "How do I tune ArduCopter PID gains?",
    "Explain ArduPilot DataFlash log analysis",
    "How do I configure ArduPilot SITL?",
  ],
  ros2: [
    "How do I bridge PX4 to ROS 2 using Micro XRCE-DDS?",
    "Explain TF2 coordinate frames for a drone",
    "How do I set up Nav2 for autonomous flight?",
  ],
  ai_ml: [
    "How do I deploy YOLOv8 on NVIDIA Jetson for UAV object detection?",
    "Explain the AI inference pipeline for a drone",
    "How do I integrate computer vision with ROS 2?",
  ],
  flight_log_analyst: [
    "How do I interpret EKF innovation flags in a PX4 log?",
    "What causes GPS position jumps in a flight log?",
    "How do I analyze motor output imbalance?",
  ],
  system_architect: [
    "Design a complete companion computer architecture for a delivery drone",
    "What communication protocols should I use for a swarm drone system?",
    "Design a redundant power system for a heavy-lift UAV",
  ],
  hardware_integration: [
    "How do I integrate a lidar sensor with PX4?",
    "What is the wiring for a CAN-based ESC with a Pixhawk?",
    "How do I set up an optical flow sensor for indoor flight?",
  ],
};

function WelcomeMessage({
  mode,
  onPromptClick,
}: {
  mode: SpecialistMode;
  onPromptClick: (prompt: string) => void;
}) {
  const prompts = WELCOME_PROMPTS[mode] ?? WELCOME_PROMPTS.general;
  return (
    <div className="flex flex-col items-center justify-center h-full py-16 px-4">
      <div className="text-4xl mb-4">🚁</div>
      <h2 className="text-2xl font-bold text-white mb-2">HAGO UAS Intelligence Bot</h2>
      <p className="text-hago-text/60 text-sm text-center max-w-md mb-8">
        {SPECIALIST_MODES[mode]} mode active. Ask any UAV/UAS engineering question.
      </p>
      <div className="grid gap-3 w-full max-w-lg">
        {prompts.map((prompt, i) => (
          <button
            key={i}
            onClick={() => onPromptClick(prompt)}
            className="text-left bg-hago-panel border border-hago-border rounded-xl px-4 py-3 text-sm text-hago-text hover:border-hago-blue hover:text-white transition"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
}
