import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";
import { ModelStatusBadge } from "@/components/ModelStatusBadge";

export const metadata: Metadata = {
  title: "CodeBuddy — Local-first AI coding companion",
  description:
    "A patient local AI mentor for debugging and learning programming. Hints first, explanations that stick.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col">
            <header className="flex items-center justify-between border-b border-white/10 px-6 py-4">
              <div>
                <div className="text-sm font-semibold text-white">CodeBuddy</div>
                <div className="text-xs text-slate-400">
                  Don&apos;t just get the answer — understand why you are stuck.
                </div>
              </div>
              <ModelStatusBadge />
            </header>
            <main className="flex-1 overflow-auto p-6">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
