"use client";

import { useState } from "react";
import UploadForm from "@/components/UploadForm";
import VideoPreview from "@/components/VideoPreview";
import { Card } from "@/components/ui/card";

interface SceneItem {
  id: number;
  label: string;
  duration: number;
  text: string;
}

export default function UploadPage() {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [aspectRatio, setAspectRatio] = useState<"16:9" | "9:16" | "1:1">(
    "9:16"
  );
  const [scenes, setScenes] = useState<SceneItem[]>([]);

  return (
    <main className="min-h-screen bg-grid">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-sky-300/80">
              Collide AI Video Editor
            </p>
            <h1 className="mt-3 text-4xl font-semibold leading-tight md:text-5xl">
              Create short-form videos with a studio-grade AI workflow
            </h1>
            <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-300 md:text-base">
              Move from script to assets, style choices, and final render inside a
              production-style workspace built for fast iteration.
            </p>
          </div>
          <div className="glass-chip rounded-full px-4 py-2 text-sm text-slate-300">
            Preview + edit workspace
          </div>
        </div>

        <div className="mt-10 grid gap-6 xl:grid-cols-[1.05fr,0.95fr]">
          <Card className="p-6">
            <UploadForm
              onVideoReady={setVideoUrl}
              onAspectRatioChange={setAspectRatio}
              onScenesChange={setScenes}
            />
          </Card>
          <Card className="p-6">
            <div className="mb-5 flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-100">Preview + Edit</h2>
                <p className="mt-1 text-sm text-slate-400">
                  Vertical reel player, scene timeline, and script breakdown in one view.
                </p>
              </div>
              <div className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300">
                SaaS studio preview
              </div>
            </div>
            <div className="mt-4">
              <VideoPreview
                videoUrl={videoUrl ?? ""}
                aspectRatio={aspectRatio}
                scenes={scenes}
              />
            </div>
          </Card>
        </div>
      </div>
    </main>
  );
}
