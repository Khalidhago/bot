"use client";

import Link from "next/link";
import { MessageSquare, FileText, Activity, Zap } from "lucide-react";
import { useAuthStore } from "@/lib/auth";

const QUICK_LINKS = [
  {
    href: "/chat",
    icon: MessageSquare,
    title: "AI Chat",
    description: "Ask technical UAV/UAS questions with 8 specialist modes",
    color: "text-hago-blue",
    bg: "bg-hago-blue/10 border-hago-blue/20",
  },
  {
    href: "/documents",
    icon: FileText,
    title: "Knowledge Base",
    description: "Upload documents and enable RAG-grounded answers",
    color: "text-hago-accent",
    bg: "bg-hago-accent/10 border-hago-accent/20",
  },
  {
    href: "/flight-logs",
    icon: Activity,
    title: "Flight Log Analyzer",
    description: "Diagnose PX4, ArduPilot, CSV, and JSON telemetry logs",
    color: "text-orange-400",
    bg: "bg-orange-400/10 border-orange-400/20",
  },
];

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-5 h-5 text-hago-accent" />
            <span className="text-hago-accent text-sm font-medium tracking-wider uppercase">
              HAGO UAS Intelligence Bot
            </span>
          </div>
          <h1 className="text-3xl font-bold text-white">
            Welcome{user?.full_name ? `, ${user.full_name}` : ""}
          </h1>
          <p className="text-hago-text/60 mt-1">
            Your AI-powered UAV/UAS engineering workspace is ready.
          </p>
        </div>

        {/* Quick links */}
        <div className="grid md:grid-cols-3 gap-4 mb-8">
          {QUICK_LINKS.map(({ href, icon: Icon, title, description, color, bg }) => (
            <Link
              key={href}
              href={href}
              className={`block p-5 rounded-xl border ${bg} hover:scale-[1.02] transition-transform`}
            >
              <Icon className={`w-6 h-6 ${color} mb-3`} />
              <h3 className="text-white font-semibold mb-1">{title}</h3>
              <p className="text-hago-text/50 text-sm">{description}</p>
            </Link>
          ))}
        </div>

        {/* Capabilities overview */}
        <div className="bg-hago-panel border border-hago-border rounded-xl p-6">
          <h2 className="text-white font-semibold mb-4">Platform Capabilities</h2>
          <div className="grid md:grid-cols-2 gap-3">
            {[
              "PX4 & ArduPilot expert support",
              "MAVLink & MAVSDK code generation",
              "ROS 2 integration guidance",
              "Flight log anomaly detection",
              "UAV architecture diagrams (Mermaid)",
              "RAG from verified technical documents",
              "Computer vision pipeline support",
              "Hardware integration engineering",
            ].map((cap) => (
              <div key={cap} className="flex items-center gap-2 text-sm text-hago-text/70">
                <span className="text-hago-accent">✓</span>
                {cap}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
