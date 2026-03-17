"use client";

interface ScriptEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function ScriptEditor({ value, onChange }: ScriptEditorProps) {
  return (
    <div>
      <p className="text-sm font-semibold">Script</p>
      <p className="text-xs text-slate-400">
        Paste or edit the narration script used to build scenes.
      </p>
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        rows={6}
        placeholder="Tired of slow workflows? Meet Collide."
        className="mt-3 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm text-slate-100"
      />
    </div>
  );
}
