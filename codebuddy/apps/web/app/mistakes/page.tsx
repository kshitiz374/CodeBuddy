"use client";

import { useEffect, useState } from "react";
import { PatternBars } from "@/components/PatternBars";
import { api } from "@/lib/api";
import type { MistakeDashboard } from "@/lib/types";

export default function MistakesPage() {
  const [data, setData] = useState<MistakeDashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .mistakes()
      .then(setData)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Mistake Memory</h1>
        <p className="mt-1 text-sm text-slate-400">A local log of problems you have already solved.</p>
      </div>

      {error && (
        <div className="rounded-lg border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
          {error}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card">
          <h2 className="mb-4 font-medium text-white">Your learning patterns</h2>
          <PatternBars patterns={data?.patterns || []} />
          {data && (
            <p className="mt-4 text-xs leading-relaxed text-slate-500">{data.note}</p>
          )}
        </div>

        <div className="card">
          <h2 className="mb-4 font-medium text-white">All mistakes ({data?.total ?? 0})</h2>
          <div className="space-y-3">
            {(data?.items || []).map((item) => (
              <div key={item.id} className="rounded-lg border border-white/10 bg-ink-900/50 p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="rounded bg-white/5 px-2 py-0.5 text-xs text-accent-400">{item.topic}</span>
                  <time className="text-xs text-slate-500">{new Date(item.created_at).toLocaleString()}</time>
                </div>
                <div className="mt-2 text-sm text-slate-200">{item.problem_summary}</div>
                <div className="mt-1 text-xs text-slate-400">Cause: {item.cause}</div>
                <div className="mt-1 text-xs text-slate-300">Lesson: {item.lesson}</div>
              </div>
            ))}
            {(data?.items.length ?? 0) === 0 && (
              <p className="text-sm text-slate-400">
                After a debug session, save a mistake note to start building this memory.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
