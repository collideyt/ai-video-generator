"use client";

import { useEffect, useMemo, useState } from "react";

import AssetUploader from "@/components/AssetUploader";
import ScriptEditor from "@/components/ScriptEditor";
import SettingsPanel, { VideoSpecs } from "@/components/SettingsPanel";
import { Button } from "@/components/ui/button";
import { generateVideo, getJobStatus, type JobStatusResponse } from "@/lib/api";

interface SceneItem {
  id: number;
  label: string;
  duration: number;
  text: string;
}

interface UploadFormProps {
  onVideoReady: (url: string) => void;
  onAspectRatioChange?: (value: VideoSpecs["aspect_ratio"]) => void;
  onScenesChange?: (scenes: SceneItem[]) => void;
}

type StepId = 1 | 2 | 3 | 4;

const workflowSteps: Array<{ id: StepId; title: string; hint: string }> = [
  { id: 1, title: "Script", hint: "Narration and intent" },
  { id: 2, title: "Assets", hint: "Clips, logo, and music" },
  { id: 3, title: "Settings", hint: "Format and AI options" },
  { id: 4, title: "Generate", hint: "Launch the pipeline" },
];

const processingSteps = [
  "Analyzing script",
  "Planning scenes",
  "Matching assets",
  "Generating voiceover",
  "Rendering video",
] as const;

const sceneLabels = ["Hook", "Content", "Demo", "CTA"];

function buildScenes(script: string, duration: number): SceneItem[] {
  const blocks = script
    .split(/\n?\s*-{3,}\s*\n?/g)
    .map((block) => block.trim())
    .filter(Boolean);

  const headerRe = /^\[\s*([^|\]]+?)\s*\|\s*([^|\]]+?)(?:\s*\|\s*([^\]]+?))?\s*\]$/m;
  const timeRe = /^\s*(\d+(?:\.\d+)?)s?\s*-\s*(\d+(?:\.\d+)?)s?\s*$/i;

  const parsed = blocks
    .map((block, index) => {
      const lines = block.split("\n").map((line) => line.trim()).filter(Boolean);
      const header = lines[0]?.match(headerRe);
      if (!header) {
        return null;
      }

      const textLines: string[] = [];
      let currentField = "";
      let visual = "";

      for (const line of lines.slice(1)) {
        const fieldMatch = line.match(/^(TEXT|VISUAL|TRANSITION)\s*:\s*(.*)$/i);
        if (fieldMatch) {
          currentField = fieldMatch[1].toUpperCase();
          const value = fieldMatch[2].trim();
          if (currentField === "TEXT" && value) {
            textLines.push(value);
          }
          if (currentField === "VISUAL" && value) {
            visual = `${visual} ${value}`.trim();
          }
          continue;
        }

        if (currentField === "TEXT") {
          textLines.push(line);
        } else if (currentField === "VISUAL") {
          visual = `${visual} ${line}`.trim();
        }
      }

      const timeMatch = header[2].match(timeRe);
      const start = timeMatch ? Number(timeMatch[1]) : index * duration;
      const end = timeMatch ? Number(timeMatch[2]) : start + Math.max(1, duration);

      return {
        id: index + 1,
        label:
          header[1]
            .trim()
            .toLowerCase()
            .replace(/\b\w/g, (char) => char.toUpperCase()) ||
          sceneLabels[index] ||
          `Scene ${index + 1}`,
        duration: end - start,
        text: textLines.join(" ") || visual || "Scene details pending.",
      };
    })
    .filter((scene): scene is SceneItem => Boolean(scene));

  if (parsed.length > 0) {
    return parsed;
  }

  const chunks = script
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
  const source =
    chunks.length > 0 ? chunks : script.split(/(?<=[.!?])\s+/).filter(Boolean);
  const selected = source.slice(0, 4);

  return selected.map((text, index) => ({
    id: index + 1,
    label: sceneLabels[index] ?? `Scene ${index + 1}`,
    duration: Math.max(4, Math.round(duration / Math.max(selected.length, 1))),
    text,
  }));
}

export default function UploadForm({
  onVideoReady,
  onAspectRatioChange,
  onScenesChange,
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
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [activeStep, setActiveStep] = useState<StepId>(1);
  const [message, setMessage] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);

  const scenes = useMemo(() => buildScenes(script, specs.duration), [script, specs.duration]);

  useEffect(() => {
    onScenesChange?.(scenes);
  }, [onScenesChange, scenes]);

  useEffect(() => {
    if (!jobId || status !== "uploading") {
      return;
    }

    let active = true;
    const pollStatus = async () => {
      try {
        const next = await getJobStatus(jobId);
        if (!active) {
          return;
        }
        setJobStatus(next);
        setMessage(next.current_step || "Processing...");

        if (next.status === "completed" && next.video_url) {
          setStatus("success");
          setMessage("Render complete. Preview ready.");
          const videoUrl = next.video_url.startsWith("http")
            ? next.video_url
            : `http://localhost:8000${next.video_url}`;
          onVideoReady(videoUrl);
        } else if (next.status === "failed") {
          setStatus("error");
          setMessage(next.error || "Something went wrong while rendering.");
        }
      } catch {
        if (active) {
          setStatus("error");
          setMessage("Lost connection while checking render progress.");
        }
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, 1500);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [jobId, onVideoReady, status]);

  const canContinueFromScript = script.trim().length > 0;
  const canContinueFromAssets = assets.length > 0 || logo !== null || music !== null;
  const canContinueFromSettings = specs.duration >= 5;
  const canGenerate = canContinueFromScript && status !== "uploading";

  const liveStatuses = processingSteps.map((step) => {
    const matching = jobStatus?.steps?.find((item) => item.label === step);
    if (status === "success") {
      return { label: step, state: "done" as const };
    }
    if (status === "error") {
      return {
        label: step,
        state:
          matching?.state === "completed"
            ? ("done" as const)
            : matching?.state === "active"
              ? ("active" as const)
              : ("idle" as const),
      };
    }
    if (matching?.state === "completed") {
      return { label: step, state: "done" as const };
    }
    if (matching?.state === "active") {
      return { label: step, state: "active" as const };
    }
    return { label: step, state: "idle" as const };
  });

  const handleSubmit = async () => {
    setStatus("uploading");
    setJobStatus(null);
    setMessage("Queueing generation job...");

    try {
      const response = await generateVideo({ script, assets, logo, music, specs });
      setJobId(response.job_id);
      setMessage("Job started. Waiting for backend updates...");
    } catch {
      setStatus("error");
      setMessage("Something went wrong while starting the render.");
    }
  };

  return (
    <div className="space-y-8">
      <div className="rounded-[28px] border border-slate-800/80 bg-slate-950/50 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          {workflowSteps.map((step) => {
            const isActive = activeStep === step.id;
            const isComplete = activeStep > step.id;

            return (
              <button
                key={step.id}
                type="button"
                onClick={() => setActiveStep(step.id)}
                className={`flex min-w-[140px] flex-1 items-center gap-3 rounded-[22px] px-4 py-3 text-left transition ${
                  isActive ? "shadow-glow bg-sky-400/10" : "bg-slate-900/60 hover:bg-slate-900"
                }`}
              >
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold ${
                    isComplete
                      ? "bg-emerald-400 text-slate-950"
                      : isActive
                        ? "bg-sky-300 text-slate-950"
                        : "bg-slate-800 text-slate-300"
                  }`}
                >
                  {isComplete ? "\u2713" : step.id}
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-100">{step.title}</p>
                  <p className="text-xs text-slate-400">{step.hint}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {activeStep === 1 && (
        <div className="glass-panel rounded-[30px] p-6">
          <ScriptEditor value={script} onChange={setScript} />
          <div className="mt-6 flex justify-end">
            <Button type="button" disabled={!canContinueFromScript} onClick={() => setActiveStep(2)}>
              Continue to Assets
            </Button>
          </div>
        </div>
      )}

      {activeStep === 2 && (
        <div className="glass-panel rounded-[30px] p-6">
          <AssetUploader
            assets={assets}
            logo={logo}
            music={music}
            onAssetsChange={setAssets}
            onLogoChange={setLogo}
            onMusicChange={setMusic}
          />
          <div className="mt-6 flex items-center justify-between gap-3">
            <Button type="button" variant="secondary" onClick={() => setActiveStep(1)}>
              Back to Script
            </Button>
            <Button type="button" disabled={!canContinueFromAssets} onClick={() => setActiveStep(3)}>
              Continue to Settings
            </Button>
          </div>
        </div>
      )}

      {activeStep === 3 && (
        <div className="glass-panel rounded-[30px] p-6">
          <SettingsPanel
            value={specs}
            onChange={(nextSpecs) => {
              setSpecs(nextSpecs);
              onAspectRatioChange?.(nextSpecs.aspect_ratio);
            }}
          />
          <div className="mt-6 flex items-center justify-between gap-3">
            <Button type="button" variant="secondary" onClick={() => setActiveStep(2)}>
              Back to Assets
            </Button>
            <Button type="button" disabled={!canContinueFromSettings} onClick={() => setActiveStep(4)}>
              Review & Generate
            </Button>
          </div>
        </div>
      )}

      {activeStep === 4 && (
        <div className="glass-panel rounded-[30px] p-6">
          <div className="grid gap-6 xl:grid-cols-[1.1fr,0.9fr]">
            <div className="space-y-4">
              <div>
                <p className="text-sm uppercase tracking-[0.28em] text-slate-500">Ready to launch</p>
                <h3 className="mt-2 text-2xl font-semibold text-slate-50">
                  AI pipeline configured for a {specs.aspect_ratio} social cut
                </h3>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
                  Collide will analyze your script, map scenes against uploaded assets,
                  synthesize optional narration, and render a polished export.
                </p>
              </div>
              <div className="grid gap-3 md:grid-cols-3">
                <div className="glass-chip rounded-[22px] px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Assets</p>
                  <p className="mt-2 text-2xl font-semibold text-slate-100">{assets.length}</p>
                </div>
                <div className="glass-chip rounded-[22px] px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Runtime</p>
                  <p className="mt-2 text-2xl font-semibold text-slate-100">{specs.duration}s</p>
                </div>
                <div className="glass-chip rounded-[22px] px-4 py-4">
                  <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Scenes</p>
                  <p className="mt-2 text-2xl font-semibold text-slate-100">{scenes.length}</p>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-4">
                <Button type="button" onClick={handleSubmit} disabled={!canGenerate}>
                  {status === "uploading" ? "Rendering..." : "\u2728 Generate AI Video"}
                </Button>
                <Button type="button" variant="secondary" onClick={() => setActiveStep(3)}>
                  Back to Settings
                </Button>
                {message && (
                  <span className={`text-sm ${status === "error" ? "text-rose-400" : "text-slate-300"}`}>
                    {message}
                  </span>
                )}
              </div>
            </div>

            <div className="rounded-[26px] border border-slate-800 bg-slate-950/55 p-5">
              <p className="text-sm font-semibold text-slate-100">Live progress</p>
              <div className="mt-4 space-y-3">
                {liveStatuses.map((item) => (
                  <div
                    key={item.label}
                    className="flex items-center justify-between rounded-[18px] border border-slate-800 px-4 py-3 text-sm"
                  >
                    <span className="text-slate-300">{item.label}</span>
                    <span
                      className={`rounded-full px-3 py-1 text-xs ${
                        item.state === "done"
                          ? "bg-emerald-400/15 text-emerald-300"
                          : item.state === "active"
                            ? "bg-amber-400/15 text-amber-300"
                            : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {item.state === "done"
                        ? "\u2714 Complete"
                        : item.state === "active"
                          ? "\u23f3 In progress"
                          : "Waiting"}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {status === "uploading" && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-6 backdrop-blur-xl">
          <div className="glass-panel w-full max-w-4xl rounded-[36px] p-8">
            <p className="text-sm uppercase tracking-[0.32em] text-slate-500">Collide render pipeline</p>
            <h2 className="mt-3 text-3xl font-semibold text-gradient">
              Building your AI video experience
            </h2>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
              Your project is moving through the generation stack. These updates now come
              directly from the backend job status.
            </p>
            <div className="mt-3 rounded-full border border-slate-800 px-4 py-2 text-xs text-slate-400">
              {jobId ? `Job ${jobId.slice(0, 8)} in progress` : "Preparing job"}
            </div>
            <div className="mt-8 grid gap-4 md:grid-cols-2">
              {liveStatuses.map((step) => {
                const isDone = step.state === "done";
                const isActive = step.state === "active";

                return (
                  <div
                    key={step.label}
                    className={`rounded-[24px] border px-5 py-5 transition ${
                      isActive
                        ? "border-sky-400/50 bg-sky-400/10 shadow-glow"
                        : isDone
                          ? "border-emerald-400/30 bg-emerald-400/10"
                          : "border-slate-800 bg-slate-950/55"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-slate-100">{step.label}</p>
                        <p className="mt-1 text-xs text-slate-400">
                          {isDone ? "Completed" : isActive ? "Currently processing" : "Queued"}
                        </p>
                      </div>
                      <div
                        className={`h-10 w-10 rounded-full ${
                          isDone ? "bg-emerald-400" : isActive ? "animate-pulse bg-sky-300" : "bg-slate-800"
                        }`}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
