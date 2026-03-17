"use client";

interface VideoPreviewProps {
  videoUrl: string;
}

export default function VideoPreview({ videoUrl }: VideoPreviewProps) {
  if (!videoUrl) {
    return (
      <div className="flex h-56 items-center justify-center rounded-xl border border-dashed border-slate-700 text-sm text-slate-500">
        Rendered video will appear here.
      </div>
    );
  }

  return (
    <video
      src={videoUrl}
      controls
      className="h-56 w-full rounded-xl border border-slate-800 bg-black object-cover"
    />
  );
}
