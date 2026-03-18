"use client";

import { useState } from "react";
import AssetUploader from "@/components/AssetUploader";
import ScriptEditor from "@/components/ScriptEditor";
import SettingsPanel, { VideoSpecs } from "@/components/SettingsPanel";
import { generateVideo } from "@/lib/api";

interface UploadFormProps {
  onVideoReady: (url: string) => void;
  onAspectRatioChange?: (value: VideoSpecs["aspect_ratio"]) => void;
}

export default function UploadForm({
  onVideoReady,
  onAspectRatioChange,
}: UploadFormProps) {
  const [script, setScript] = useState("");
  const [assets, setAssets] = useState<File[]>([]);
  const [logo, setLogo] = useState<File | null>(null);
  const [music, setMusic] = useState<File | null>(null);
  const [specs, setSpecs] = useState<VideoSpecs>({
    duration: 30,
    aspect_ratio: "9:16",
    captions: true,
    voiceover: true,
  });
  const [status, setStatus] = useState<
    "idle" | "uploading" | "success" | "error"
  >("idle");
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async () => {
    setStatus("uploading");
    setMessage("Generating video. This can take a few minutes...");
    try {
      const response = await generateVideo({ script, assets, logo, music, specs });
      setStatus("success");
      setMessage("Render complete. Preview ready.");
      const videoUrl = response.video_url.startsWith("http")
        ? response.video_url
        : `http://localhost:8000${response.video_url}`;
      onVideoReady(videoUrl);
    } catch (error) {
      setStatus("error");
      setMessage("Something went wrong while rendering.");
    }
  };

  return (
    <div className="space-y-6">
      <ScriptEditor value={script} onChange={setScript} />
      <AssetUploader
        assets={assets}
        logo={logo}
        music={music}
        onAssetsChange={setAssets}
        onLogoChange={setLogo}
        onMusicChange={setMusic}
      />
      <SettingsPanel
        value={specs}
        onChange={(nextSpecs) => {
          setSpecs(nextSpecs);
          onAspectRatioChange?.(nextSpecs.aspect_ratio);
        }}
      />
      <div className="flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!script || status === "uploading"}
          className="rounded-full bg-emerald-500 px-6 py-3 text-sm font-semibold text-slate-950 disabled:cursor-not-allowed disabled:bg-slate-600"
        >
          {status === "uploading" ? "Rendering..." : "Generate video"}
        </button>
        {message && (
          <span
            className={`text-sm ${
              status === "error" ? "text-rose-400" : "text-slate-300"
            }`}
          >
            {message}
          </span>
        )}
      </div>
      <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
        <h3 className="text-sm font-semibold">Pipeline progress</h3>
        <div className="mt-3 h-2 w-full rounded-full bg-slate-800">
          <div
            className={`h-2 rounded-full bg-emerald-500 transition-all ${
              status === "uploading" ? "w-2/3" : status === "success" ? "w-full" : "w-1/5"
            }`}
          />
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Scene analysis → matching → voiceover → captions → render
        </p>
      </div>
    </div>
  );
}
