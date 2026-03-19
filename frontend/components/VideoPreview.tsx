"use client";

interface SceneItem {
  id: number;
  label: string;
  duration: number;
  text: string;
}

interface VideoPreviewProps {
  videoUrl: string;
  aspectRatio?: "16:9" | "9:16" | "1:1";
  scenes?: SceneItem[];
}

const ASPECT_CLASS: Record<string, string> = {
  "16:9": "aspect-video",
  "9:16": "aspect-[9/16]",
  "1:1": "aspect-square",
};

export default function VideoPreview({
  videoUrl,
  aspectRatio = "9:16",
  scenes = [],
}: VideoPreviewProps) {
  return (
    <div className="space-y-5">
      <div className="mx-auto w-full max-w-[360px]">
        <div className="glass-panel rounded-[36px] p-3">
          <div className="rounded-[30px] border border-white/10 bg-slate-950 p-3 shadow-2xl">
            <div className="mb-3 flex items-center justify-between px-2 text-xs text-slate-500">
              <span>AI Preview</span>
              <span>{aspectRatio}</span>
            </div>
            <div
              className={`overflow-hidden rounded-[26px] border border-slate-800 bg-black ${ASPECT_CLASS[aspectRatio]}`}
            >
              {videoUrl ? (
                <video
                  src={videoUrl}
                  controls
                  className="h-full w-full object-contain"
                />
              ) : (
                <div className="flex h-full items-center justify-center bg-[radial-gradient(circle_at_top,rgba(34,197,94,0.15),transparent_35%),linear-gradient(180deg,#020617_0%,#111827_100%)] px-8 text-center text-sm text-slate-400">
                  Rendered video will appear here in a vertical reel-style player.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="glass-panel rounded-[28px] p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-slate-100">Scene Timeline</p>
            <p className="text-xs text-slate-400">
              Review pacing, scene purpose, and narration mapping.
            </p>
          </div>
          <div className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300">
            {scenes.length} scenes
          </div>
        </div>
        <div className="mt-5 space-y-3">
          {scenes.length > 0 ? (
            scenes.map((scene) => (
              <div
                key={scene.id}
                className="rounded-[24px] border border-slate-800 bg-slate-950/70 p-4 transition hover:border-sky-400/40"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-100">
                      Scene {scene.id} - {scene.label}
                    </p>
                    <p className="mt-2 text-sm leading-6 text-slate-300">{scene.text}</p>
                  </div>
                  <span className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300">
                    {scene.duration}s
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="rounded-[24px] border border-dashed border-slate-700 bg-slate-950/60 p-5 text-sm text-slate-400">
              Add a script to build a scene breakdown before generation.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
