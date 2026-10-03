"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ModelStatus } from "@/lib/types";

export function ModelStatusBadge() {
  const [status, setStatus] = useState<ModelStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .modelStatus()
      .then((data) => {
        if (!cancelled) setStatus(data);
      })
      .catch((err: Error) => {
        if (!cancelled) setError(err.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-full border border-amber-400/30 bg-amber-400/10 px-3 py-1 text-xs text-amber-200">
        <span className="h-2 w-2 rounded-full bg-amber-400" />
        API offline — start the backend
      </div>
    );
  }

  if (!status) {
    return (
      <div className="flex items-center gap-2 rounded-full border border-white/10 px-3 py-1 text-xs text-slate-400">
        <span className="h-2 w-2 animate-pulse rounded-full bg-slate-500" />
        Checking model…
      </div>
    );
  }

  const local = status.is_local;
  return (
    <div
      title={status.detail}
      className={`flex items-center gap-2 rounded-full border px-3 py-1 text-xs ${
        status.available
          ? local
            ? "border-accent-500/40 bg-accent-500/10 text-accent-400"
            : "border-sky-400/30 bg-sky-400/10 text-sky-200"
          : "border-rose-400/30 bg-rose-400/10 text-rose-200"
      }`}
    >
      <span
        className={`h-2 w-2 rounded-full ${
          status.available ? (local ? "bg-accent-400" : "bg-sky-400") : "bg-rose-400"
        }`}
      />
      {local ? "Local AI" : "Non-local AI"} ● {status.provider}
      {status.model_name ? ` · ${status.model_name}` : ""}
    </div>
  );
}
