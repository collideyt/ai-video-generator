"use client";

interface VideoPreviewProps {
  videoUrl: string;
  aspectRatio?: "16:9" | "9:16" | "1:1";
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
  if (!videoUrl) {
    return (
      <div className="w-full max-w-sm">
        <div
          className={`flex items-center justify-center rounded-xl border border-dashed border-slate-700 text-sm text-slate-500 ${ASPECT_CLASS[aspectRatio]}`}
        >
          Rendered video will appear here.
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-sm">
      <div
        className={`overflow-hidden rounded-xl border border-slate-800 bg-black ${ASPECT_CLASS[aspectRatio]}`}
      >
        <video
          src={videoUrl}
          controls
          className="h-full w-full object-contain"
        />
      </div>
    </div>
  );
}
