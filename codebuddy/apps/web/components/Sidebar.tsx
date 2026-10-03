"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { href: "/", label: "Dashboard" },
  { href: "/debug", label: "Debug My Code" },
  { href: "/explain", label: "Explain This" },
  { href: "/mistakes", label: "Mistakes" },
  { href: "/profile", label: "Learning Profile" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-56 shrink-0 border-r border-white/10 bg-ink-900/80 p-4">
      <div className="mb-8">
        <div className="text-lg font-semibold tracking-tight text-white">CodeBuddy</div>
        <div className="text-xs text-slate-400">Local-first coding mentor</div>
      </div>
      <nav className="space-y-1">
        {nav.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-md px-3 py-2 text-sm transition ${
                active
                  ? "bg-accent-500/15 text-accent-400"
                  : "text-slate-300 hover:bg-white/5 hover:text-white"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-10 rounded-lg border border-white/10 bg-white/[0.03] p-3 text-xs leading-relaxed text-slate-400">
        Philosophy: diagnose first, hint next, full fix later.
        <div className="mt-2 text-slate-500">Private code stays local with local inference.</div>
      </div>
    </aside>
  );
}
