"use client";

export interface TimelineScene {
  id: number;
  title: string;
  durationLabel: string;
  description: string;
}

interface TimelineProps {
  scenes: TimelineScene[];
  activeSceneId: number;
  onSceneSelect: (sceneId: number) => void;
}

const SCENE_GRADIENTS = [
  "from-indigo-500/30 via-violet-500/20 to-sky-500/10",
  "from-sky-500/30 via-cyan-500/20 to-teal-500/10",
  "from-violet-500/30 via-purple-500/20 to-pink-500/10",
  "from-emerald-500/25 via-teal-500/15 to-cyan-500/10",
];

export default function Timeline({ scenes, activeSceneId, onSceneSelect }: TimelineProps) {
  return (
    <section aria-label="Scene timeline" className="glass-panel rounded-3xl p-5">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="text-[10px] uppercase tracking-[0.3em] text-indigo-300/70">
            Scene Timeline
          </p>
          <h3 className="mt-1.5 text-base font-semibold text-slate-100">AI scene sequence</h3>
        </div>
        <div className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300">
          {scenes.length} {scenes.length === 1 ? "scene" : "scenes"}
        </div>
      </div>

      <div className="relative mb-1">
        <div className="absolute left-0 top-1/2 h-px w-full -translate-y-1/2 bg-gradient-to-r from-indigo-400/20 via-violet-400/15 to-transparent" />
      </div>

      <div className="overflow-x-auto pb-3 [&::-webkit-scrollbar]:h-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-slate-700/60 [&::-webkit-scrollbar-track]:bg-transparent">
        <div className="flex min-w-max gap-3">
          {scenes.map((scene, index) => {
            const isActive = scene.id === activeSceneId;
            const gradient = SCENE_GRADIENTS[index % SCENE_GRADIENTS.length];

            return (
              <button
                key={scene.id}
                type="button"
                onClick={() => onSceneSelect(scene.id)}
                className={[
                  "group relative w-64 flex-none rounded-2xl border p-0 text-left outline-none",
                  "transition-all duration-300 ease-out",
                  "focus-visible:ring-2 focus-visible:ring-indigo-400/50",
                  isActive
                    ? "border-indigo-400/50 bg-indigo-500/10 shadow-[0_0_0_1px_rgba(129,140,248,0.15),0_16px_40px_rgba(129,140,248,0.2)] scale-[1.02]"
                    : "border-white/[0.07] bg-slate-900/40 hover:border-indigo-300/25 hover:bg-slate-800/60 hover:scale-[1.01] hover:shadow-[0_8px_24px_rgba(0,0,0,0.35)]",
                ].join(" ")}
              >
                <div
                  className={`relative overflow-hidden rounded-t-2xl border-b border-white/[0.06] bg-gradient-to-br ${gradient} aspect-video`}
                >
                  <div className="absolute inset-0 opacity-20"
                    style={{
                      backgroundImage:
                        "linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px)",
                      backgroundSize: "24px 24px",
                    }}
                  />
                  <span className="absolute left-2.5 top-2.5 rounded-lg bg-black/40 px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-slate-300 backdrop-blur-sm">
                    Scene {index + 1}
                  </span>
                  <span
                    className={[
                      "absolute right-2.5 top-2.5 rounded-full px-2.5 py-1 text-[11px] font-medium tabular-nums backdrop-blur-sm",
                      isActive
                        ? "bg-indigo-500/30 text-indigo-200"
                        : "bg-black/35 text-slate-300 group-hover:bg-indigo-500/20 group-hover:text-indigo-200",
                    ].join(" ")}
                  >
                    {scene.durationLabel}
                  </span>
                  {isActive && (
                    <span className="absolute bottom-2.5 right-2.5 flex h-2 w-2 items-center justify-center">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75" />
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-indigo-400" />
                    </span>
                  )}
                </div>
                <div className="px-3.5 pb-3.5 pt-3">
                  <p
                    className={[
                      "text-sm font-semibold transition-colors duration-200",
                      isActive ? "text-indigo-200" : "text-slate-100 group-hover:text-indigo-100",
                    ].join(" ")}
                  >
                    {scene.title}
                  </p>
                  <p className="mt-1.5 line-clamp-2 text-xs leading-5 text-slate-400 group-hover:text-slate-300 transition-colors duration-200">
                    {scene.description}
                  </p>
                </div>
                <div
                  className={[
                    "absolute bottom-0 left-1/2 h-0.5 -translate-x-1/2 rounded-full transition-all duration-300",
                    isActive ? "w-12 bg-indigo-400" : "w-0 bg-transparent",
                  ].join(" ")}
                />
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
