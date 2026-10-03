import type {
  ApiError,
  DebugResponse,
  ExplainResponse,
  HistoryItem,
  MistakeDashboard,
  ModelStatus,
  Profile,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE || "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!res.ok) {
    const err = data as ApiError;
    const message = err?.error?.message || res.statusText || "Request failed";
    throw new Error(message);
  }
  return data as T;
}

export const api = {
  health: () => request<{ status: string; provider: string }>("/api/health"),
  modelStatus: () => request<ModelStatus>("/api/model/status"),
  debug: (body: unknown) =>
    request<DebugResponse>("/api/debug", { method: "POST", body: JSON.stringify(body) }),
  hint: (sessionId: string, nextLevel: string) =>
    request<{ session_id: string; level: string; content: string; provider: string }>(
      "/api/hint",
      { method: "POST", body: JSON.stringify({ session_id: sessionId, next_level: nextLevel }) },
    ),
  explain: (body: unknown) =>
    request<ExplainResponse>("/api/explain", { method: "POST", body: JSON.stringify(body) }),
  profile: () => request<Profile>("/api/profile"),
  updateProfile: (body: Partial<Profile>) =>
    request<Profile>("/api/profile", { method: "PUT", body: JSON.stringify(body) }),
  mistakes: () => request<MistakeDashboard>("/api/mistakes"),
  createMistake: (body: unknown) =>
    request<import("./types").MistakeOut>("/api/mistakes", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  history: (limit = 20) => request<{ items: HistoryItem[]; total: number }>(`/api/history?limit=${limit}`),
};
