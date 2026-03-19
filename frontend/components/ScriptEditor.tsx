"use client";

interface ScriptEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function ScriptEditor({ value, onChange }: ScriptEditorProps) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-semibold text-slate-100">Script</p>
        <p className="text-xs text-slate-400">
          Paste or edit the narration script used to build scenes.
        </p>
      </div>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={10}
        placeholder="Tired of slow workflows? Meet Collide."
        className="min-h-[220px] w-full rounded-[24px] border border-slate-700/60 bg-slate-950/60 px-5 py-4 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-sky-400/60 focus:ring-2 focus:ring-sky-400/20"
      />
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>Use short, punchy lines for stronger reel pacing.</span>
        <span>{value.trim() ? value.trim().split(/\s+/).length : 0} words</span>
      </div>
    </div>
  );
}
