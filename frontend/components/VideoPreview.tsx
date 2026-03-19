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
}: VideoPreviewProps) {
  const widthClass =
    aspectRatio === "9:16"
      ? "max-w-[420px]"
      : aspectRatio === "1:1"
        ? "max-w-[720px]"
        : "max-w-4xl";

  return (
    <div className="flex h-full items-center justify-center">
      <div className={`w-full ${widthClass}`}>
        <div className="glass-panel rounded-[36px] p-4 shadow-[0_30px_80px_rgba(2,6,23,0.55)]">
          <div className="rounded-[32px] border border-white/10 bg-slate-950 p-4">
            <div className="mb-4 flex items-center justify-between px-1 text-xs text-slate-500">
              <span>AI Preview</span>
              <span>{videoUrl ? "Latest render" : "Awaiting render"}</span>
            </div>
            <div
              className={`overflow-hidden rounded-[28px] border border-slate-800 bg-black ${ASPECT_CLASS[aspectRatio]}`}
            >
              {videoUrl ? (
                <video
                  src={videoUrl}
                  controls
                  className="h-full w-full object-contain"
                />
              ) : (
                <div className="flex h-full items-center justify-center bg-[radial-gradient(circle_at_top,rgba(34,197,94,0.15),transparent_35%),linear-gradient(180deg,#020617_0%,#111827_100%)] px-10 text-center text-sm text-slate-400">
                  Rendered video will appear here in the main editor preview.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
