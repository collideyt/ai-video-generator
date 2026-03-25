"use client";

export type PromptStyle = "cinematic" | "viral" | "minimal";
export type PromptVoice = "male" | "female" | "none";
export type PromptDuration = "15s" | "30s" | "60s";

export interface PromptInputValue {
  prompt: string;
  style: PromptStyle;
  voice: PromptVoice;
  duration: PromptDuration;
  images: File[];
  videos: File[];
  audio: File | null;
}

interface PromptInputProps {
  value: PromptInputValue;
  isGenerating: boolean;
  onChange: (next: PromptInputValue) => void;
  onGenerate: () => void;
}

const inputClass =
  "h-11 w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 text-sm text-slate-100 outline-none transition duration-300 focus:border-indigo-400/60 focus:ring-2 focus:ring-indigo-400/20";

export default function PromptInput({
  value,
  isGenerating,
  onChange,
  onGenerate,
}: PromptInputProps) {
  const updateField = <K extends keyof PromptInputValue>(
    key: K,
    nextValue: PromptInputValue[K]
  ) => {
    onChange({ ...value, [key]: nextValue });
  };

  return (
    <section className="glass-panel rounded-3xl p-6 md:p-8">
      <div className="mb-4">
        <p className="text-xs uppercase tracking-[0.32em] text-indigo-200/75">
          Prompt-First Studio
        </p>
        <h1 className="mt-3 text-3xl font-semibold leading-tight text-gradient md:text-4xl">
          Type one idea, get a cinematic video in seconds.
        </h1>
      </div>

      <textarea
        value={value.prompt}
        onChange={(event) => updateField("prompt", event.target.value)}
        onKeyDown={(event) => {
          if ((event.ctrlKey || event.metaKey) && event.key === "Enter" && !isGenerating) {
            onGenerate();
          }
        }}
        placeholder="Describe your video..."
        className="h-40 w-full resize-none rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-4 text-base leading-7 text-slate-100 outline-none transition duration-300 placeholder:text-slate-500 focus:border-indigo-400/70 focus:ring-2 focus:ring-indigo-400/25"
      />

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Style</span>
          <select
            value={value.style}
            onChange={(event) => updateField("style", event.target.value as PromptStyle)}
            className={inputClass}
          >
            <option value="cinematic">cinematic</option>
            <option value="viral">viral</option>
            <option value="minimal">minimal</option>
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Voice</span>
          <select
            value={value.voice}
            onChange={(event) => updateField("voice", event.target.value as PromptVoice)}
            className={inputClass}
          >
            <option value="male">male</option>
            <option value="female">female</option>
            <option value="none">none</option>
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">
            Duration
          </span>
          <select
            value={value.duration}
            onChange={(event) => updateField("duration", event.target.value as PromptDuration)}
            className={inputClass}
          >
            <option value="15s">15s</option>
            <option value="30s">30s</option>
            <option value="60s">60s</option>
          </select>
        </label>

        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Images</span>
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={(e) => updateField("images", Array.from(e.target.files || []))}
            className="w-full text-sm text-slate-400 file:mr-3 file:rounded-xl file:border-0 file:bg-white/10 file:px-3 file:py-2.5 file:text-xs file:font-semibold file:uppercase file:tracking-wider file:text-slate-200 hover:file:bg-white/20"
          />
        </label>

        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Videos</span>
          <input
            type="file"
            multiple
            accept="video/*"
            onChange={(e) => updateField("videos", Array.from(e.target.files || []))}
            className="w-full text-sm text-slate-400 file:mr-3 file:rounded-xl file:border-0 file:bg-white/10 file:px-3 file:py-2.5 file:text-xs file:font-semibold file:uppercase file:tracking-wider file:text-slate-200 hover:file:bg-white/20"
          />
        </label>

        <label className="space-y-2">
          <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Audio Overlay</span>
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => updateField("audio", e.target.files?.[0] || null)}
            className="w-full text-sm text-slate-400 file:mr-3 file:rounded-xl file:border-0 file:bg-white/10 file:px-3 file:py-2.5 file:text-xs file:font-semibold file:uppercase file:tracking-wider file:text-slate-200 hover:file:bg-white/20"
          />
        </label>
      </div>

      <div className="mt-6 flex flex-col items-start gap-3">
        <button
          type="button"
          onClick={onGenerate}
          disabled={isGenerating || !value.prompt.trim()}
          className="glow-button rounded-xl bg-gradient-to-r from-indigo-400 via-violet-400 to-sky-400 px-6 py-3 text-sm font-semibold text-slate-950 transition duration-300 hover:-translate-y-0.5 hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-55 disabled:transform-none"
        >
          {"\u{1F680} Generate Video"}
        </button>
        <p className="text-sm text-slate-400">
          AI will create scenes, voiceover, and music automatically. Provide visual assets to override AI defaults.
        </p>
      </div>
    </section>
  );
}
