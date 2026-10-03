export type DebugResponse = {
  problem: string;
  severity: string;
  location: string | null;
  explanation: string;
  hint: string;
  concept: string;
  fix: string;
  lesson: string;
  deterministic: {
    source: string;
    findings: string[];
    compiler_output: string | null;
    executed: boolean;
  };
  prior_mistake: {
    exists: boolean;
    summary: string | null;
    topic: string | null;
    connection: string | null;
    mistake_id: string | null;
  };
  session_id: string;
  provider: string;
  model_name: string | null;
};

export type ExplainResponse = {
  concept: string;
  simple_explanation: string;
  analogy: string;
  example_code: string;
  step_by_step: string;
  common_mistake: string;
  mini_question: string;
  provider: string;
  model_name: string | null;
  session_id: string | null;
};

export type Profile = {
  name: string;
  level: string;
  languages: string[];
  topics: string[];
  preferred_explanation: string;
  hint_first: boolean;
  updated_at?: string | null;
};

export type MistakeOut = {
  id: string;
  topic: string;
  problem_summary: string;
  cause: string;
  lesson: string;
  language: string | null;
  session_id: string | null;
  created_at: string;
};

export type MistakeDashboard = {
  total: number;
  patterns: { topic: string; count: number }[];
  note: string;
  items: MistakeOut[];
};

export type HistoryItem = {
  id: string;
  kind: string;
  title: string;
  language: string | null;
  created_at: string;
};

export type ModelStatus = {
  provider: string;
  model_name: string | null;
  is_local: boolean;
  available: boolean;
  detail: string;
  privacy?: string;
  models?: string[];
};

export type ApiError = {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
};
