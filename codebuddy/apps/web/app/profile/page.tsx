"use client";

import { FormEvent, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Profile } from "@/lib/types";

const levels = ["beginner", "intermediate", "advanced"];
const styles = ["simple", "detailed", "analogy-heavy", "example-first"];

function listToText(items: string[]) {
  return items.join(", ");
}

function textToList(value: string) {
  return value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [languages, setLanguages] = useState("");
  const [topics, setTopics] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .profile()
      .then((p) => {
        setProfile(p);
        setLanguages(listToText(p.languages));
        setTopics(listToText(p.topics));
      })
      .catch((err: Error) => setError(err.message));
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    setMessage(null);
    setError(null);
    try {
      const updated = await api.updateProfile({
        name: profile.name,
        level: profile.level,
        languages: textToList(languages),
        topics: textToList(topics),
        preferred_explanation: profile.preferred_explanation,
        hint_first: profile.hint_first,
      });
      setProfile(updated);
      setMessage("Profile saved locally.");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  if (!profile && !error) {
    return <div className="text-sm text-slate-400">Loading profile…</div>;
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-white">Learning Profile</h1>
        <p className="mt-1 text-sm text-slate-400">
          This profile personalizes explanations. It is stored on this machine.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-rose-400/30 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
          {error}
        </div>
      )}
      {message && (
        <div className="rounded-lg border border-accent-500/30 bg-accent-500/10 px-4 py-3 text-sm text-accent-200">
          {message}
        </div>
      )}

      {profile && (
        <form onSubmit={onSubmit} className="card space-y-4">
          <label className="block text-xs text-slate-400">
            Display name
            <input
              className="field mt-1"
              value={profile.name}
              onChange={(e) => setProfile({ ...profile, name: e.target.value })}
            />
          </label>

          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-xs text-slate-400">
              Level
              <select
                className="field mt-1"
                value={profile.level}
                onChange={(e) => setProfile({ ...profile, level: e.target.value })}
              >
                {levels.map((l) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </select>
            </label>
            <label className="block text-xs text-slate-400">
              Preferred explanation style
              <select
                className="field mt-1"
                value={profile.preferred_explanation}
                onChange={(e) => setProfile({ ...profile, preferred_explanation: e.target.value })}
              >
                {styles.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="block text-xs text-slate-400">
            Languages (comma-separated)
            <input className="field mt-1" value={languages} onChange={(e) => setLanguages(e.target.value)} />
          </label>

          <label className="block text-xs text-slate-400">
            Topics (comma-separated)
            <input className="field mt-1" value={topics} onChange={(e) => setTopics(e.target.value)} />
          </label>

          <label className="flex items-center gap-2 text-sm text-slate-200">
            <input
              type="checkbox"
              checked={profile.hint_first}
              onChange={(e) => setProfile({ ...profile, hint_first: e.target.checked })}
            />
            Prefer hints before full solutions
          </label>

          <div className="flex items-center gap-3">
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Saving…" : "Save profile"}
            </button>
            <span className="text-xs text-slate-500">
              Replace this example profile with your friend&apos;s real preferences.
            </span>
          </div>
        </form>
      )}
    </div>
  );
}
