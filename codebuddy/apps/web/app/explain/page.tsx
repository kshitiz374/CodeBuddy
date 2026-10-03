"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { ExplainResponse } from "@/lib/types";

const examples = ["Explain recursion", "Why does this linked list code work?", "What is a pointer in C++?"];

export default function ExplainPage() {
  const [query, setQuery] = useState(examples[0]);
  const [language, setLanguage] = useState("python");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExplainResponse | null>(null);

  async function onExplain() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.explain({ query, language });
      setResult(data);
    } catch (err) {
      setError((err as Error).message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Explain This</h1>
        <p className="mt-1 text-sm text-slate-400">
          Concept explanations with analogy, example, steps, and a mini question.
        </p>
      </div>

      <div className="card space-y-3">
        <label className="block text-xs text-slate-400">
          What do you want explained?
          <textarea
            className="field mt-1 min-h-[80px]"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <div className="flex flex-wrap gap-2">
          {examples.map((ex) => (
            <button
              key={ex}
              type="button"
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300 hover:bg-white/10"
              onClick={() => setQuery(ex)}
            >
              {ex}
            </button>
          ))}
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select className="field max-w-[160px]" value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="python">python</option>
            <option value="cpp">cpp</option>
            <option value="java">java</option>
            <option value="javascript">javascript</option>
          </select>
          <button className="btn-primary" onClick={onExplain} disabled={loading || query.trim().length < 2}>
            {loading ? "Explaining…" : "Explain concept"}
          </button>
        </div>
        {error && (
          <div className="rounded-lg border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="card space-y-3">
            <h2 className="text-lg font-semibold text-white">{result.concept}</h2>
            <section>
              <h3 className="text-sm font-medium text-accent-400">Simple explanation</h3>
              <p className="mt-1 text-sm leading-relaxed text-slate-300">{result.simple_explanation}</p>
            </section>
            <section>
              <h3 className="text-sm font-medium text-accent-400">Analogy</h3>
              <p className="mt-1 text-sm leading-relaxed text-slate-300">{result.analogy}</p>
            </section>
            <section>
              <h3 className="text-sm font-medium text-accent-400">Common mistake</h3>
              <p className="mt-1 text-sm leading-relaxed text-slate-300">{result.common_mistake}</p>
            </section>
            <section>
              <h3 className="text-sm font-medium text-accent-400">Try this</h3>
              <p className="mt-1 text-sm leading-relaxed text-slate-300">{result.mini_question}</p>
            </section>
          </div>
          <div className="card space-y-3">
            <section>
              <h3 className="text-sm font-medium text-accent-400">Example</h3>
              <pre className="mt-2 overflow-auto rounded-lg border border-white/10 bg-ink-900 p-3 text-xs text-slate-200">
                {result.example_code}
              </pre>
            </section>
            <section>
              <h3 className="text-sm font-medium text-accent-400">Step-by-step</h3>
              <pre className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-300">
                {result.step_by_step}
              </pre>
            </section>
          </div>
        </div>
      )}
    </div>
  );
}
