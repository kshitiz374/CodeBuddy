"use client";

import dynamic from "next/dynamic";

const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full items-center justify-center rounded-lg border border-white/10 bg-ink-900 text-sm text-slate-400">
      Loading editor…
    </div>
  ),
});

type Props = {
  language: string;
  value: string;
  onChange: (value: string) => void;
  height?: string;
};

const langMap: Record<string, string> = {
  cpp: "cpp",
  c: "c",
  python: "python",
  java: "java",
  javascript: "javascript",
  typescript: "typescript",
  go: "go",
  rust: "rust",
};

export function CodeEditor({ language, value, onChange, height = "360px" }: Props) {
  return (
    <div className="overflow-hidden rounded-lg border border-white/10 bg-[#0f172a]">
      <MonacoEditor
        height={height}
        language={langMap[language] || "plaintext"}
        value={value}
        theme="vs-dark"
        onChange={(v) => onChange(v ?? "")}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 4,
          wordWrap: "on",
        }}
      />
    </div>
  );
}
