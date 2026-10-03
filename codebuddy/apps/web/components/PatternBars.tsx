"use client";

export function PatternBars({
  patterns,
}: {
  patterns: { topic: string; count: number }[];
}) {
  const max = Math.max(1, ...patterns.map((p) => p.count));
  return (
    <div className="space-y-3">
      {patterns.length === 0 && (
        <p className="text-sm text-slate-400">No mistakes recorded yet.</p>
      )}
      {patterns.map((p) => (
        <div key={p.topic}>
          <div className="mb-1 flex items-center justify-between text-sm">
            <span className="text-slate-200">{p.topic}</span>
            <span className="text-slate-400">{p.count}</span>
          </div>
          <div className="h-3 w-full overflow-hidden rounded bg-white/5">
            <div
              className="h-full rounded bg-gradient-to-r from-accent-600 to-accent-400"
              style={{ width: `${Math.max(8, Math.round((p.count / max) * 100))}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
