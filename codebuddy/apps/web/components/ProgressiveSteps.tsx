"use client";

const steps = [
  { key: "problem", label: "Problem" },
  { key: "explanation", label: "Why it happens" },
  { key: "hint", label: "Hint" },
  { key: "concept", label: "Concept" },
  { key: "fix", label: "Fix" },
  { key: "lesson", label: "What you learned" },
] as const;

export type DebugStepKey = (typeof steps)[number]["key"];

export function ProgressiveSteps({
  data,
  revealed,
  onReveal,
}: {
  data: Record<DebugStepKey, string> | null;
  revealed: DebugStepKey[];
  onReveal: (key: DebugStepKey) => void;
}) {
  return (
    <div className="space-y-3">
      {steps.map((step, index) => {
        const isRevealed = revealed.includes(step.key);
        const content = data?.[step.key] || "";
        return (
          <div
            key={step.key}
            className={`rounded-xl border p-4 transition ${
              isRevealed
                ? "border-white/10 bg-white/[0.03]"
                : "border-dashed border-white/10 bg-transparent"
            }`}
          >
            <div className="mb-2 flex items-center justify-between gap-3">
              <div className="text-sm font-medium text-slate-200">
                <span className="mr-2 text-slate-500">{index + 1}</span>
                {step.label}
              </div>
              {!isRevealed && (
                <button
                  type="button"
                  onClick={() => onReveal(step.key)}
                  className="rounded-md bg-white/10 px-3 py-1 text-xs text-slate-200 hover:bg-white/15"
                >
                  Reveal
                </button>
              )}
            </div>
            {isRevealed ? (
              <div className="whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
                {content || "—"}
              </div>
            ) : (
              <div className="text-xs text-slate-500">Hidden until you ask for this level.</div>
            )}
          </div>
        );
      })}
    </div>
  );
}
