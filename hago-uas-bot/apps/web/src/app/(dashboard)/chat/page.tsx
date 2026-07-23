"use client";

import { useAuthStore } from "@/lib/auth";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { redirect } from "next/navigation";

export default function ChatPage() {
  const { accessToken } = useAuthStore();

  if (!accessToken) {
    redirect("/auth/login");
  }

  return (
    <div className="h-screen">
      <ChatInterface token={accessToken} />
    </div>
  );
}
