"use client";

import { useState } from "react";
import { CodeEditor } from "@/components/CodeEditor";
import { ProgressiveSteps, type DebugStepKey } from "@/components/ProgressiveSteps";
import { api } from "@/lib/api";
import type { DebugResponse } from "@/lib/types";

const languages = ["cpp", "python", "java", "c", "javascript", "typescript"];

const demoCode = `struct Node {
    int data;
    Node* next;
};

int main() {
    Node* head;
    head->data = 10;
    return 0;
}
`;

const revealOrder: DebugStepKey[] = ["problem", "explanation", "hint", "concept", "fix", "lesson"];

export default function DebugPage() {
  const [code, setCode] = useState(demoCode);
  const [language, setLanguage] = useState("cpp");
  const [errorMessage, setErrorMessage] = useState("Segmentation fault (core dumped)");
  const [expected, setExpected] = useState("Set head->data to 10 without crashing");
  const [actual, setExpectedActual] = useState("Program crashes when writing head->data");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DebugResponse | null>(null);
  const [revealed, setRevealed] = useState<DebugStepKey[]>(["problem"]);
  const [recordMistake, setRecordMistake] = useState(true);
  const [savedMistake, setSavedMistake] = useState(false);

  async function onAnalyze() {
    setLoading(true);
    setError(null);
    setSavedMistake(false);
    try {
      const data = await api.debug({
        code,
        language,
        error_message: errorMessage || null,
        expected_behavior: expected || null,
        actual_behavior: actual || null,
        hint_level: "learn",
      });
      setResult(data);
      setRevealed(["problem", "explanation"]);
    } catch (err) {
      setError((err as Error).message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  async function revealNext() {
    if (!result) return;
    const next = revealOrder.find((key) => !revealed.includes(key));
    if (!next) return;
    // Prefer API hint for later levels when available
    if (["hint", "concept", "fix", "lesson"].includes(next)) {
      try {
        const hint = await api.hint(result.session_id, next === "concept" ? "explain" : next === "lesson" ? "learn" : next);
        // Merge into local display by revealing the step; content already in result
        void hint;
      } catch {
        // fall through and reveal local content
      }
    }
    setRevealed((prev) => [...prev, next]);
  }

  async function saveMistake() {
    if (!result) return;
    try {
      await api.createMistake({
        topic: result.concept.split(/[:(]/)[0].slice(0, 80) || "General",
        problem_summary: result.problem,
        cause: result.explanation.slice(0, 300),
        lesson: result.lesson,
        language,
        session_id: result.session_id,
      });
      setSavedMistake(true);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">Debug My Code</h1>
          <p className="mt-1 text-sm text-slate-400">
            Paste the stuck code. CodeBuddy diagnoses first, then unlocks hints step by step.
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <div className="card space-y-3">
            <div className="grid gap-3 sm:grid-cols-2">
              <label className="block text-xs text-slate-400">
                Language
                <select
                  className="field mt-1"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                >
                  {languages.map((l) => (
                    <option key={l} value={l}>
                      {l}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-xs text-slate-400">
                Error message
                <input
                  className="field mt-1"
                  value={errorMessage}
                  onChange={(e) => setErrorMessage(e.target.value)}
                  placeholder="Paste compiler/runtime error"
                />
              </label>
            </div>
            <label className="block text-xs text-slate-400">
              Expected behavior
              <input
                className="field mt-1"
                value={expected}
                onChange={(e) => setExpected(e.target.value)}
              />
            </label>
            <label className="block text-xs text-slate-400">
              Actual behavior
              <input
                className="field mt-1"
                value={actual}
                onChange={(e) => setExpectedActual(e.target.value)}
              />
            </label>
          </div>

          <CodeEditor language={language} value={code} onChange={setCode} />

          <div className="flex flex-wrap items-center gap-3">
            <button className="btn-primary" onClick={onAnalyze} disabled={loading || !code.trim()}>
              {loading ? "Analyzing…" : "Analyze Code"}
            </button>
            {result && (
              <>
                <button className="btn-secondary" onClick={revealNext} disabled={revealed.length >= revealOrder.length}>
                  Unlock next step
                </button>
                <label className="flex items-center gap-2 text-xs text-slate-300">
                  <input
                    type="checkbox"
                    checked={recordMistake}
                    onChange={(e) => setRecordMistake(e.target.checked)}
                  />
                  Record this in Mistake Memory after review
                </label>
              </>
            )}
          </div>

          {error && (
            <div className="rounded-lg border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
              {error}
            </div>
          )}
        </div>

        <div className="space-y-4">
          {!result && (
            <div className="card h-full min-h-[320px] flex items-center justify-center text-sm text-slate-400">
              Analysis appears here after you submit code.
            </div>
          )}
          {result && (
            <>
              <div className="card space-y-2">
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="rounded bg-white/5 px-2 py-0.5 text-slate-300">
                    severity: {result.severity}
                  </span>
                  <span className="rounded bg-white/5 px-2 py-0.5 text-slate-300">
                    source: {result.deterministic.source}
                  </span>
                  <span className="rounded bg-white/5 px-2 py-0.5 text-slate-300">
                    provider: {result.provider}
                  </span>
                  {result.location && (
                    <span className="rounded bg-white/5 px-2 py-0.5 text-slate-300">
                      location: {result.location}
                    </span>
                  )}
                </div>
                {result.deterministic.findings.length > 0 && (
                  <div className="rounded-lg border border-white/10 bg-ink-900/60 p-3 text-xs text-slate-300">
                    <div className="mb-1 font-medium text-slate-200">Static analysis</div>
                    <ul className="list-disc space-y-1 pl-4">
                      {result.deterministic.findings.map((f, i) => (
                        <li key={i}>{f}</li>
                      ))}
                    </ul>
                    <div className="mt-2 text-slate-500">
                      Deterministic checks are not a full compiler run.
                    </div>
                  </div>
                )}
                {result.prior_mistake.exists && (
                  <div className="rounded-lg border border-amber-400/20 bg-amber-400/10 p-3 text-xs text-amber-100">
                    <div className="font-medium">Have I made this mistake before?</div>
                    <div className="mt-1">{result.prior_mistake.connection}</div>
                  </div>
                )}
              </div>

              <ProgressiveSteps
                data={{
                  problem: result.problem,
                  explanation: result.explanation,
                  hint: result.hint,
                  concept: result.concept,
                  fix: result.fix,
                  lesson: result.lesson,
                }}
                revealed={revealed}
                onReveal={(key) => setRevealed((prev) => (prev.includes(key) ? prev : [...prev, key]))}
              />

              {recordMistake && (
                <div className="card flex flex-wrap items-center justify-between gap-3">
                  <div className="text-sm text-slate-300">
                    Save a short mistake note for pattern tracking?
                  </div>
                  <button className="btn-secondary" onClick={saveMistake} disabled={savedMistake}>
                    {savedMistake ? "Saved to Mistake Memory" : "Save mistake note"}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
