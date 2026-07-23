"use client";

import { useEffect, useState, useRef } from "react";
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";
import type { Document } from "@/types";
import { formatDate } from "@/lib/utils";

const STATUS_ICONS: Record<string, React.ReactNode> = {
  ready: <CheckCircle className="w-4 h-4 text-green-400" />,
  processing: <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />,
  failed: <AlertCircle className="w-4 h-4 text-red-400" />,
  pending: <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />,
};

export default function DocumentsPage() {
  const { accessToken } = useAuthStore();
  const [docs, setDocs] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const load = async () => {
    if (!accessToken) return;
    const data = await api.documents.list(accessToken).catch(() => []);
    setDocs(data);
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
      await api.documents.upload(file, accessToken);
      await load();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white">Knowledge Base</h1>
            <p className="text-hago-text/50 text-sm mt-1">
              Upload technical documents to ground AI answers with verified sources
            </p>
          </div>
          <label className="cursor-pointer">
            <input
              ref={fileRef}
              type="file"
              className="hidden"
              accept=".pdf,.docx,.txt,.md"
              onChange={handleUpload}
              disabled={uploading}
            />
            <span className="flex items-center gap-2 bg-hago-blue hover:bg-hago-blue-light text-white px-4 py-2 rounded-lg text-sm font-medium transition">
              {uploading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Upload className="w-4 h-4" />
              )}
              Upload Document
            </span>
          </label>
        </div>

        {error && (
          <div className="mb-4 bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="bg-hago-panel border border-hago-border rounded-xl divide-y divide-hago-border">
          {docs.length === 0 ? (
            <div className="p-12 text-center">
              <FileText className="w-12 h-12 text-hago-text/20 mx-auto mb-3" />
              <p className="text-hago-text/40 text-sm">No documents yet</p>
              <p className="text-hago-text/30 text-xs mt-1">
                Upload PDFs, DOCX, or text files to enable RAG-grounded answers
              </p>
            </div>
          ) : (
            docs.map((doc) => (
              <div key={doc.id} className="flex items-center gap-4 px-5 py-4">
                <FileText className="w-5 h-5 text-hago-text/40 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{doc.filename}</p>
                  <p className="text-xs text-hago-text/40 mt-0.5">
                    {doc.chunk_count} chunks · {doc.mime_type} · {formatDate(doc.created_at)}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {STATUS_ICONS[doc.status] ?? null}
                  <span className="text-xs text-hago-text/50 capitalize">{doc.status}</span>
                </div>
              </div>
            ))
          )}
        </div>

        <p className="text-xs text-hago-text/30 mt-4 text-center">
          Supported formats: PDF, DOCX, TXT, Markdown · Max 50 MB
        </p>
      </div>
    </div>
  );
}
