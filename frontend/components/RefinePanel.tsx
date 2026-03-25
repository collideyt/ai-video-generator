"use client";

import type { TimelineScene } from "./Timeline";

interface RefinePanelProps {
  scenes: TimelineScene[];
  initialPrompt: string;
  initialStyle: string;
  initialVoice: string;
}

export default function RefinePanel({ scenes, initialPrompt, initialStyle, initialVoice }: RefinePanelProps) {
  return (
    <section className="glass-panel h-full rounded-3xl border border-white/5 bg-slate-900/60 p-6">
      <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-300">Refine Settings</h3>
      <div className="space-y-4">
        <div>
          <p className="text-xs text-slate-500">Prompt</p>
          <p className="mt-1 line-clamp-3 text-sm text-slate-200">{initialPrompt}</p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-slate-500">Style</p>
            <p className="mt-1 text-sm capitalize text-slate-200">{initialStyle}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Voice</p>
            <p className="mt-1 text-sm capitalize text-slate-200">{initialVoice}</p>
          </div>
        </div>

        <div className="mt-4 border-t border-slate-800 pt-4">
          <p className="mb-2 text-xs text-slate-500">Generated Scenes</p>
          <div className="max-h-[300px] space-y-2 overflow-y-auto pr-2 text-xs text-slate-400">
            {scenes.map((s) => (
              <div key={s.id} className="rounded border border-slate-800 bg-slate-950/50 p-2">
                <span className="font-semibold text-slate-300">{s.title}</span> - {s.durationLabel}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
