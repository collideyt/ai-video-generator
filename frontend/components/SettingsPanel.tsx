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

export default function SettingsPanel({ value, onChange }: SettingsPanelProps) {
  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-semibold">Video settings</p>
        <p className="text-xs text-slate-400">
          Choose format, runtime, and AI services.
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {(["16:9", "9:16", "1:1"] as const).map((ratio) => (
          <button
            key={ratio}
            type="button"
            onClick={() => onChange({ ...value, aspect_ratio: ratio })}
            className={`rounded-[22px] border px-4 py-4 text-sm font-semibold transition ${
              value.aspect_ratio === ratio
                ? "border-sky-400/60 bg-sky-400/10 text-sky-200 shadow-glow"
                : "border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-600"
            }`}
          >
            {ratio}
          </button>
        ))}
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-2 text-sm">
          Duration (seconds)
          <input
            type="number"
            min={5}
            value={value.duration}
            onChange={(event) =>
              onChange({ ...value, duration: Number(event.target.value) })
            }
            className="rounded-[18px] border border-slate-800 bg-slate-950/60 px-4 py-3 outline-none focus:border-sky-400/60"
          />
        </label>
        <div className="flex flex-col gap-3 text-sm">
          <label className="flex items-center justify-between rounded-[20px] border border-slate-800 bg-slate-950/60 px-4 py-3">
            Captions
            <input
              type="checkbox"
              checked={value.captions}
              onChange={(event) =>
                onChange({ ...value, captions: event.target.checked })
              }
              className="h-4 w-4 accent-emerald-500"
            />
          </label>
          <label className="flex items-center justify-between rounded-[20px] border border-slate-800 bg-slate-950/60 px-4 py-3">
            Voiceover
            <input
              type="checkbox"
              checked={value.voiceover}
              onChange={(event) =>
                onChange({ ...value, voiceover: event.target.checked })
              }
              className="h-4 w-4 accent-emerald-500"
            />
          </label>
        </div>
      </div>
    </div>
  );
}
