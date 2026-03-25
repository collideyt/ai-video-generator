"use client";

import { startTransition, useEffect, useState } from "react";

import GenerationProgress from "../../components/GenerationProgress";
import PromptInput, { type PromptInputValue } from "../../components/PromptInput";
import RefinePanel from "../../components/RefinePanel";
import Timeline, { type TimelineScene } from "../../components/Timeline";
import VideoPreview from "../../components/VideoPreview";

type GenerationState = "idle" | "generating" | "completed";

interface GenerateVideoApiResponse {
  job_id?: string;
  video_url?: string | null;
}

interface JobStatusPayload {
  status: "queued" | "processing" | "completed" | "failed";
  current_step?: string;
  video_url?: string | null;
  error?: string | null;
}

const API_BASE = "http://localhost:8000";
const GENERATION_STEPS = [
  "Generating script",
  "Analyzing script",
  "Planning scenes",
  "Matching assets",
  "Generating voiceover",
  "Rendering video",
];

const initialPromptValue: PromptInputValue = {
  prompt: "",
  style: "cinematic",
  voice: "female",
  duration: "30s",
  images: [],
  videos: [],
  audio: null,
};

const wait = (delay: number) => new Promise((resolve) => setTimeout(resolve, delay));

function durationToSeconds(duration: PromptInputValue["duration"]): number {
  return Number.parseInt(duration.replace("s", ""), 10);
}

function normalizeVideoUrl(videoUrl: string | null | undefined): string | null {
  if (!videoUrl) {
    return null;
  }
  if (videoUrl.startsWith("http")) {
    return videoUrl;
  }
  return `${API_BASE}${videoUrl}`;
}

function mapBackendStep(currentStep?: string): number {
  if (!currentStep) return 0;
  const normalized = currentStep.toLowerCase();
  if (normalized.includes("generating script")) return 0;
  if (normalized.includes("understand") || normalized.includes("analyze")) return 1;
  if (normalized.includes("scene")) return 2;
  if (normalized.includes("asset") || normalized.includes("match")) return 3;
  if (normalized.includes("voice")) return 4;
  if (normalized.includes("render")) return 5;
  return 0;
}

function buildTimelineScenes(
  prompt: string,
  duration: PromptInputValue["duration"]
): TimelineScene[] {
  const totalDuration = durationToSeconds(duration);
  const perScene = Math.max(5, Math.round(totalDuration / 3));
  const cleanedPrompt = prompt.trim().replace(/\s+/g, " ");

  return [
    {
      id: 1,
      title: "Hook",
      durationLabel: `${perScene}s`,
      description: `Introducing the setting for ${cleanedPrompt.slice(0, 30)}...`,
    },
    {
      id: 2,
      title: "Content",
      durationLabel: `${Math.max(4, totalDuration - perScene - 5)}s`,
      description: `Dynamic showcase based on your prompt.`,
    },
    {
      id: 3,
      title: "CTA",
      durationLabel: `5s`,
      description: `Final call to action and logo resolve.`,
    },
  ];
}

async function submitGenerationRequest(
  promptValue: PromptInputValue
): Promise<GenerateVideoApiResponse> {
  const formData = new FormData();
  formData.append("prompt", promptValue.prompt);
  formData.append("style", promptValue.style);
  formData.append("voice", promptValue.voice);
  formData.append("duration", durationToSeconds(promptValue.duration).toString());

  promptValue.images.forEach((file: File) => formData.append("images", file));
  promptValue.videos.forEach((file: File) => formData.append("videos", file));
  if (promptValue.audio) {
    formData.append("audio", promptValue.audio);
  }

  const response = await fetch(`${API_BASE}/generate-video`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to start generation request.");
  }

  return (await response.json()) as GenerateVideoApiResponse;
}

async function pollJobForVideo(
  jobId: string,
  onStepUpdate: (stepIndex: number) => void
): Promise<string | null> {
  for (let attempt = 0; attempt < 300; attempt += 1) {
    let response: Response;
    try {
      response = await fetch(`${API_BASE}/job-status/${jobId}`, { cache: "no-store" });
    } catch {
      await wait(1600);
      continue;
    }

    if (response.ok) {
      const payload = (await response.json()) as JobStatusPayload;
      onStepUpdate(mapBackendStep(payload.current_step));

      if (payload.status === "failed") {
        throw new Error(payload.error ?? "Generation failed while rendering.");
      }
      if (payload.status === "completed") {
        return normalizeVideoUrl(payload.video_url);
      }
    }
    await wait(2000);
  }
  return null;
}

export default function GeneratePage() {
  const [generationState, setGenerationState] = useState<GenerationState>("idle");
  const [promptValue, setPromptValue] = useState<PromptInputValue>(initialPromptValue);
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [activeStepProgress, setActiveStepProgress] = useState(0);
  const [videoUrl, setVideoUrl] = useState("");
  const [scenes, setScenes] = useState<TimelineScene[]>([]);
  const [activeSceneId, setActiveSceneId] = useState(1);
  const [caption, setCaption] = useState("AI-generated caption overlay appears here.");
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (generationState !== "generating") return;
    const interval = setInterval(() => {
      setActiveStepProgress((currentProgress) => {
        const isLastStep = activeStepIndex >= GENERATION_STEPS.length - 1;
        const maxProgress = isLastStep ? 90 : 100;
        if (currentProgress >= maxProgress) {
          return maxProgress;
        }
        return Math.min(maxProgress, currentProgress + (Math.random() * 8 + 2));
      });
    }, 400);
    return () => clearInterval(interval);
  }, [generationState, activeStepIndex]);

  const handleGenerate = async () => {
    const trimmedPrompt = promptValue.prompt.trim();
    if (!trimmedPrompt) {
      setNotice("Please describe your video idea before generating.");
      return;
    }

    setNotice(null);
    setGenerationState("generating");
    setActiveStepIndex(0);
    setActiveStepProgress(5);
    setCaption(trimmedPrompt.slice(0, 100));

    try {
      const response = await submitGenerationRequest({ ...promptValue, prompt: trimmedPrompt });
      let resolvedVideoUrl = normalizeVideoUrl(response.video_url);

      if (!resolvedVideoUrl && response.job_id) {
        resolvedVideoUrl = await pollJobForVideo(response.job_id, (backendStep) => {
          setActiveStepIndex((prev) => Math.max(prev, backendStep));
          setActiveStepProgress((prev) => Math.max(prev, 15));
        });
      }

      if (!resolvedVideoUrl) {
        throw new Error("No video URL returned from backend.");
      }

      setActiveStepIndex(GENERATION_STEPS.length - 1);
      setActiveStepProgress(100);
      await wait(600);

      startTransition(() => {
        const builtScenes = buildTimelineScenes(trimmedPrompt, promptValue.duration);
        setScenes(builtScenes);
        setActiveSceneId(builtScenes[0]?.id ?? 1);
        setVideoUrl(resolvedVideoUrl);
        setGenerationState("completed");
      });
    } catch {
      setNotice("Video generation failed. Please try again.");
      startTransition(() => setGenerationState("idle"));
    }
  };

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0B0F19]">
      <div className="pointer-events-none absolute inset-0 bg-grid opacity-55" />
      <div className="pointer-events-none absolute -top-24 left-1/2 h-[28rem] w-[28rem] -translate-x-1/2 rounded-full bg-[radial-gradient(circle,rgba(129,140,248,0.3)_0%,rgba(129,140,248,0)_70%)] blur-2xl" />
      <div className="pointer-events-none absolute right-[-10rem] top-32 h-[24rem] w-[24rem] rounded-full bg-[radial-gradient(circle,rgba(56,189,248,0.3)_0%,rgba(56,189,248,0)_70%)] blur-3xl" />

      <div className="relative mx-auto flex min-h-screen w-full max-w-[1320px] flex-col px-4 pb-10 pt-8 md:px-8">
        <header className="mb-7 flex items-center justify-between">
          <p className="text-xs uppercase tracking-[0.3em] text-indigo-200/80">Collide AI Studio</p>
          <span className="glass-chip rounded-full px-3 py-1 text-xs text-slate-200">
            {generationState === "idle"
              ? "Ready"
              : generationState === "generating"
                ? "Generating"
                : "Completed"}
          </span>
        </header>

        <div className="mx-auto w-full max-w-5xl">
          <PromptInput
            value={promptValue}
            isGenerating={generationState === "generating"}
            onChange={setPromptValue}
            onGenerate={handleGenerate}
          />
          {notice && <p className="mt-3 text-center text-sm text-sky-300">{notice}</p>}
        </div>

        <section className="mt-8 flex-1">
          {generationState === "idle" && (
            <div className="glass-panel mx-auto flex min-h-[340px] max-w-5xl items-center justify-center rounded-3xl p-8 text-center">
              <div className="max-w-2xl">
                <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Instant Cinematic Output</p>
                <h2 className="mt-4 text-3xl font-semibold text-slate-100">
                  Preview, timeline, and controls appear right after generation.
                </h2>
                <p className="mt-3 text-sm text-slate-400">
                  Start with one prompt above. The AI will generate a script, build scenes, score music, add voiceover,
                  and render the final video automatically.
                </p>
              </div>
            </div>
          )}

          {generationState === "generating" && (
            <div className="mx-auto max-w-5xl">
              <GenerationProgress
                steps={GENERATION_STEPS}
                activeStepIndex={activeStepIndex}
                activeStepProgress={activeStepProgress}
              />
            </div>
          )}

          {generationState === "completed" && (
            <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_340px]">
              <div className="space-y-6">
                <VideoPreview
                  videoUrl={videoUrl}
                  aspectRatio="16:9"
                />
                <Timeline
                  scenes={scenes}
                  activeSceneId={activeSceneId}
                  onSceneSelect={setActiveSceneId}
                />
              </div>

              <RefinePanel
                scenes={scenes}
                initialPrompt={promptValue.prompt}
                initialStyle={promptValue.style}
                initialVoice={promptValue.voice}
              />
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
