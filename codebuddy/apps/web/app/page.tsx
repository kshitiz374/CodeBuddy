"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { HistoryItem, MistakeDashboard, ModelStatus } from "@/lib/types";

export default function DashboardPage() {
  const [mistakes, setMistakes] = useState<MistakeDashboard | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [model, setModel] = useState<ModelStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.mistakes(), api.history(8), api.modelStatus()])
      .then(([m, h, s]) => {
        setMistakes(m);
        setHistory(h.items);
        setModel(s);
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-400">
          A simple record of what you practiced. Not a scientific score.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
          {error}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <div className="card">
          <div className="text-xs uppercase tracking-wide text-slate-400">Mistakes recorded</div>
          <div className="mt-2 text-3xl font-semibold text-white">{mistakes?.total ?? "—"}</div>
        </div>
        <div className="card">
          <div className="text-xs uppercase tracking-wide text-slate-400">Debug sessions</div>
          <div className="mt-2 text-3xl font-semibold text-white">
            {history.filter((h) => h.kind === "debug").length || "—"}
          </div>
        </div>
        <div className="card">
          <div className="text-xs uppercase tracking-wide text-slate-400">Model status</div>
          <div className="mt-2 text-lg font-semibold text-white">
            {model ? `${model.provider}${model.available ? " · ready" : " · unavailable"}` : "…"}
          </div>
          <div className="mt-1 text-xs text-slate-400">{model?.detail}</div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-medium text-white">Most common mistakes</h2>
            <Link href="/mistakes" className="text-xs text-accent-400 hover:text-accent-500">
              Open Mistake Memory
            </Link>
          </div>
          {mistakes && mistakes.patterns.length > 0 ? (
            <ul className="space-y-2 text-sm">
              {mistakes.patterns.slice(0, 5).map((p) => (
                <li key={p.topic} className="flex items-center justify-between">
                  <span className="text-slate-200">{p.topic}</span>
                  <span className="rounded bg-white/5 px-2 py-0.5 text-slate-300">{p.count}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-400">
              Record mistakes after a debug session to see patterns here.
            </p>
          )}
        </div>

        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-medium text-white">Recent sessions</h2>
            <Link href="/debug" className="text-xs text-accent-400 hover:text-accent-500">
              Start debugging
            </Link>
          </div>
          {history.length === 0 ? (
            <p className="text-sm text-slate-400">
              No sessions yet. Paste a stuck snippet into Debug My Code.
            </p>
          ) : (
            <ul className="space-y-2 text-sm">
              {history.map((item) => (
                <li key={item.id} className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="truncate text-slate-200">{item.title}</div>
                    <div className="text-xs text-slate-500">
                      {item.kind}
                      {item.language ? ` · ${item.language}` : ""}
                    </div>
                  </div>
                  <time className="shrink-0 text-xs text-slate-500">
                    {new Date(item.created_at).toLocaleString()}
                  </time>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-accent-500/20 bg-accent-500/5 p-4 text-sm text-slate-300">
        <strong className="text-accent-400">Local-first note:</strong>{" "}
        {model?.privacy ||
          "When using local inference, your code stays on your machine. Cloud providers (if configured) are labeled separately."}
      </div>
    </div>
  );
}
