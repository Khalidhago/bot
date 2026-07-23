"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";

const schema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const { setTokens, setUser } = useAuthStore();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError(null);
    try {
      const tokens = await api.auth.login(data.email, data.password);
      setTokens(tokens.access_token, tokens.refresh_token);
      const user = await api.auth.me(tokens.access_token);
      setUser(user);
      router.push("/chat");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-hago-dark">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded bg-hago-blue flex items-center justify-center text-white font-bold text-sm">
              H
            </div>
            <span className="text-hago-accent font-bold text-lg tracking-wider">
              HAGO UAS
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-2">Intelligence & Support Bot</h1>
          <p className="text-hago-text/60 text-sm mt-1">Sign in to your engineering workspace</p>
        </div>

        {/* Card */}
        <div className="bg-hago-panel border border-hago-border rounded-xl p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-hago-text/80 mb-1">
                Email
              </label>
              <input
                {...register("email")}
                type="email"
                placeholder="engineer@example.com"
                className="w-full bg-hago-dark border border-hago-border rounded-lg px-3 py-2 text-white placeholder-hago-text/30 focus:outline-none focus:border-hago-blue transition"
              />
              {errors.email && (
                <p className="text-red-400 text-xs mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-hago-text/80 mb-1">
                Password
              </label>
              <input
                {...register("password")}
                type="password"
                placeholder="••••••••"
                className="w-full bg-hago-dark border border-hago-border rounded-lg px-3 py-2 text-white placeholder-hago-text/30 focus:outline-none focus:border-hago-blue transition"
              />
              {errors.password && (
                <p className="text-red-400 text-xs mt-1">{errors.password.message}</p>
              )}
            </div>

            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-hago-blue hover:bg-hago-blue-light text-white font-medium py-2.5 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Signing in…" : "Sign In"}
            </button>
          </form>

          <p className="text-center text-sm text-hago-text/50 mt-6">
            Don&apos;t have an account?{" "}
            <a href="/auth/register" className="text-hago-accent hover:underline">
              Register
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
