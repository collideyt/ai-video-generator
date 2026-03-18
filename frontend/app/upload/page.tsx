"use client";

import { useState } from "react";
import UploadForm from "@/components/UploadForm";
import VideoPreview from "@/components/VideoPreview";

export default function UploadPage() {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [aspectRatio, setAspectRatio] = useState<"16:9" | "9:16" | "1:1">(
    "9:16"
  );

  return (
    <main className="min-h-screen bg-slate-950">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-slate-400">
              Upload Studio
            </p>
            <h1 className="text-3xl font-semibold">Generate a new video</h1>
          </div>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[1.3fr,0.7fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
            <UploadForm
              onVideoReady={setVideoUrl}
              onAspectRatioChange={setAspectRatio}
            />
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-lg font-semibold">Preview</h2>
            <p className="mt-2 text-sm text-slate-400">
              Rendered output will appear here once the pipeline completes.
            </p>
            <div className="mt-4">
              <VideoPreview
                videoUrl={videoUrl ?? ""}
                aspectRatio={aspectRatio}
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
