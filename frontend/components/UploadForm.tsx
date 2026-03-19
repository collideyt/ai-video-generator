"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

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

function Section({
  title,
  subtitle,
  defaultOpen = false,
  children,
}: {
  title: string;
  subtitle: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="glass-panel rounded-[28px] p-4">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex w-full items-center justify-between gap-4 text-left"
      >
        <div>
          <p className="text-sm font-semibold text-slate-100">{title}</p>
          <p className="text-xs text-slate-400">{subtitle}</p>
        </div>
        <div className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300">
          {open ? "Hide" : "Show"}
        </div>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="overflow-hidden"
          >
            <div className="pt-4">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
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

  const liveStatuses = processingSteps.map((step) => {
    const matching = jobStatus?.steps?.find((item) => item.label === step);
    if (status === "success") {
      return { label: step, state: "done" as const };
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
    setMessage("Uploading assets to backend...");

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
    <div className="space-y-4">
      <Section title="Script" subtitle="Structure the story and prompts for the AI editor." defaultOpen>
        <ScriptEditor value={script} onChange={setScript} />
      </Section>

      <Section title="Assets" subtitle="Manage visual uploads, logo, and soundtrack.">
        <AssetUploader
          assets={assets}
          logo={logo}
          music={music}
          onAssetsChange={setAssets}
          onLogoChange={setLogo}
          onMusicChange={setMusic}
        />
      </Section>

      <Section title="Settings" subtitle="Configure aspect ratio, runtime, and AI services.">
        <SettingsPanel
          value={specs}
          onChange={(nextSpecs) => {
            setSpecs(nextSpecs);
            onAspectRatioChange?.(nextSpecs.aspect_ratio);
          }}
        />
      </Section>

      <div className="glass-panel rounded-[28px] p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold text-slate-100">Generate</p>
            <p className="text-xs text-slate-400">
              Launch the backend pipeline and monitor live status.
            </p>
          </div>
          <Button
            type="button"
            onClick={handleSubmit}
            disabled={!script.trim() || status === "uploading"}
            className="px-4 py-2 text-sm shadow-[0_14px_35px_rgba(34,197,94,0.18)] min-w-[132px]"
          >
            {status === "uploading" ? "Rendering..." : "Generate"}
          </Button>
        </div>

        <div className="mt-4 space-y-2">
          {liveStatuses.map((item) => (
            <div
              key={item.label}
              className="flex items-center justify-between rounded-[16px] border border-slate-800/90 bg-slate-950/35 px-3.5 py-2.5 text-sm"
            >
              <span className="text-slate-300">{item.label}</span>
              <span
                className={`rounded-full px-2.5 py-1 text-[11px] ${
                  item.state === "done"
                    ? "bg-emerald-400/15 text-emerald-300"
                    : item.state === "active"
                      ? "bg-sky-400/15 text-sky-300"
                      : "bg-slate-800 text-slate-400"
                }`}
              >
                {item.state === "done" ? "Done" : item.state === "active" ? "Live" : "Idle"}
              </span>
            </div>
          ))}
        </div>

        {message && (
          <p className={`mt-4 text-sm ${status === "error" ? "text-rose-400" : "text-slate-300"}`}>
            {message}
          </p>
        )}
      </div>
    </div>
  );
}
