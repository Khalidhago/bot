"use client";

import { useEffect, useRef, useState } from "react";
import { Upload, Activity, ChevronDown, ChevronRight, AlertTriangle, Info } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";
import type { AnomalyFinding, FlightLog } from "@/types";
import { cn, formatDate, severityColor } from "@/lib/utils";

export default function FlightLogsPage() {
  const { accessToken } = useAuthStore();
  const [logs, setLogs] = useState<FlightLog[]>([]);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const load = async () => {
    if (!accessToken) return;
    const data = await api.flightLogs.list(accessToken).catch(() => []);
    setLogs(data);
  };

  useEffect(() => {
    load();
  }, [accessToken]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !accessToken) return;
    setUploading(true);
    setError(null);
    try {
      await api.flightLogs.upload(file, accessToken);
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleAnalyze = async (logId: string) => {
    if (!accessToken) return;
    setAnalyzing(logId);
    try {
      await api.flightLogs.analyze(logId, accessToken);
      await load();
      setExpanded(logId);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setAnalyzing(null);
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">Flight Log Analysis</h1>
            <p className="text-hago-text/50 text-sm mt-1">
              Upload PX4 ULog, ArduPilot DataFlash, CSV, or JSON telemetry for AI diagnosis
            </p>
          </div>
          <label className="cursor-pointer">
            <input
              ref={fileRef}
              type="file"
              className="hidden"
              accept=".ulg,.ulog,.bin,.log,.csv,.json"
              onChange={handleUpload}
            />
            <span className="flex items-center gap-2 bg-hago-blue hover:bg-hago-blue-light text-white px-4 py-2 rounded-lg text-sm font-medium transition">
              <Upload className="w-4 h-4" />
              Upload Log
            </span>
          </label>
        </div>

        {error && (
          <div className="mb-4 bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-3">
          {logs.length === 0 && (
            <div className="bg-hago-panel border border-hago-border rounded-xl p-12 text-center">
              <Activity className="w-12 h-12 text-hago-text/20 mx-auto mb-3" />
              <p className="text-hago-text/40 text-sm">No flight logs yet</p>
              <p className="text-hago-text/30 text-xs mt-1">
                Supported: .ulg, .bin, .log, .csv, .json
              </p>
            </div>
          )}

          {logs.map((log) => (
            <div
              key={log.id}
              className="bg-hago-panel border border-hago-border rounded-xl overflow-hidden"
            >
              <div className="flex items-center gap-4 px-5 py-4">
                <Activity className="w-5 h-5 text-hago-text/40 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{log.filename}</p>
                  <p className="text-xs text-hago-text/40 mt-0.5">
                    {log.log_type.toUpperCase()} · {formatDate(log.created_at)}
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  {log.status === "ready" && log.analysis_result && (
                    <span
                      className={cn(
                        "text-xs px-2 py-0.5 rounded-full border",
                        severityBadge(log.analysis_result.overall_severity)
                      )}
                    >
                      {log.analysis_result.overall_severity.toUpperCase()}
                    </span>
                  )}

                  {log.status !== "ready" && (
                    <button
                      onClick={() => handleAnalyze(log.id)}
                      disabled={analyzing === log.id}
                      className="text-xs bg-hago-blue/20 border border-hago-blue/30 text-hago-accent px-3 py-1 rounded-lg hover:bg-hago-blue/30 transition disabled:opacity-50"
                    >
                      {analyzing === log.id ? "Analyzing…" : "Analyze"}
                    </button>
                  )}

                  {log.status === "ready" && (
                    <button
                      onClick={() => setExpanded((p) => (p === log.id ? null : log.id))}
                      className="text-hago-text/40 hover:text-white transition"
                    >
                      {expanded === log.id ? (
                        <ChevronDown className="w-4 h-4" />
                      ) : (
                        <ChevronRight className="w-4 h-4" />
                      )}
                    </button>
                  )}
                </div>
              </div>

              {expanded === log.id && log.analysis_result && (
                <AnalysisResult result={log.analysis_result} />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AnalysisResult({
  result,
}: {
  result: NonNullable<FlightLog["analysis_result"]>;
}) {
  return (
    <div className="border-t border-hago-border px-5 py-4 space-y-4">
      <p className="text-sm text-hago-text/80">{result.summary}</p>

      {result.findings.length === 0 ? (
        <div className="flex items-center gap-2 text-green-400 text-sm">
          <Info className="w-4 h-4" />
          No anomalies detected
        </div>
      ) : (
        <div className="space-y-3">
          {result.findings.map((f, i) => (
            <FindingCard key={i} finding={f} />
          ))}
        </div>
      )}
    </div>
  );
}

function FindingCard({ finding }: { finding: AnomalyFinding }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="bg-hago-dark border border-hago-border rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-hago-border/10 transition"
        onClick={() => setOpen((p) => !p)}
      >
        <AlertTriangle className={cn("w-4 h-4 shrink-0", severityColor(finding.severity))} />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-white">{finding.problem}</p>
          <p className="text-xs text-hago-text/50">
            {finding.category} · {finding.severity} · {finding.confidence}
          </p>
        </div>
        {open ? (
          <ChevronDown className="w-4 h-4 text-hago-text/40" />
        ) : (
          <ChevronRight className="w-4 h-4 text-hago-text/40" />
        )}
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-2 text-sm">
          <Row label="Evidence" value={finding.evidence} />
          <Row label="Probable Cause" value={finding.probable_cause} />
          <Row label="Investigation" value={finding.recommended_investigation} />
          <Row label="Corrective Action" value={finding.corrective_action} />
        </div>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-hago-text/40 uppercase tracking-wide">{label}</p>
      <p className="text-hago-text/80 text-sm">{value}</p>
    </div>
  );
}

function severityBadge(severity: string): string {
  switch (severity) {
    case "critical":
      return "bg-red-500/10 border-red-500/30 text-red-400";
    case "high":
      return "bg-orange-500/10 border-orange-500/30 text-orange-400";
    case "medium":
      return "bg-yellow-500/10 border-yellow-500/30 text-yellow-400";
    default:
      return "bg-green-500/10 border-green-500/30 text-green-400";
  }
}
