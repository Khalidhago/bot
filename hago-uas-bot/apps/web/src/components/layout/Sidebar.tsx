"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageSquare,
  FileText,
  Activity,
  LayoutDashboard,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/chat", icon: MessageSquare, label: "AI Chat" },
  { href: "/documents", icon: FileText, label: "Documents" },
  { href: "/flight-logs", icon: Activity, label: "Flight Logs" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/auth/login");
  };

  return (
    <aside className="w-64 min-h-screen bg-hago-panel border-r border-hago-border flex flex-col">
      {/* Logo */}
      <div className="p-5 border-b border-hago-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-hago-blue flex items-center justify-center text-white font-bold text-sm">
            H
          </div>
          <div>
            <p className="text-hago-accent font-bold text-sm tracking-wider">HAGO UAS</p>
            <p className="text-hago-text/40 text-xs">Intelligence Bot</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
          const active = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition",
                active
                  ? "bg-hago-blue/20 text-hago-accent border border-hago-blue/20"
                  : "text-hago-text/60 hover:bg-hago-border/20 hover:text-hago-text"
              )}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* User info */}
      <div className="p-4 border-t border-hago-border">
        {user && (
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-hago-blue/30 border border-hago-blue/30 flex items-center justify-center text-hago-accent text-xs font-bold">
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-white truncate">{user.full_name}</p>
              <p className="text-xs text-hago-text/40 capitalize">{user.role}</p>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 text-sm text-hago-text/50 hover:text-red-400 transition px-2 py-1.5 rounded"
        >
          <LogOut className="w-4 h-4" />
          Sign out
        </button>
      </div>
    </aside>
  );
}
