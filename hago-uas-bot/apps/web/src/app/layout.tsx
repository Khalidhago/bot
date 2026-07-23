import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HAGO UAS Intelligence & Support Bot",
  description: "AI-powered technical support for UAV/UAS engineers and operators",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-hago-dark text-hago-text antialiased">
        {children}
      </body>
    </html>
  );
}
