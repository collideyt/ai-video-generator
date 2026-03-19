"use client";

export interface VideoSpecs {
  duration: number;
  aspect_ratio: "16:9" | "9:16" | "1:1";
  captions: boolean;
  voiceover: boolean;
}

interface SettingsPanelProps {
  value: VideoSpecs;
  onChange: (value: VideoSpecs) => void;
}

function ToggleRow({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={`flex items-center justify-between rounded-[18px] border px-4 py-3 text-sm transition ${
        checked
          ? "border-emerald-400/30 bg-emerald-400/10 text-slate-100"
          : "border-slate-800 bg-slate-950/50 text-slate-300 hover:border-slate-700"
      }`}
    >
      <span>{label}</span>
      <span
        className={`flex h-5 w-5 items-center justify-center rounded-md text-[11px] font-bold ${
          checked ? "bg-emerald-400 text-slate-950" : "bg-slate-800 text-slate-500"
        }`}
      >
        {checked ? "✓" : ""}
      </span>
    </button>
  );
}

export default function SettingsPanel({ value, onChange }: SettingsPanelProps) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-semibold text-slate-100">Video settings</p>
        <p className="text-xs text-slate-400">
          Choose format, runtime, and AI services.
        </p>
      </div>

      <div className="grid gap-3 grid-cols-3">
        {(["16:9", "9:16", "1:1"] as const).map((ratio) => (
          <button
            key={ratio}
            type="button"
            onClick={() => onChange({ ...value, aspect_ratio: ratio })}
            className={`rounded-[18px] border px-4 py-3 text-sm font-semibold transition ${
              value.aspect_ratio === ratio
                ? "border-sky-400/50 bg-sky-400/12 text-sky-100 shadow-[0_0_0_1px_rgba(125,211,252,0.12)]"
                : "border-slate-800 bg-slate-950/45 text-slate-400 hover:border-slate-700 hover:text-slate-200"
            }`}
          >
            {ratio}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        <label className="flex flex-col gap-2 text-sm text-slate-300">
          <span className="text-xs uppercase tracking-[0.22em] text-slate-500">Duration</span>
          <input
            type="number"
            min={5}
            value={value.duration}
            onChange={(event) => onChange({ ...value, duration: Number(event.target.value) })}
            className="rounded-[18px] border border-slate-800 bg-slate-950/45 px-4 py-3 text-base text-slate-100 outline-none transition focus:border-sky-400/50"
          />
        </label>

        <div className="grid gap-3 sm:grid-cols-2">
          <ToggleRow
            label="Captions"
            checked={value.captions}
            onChange={(checked) => onChange({ ...value, captions: checked })}
          />
          <ToggleRow
            label="Voiceover"
            checked={value.voiceover}
            onChange={(checked) => onChange({ ...value, voiceover: checked })}
          />
        </div>
      </div>
    </div>
  );
}
