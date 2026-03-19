"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import VideoPreview from "@/components/VideoPreview";
import { getLatestRender, type JobStatusResponse } from "@/lib/api";

export default function DashboardPage() {
  const [videoUrl, setVideoUrl] = useState("");
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);

  useEffect(() => {
    let active = true;

    const loadLatest = async () => {
      try {
        const latest = await getLatestRender();
        if (!active) {
          return;
        }
        setVideoUrl(
          latest.video_url
            ? latest.video_url.startsWith("http")
              ? latest.video_url
              : `http://localhost:8000${latest.video_url}`
            : ""
        );
        setJobStatus(latest.job_status ?? null);
      } catch {
        if (active) {
          setVideoUrl("");
          setJobStatus(null);
        }
      }
    };

    loadLatest();
    const interval = setInterval(loadLatest, 4000);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <main className="min-h-screen bg-slate-950">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-slate-400">
              Dashboard
            </p>
            <h1 className="text-3xl font-semibold">Project Overview</h1>
          </div>
          <Link
            href="/upload"
            className="rounded-full bg-emerald-500 px-5 py-2 text-sm font-semibold text-slate-950 hover:bg-emerald-400"
          >
            New Generation
          </Link>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-lg font-semibold">Latest Render</h2>
            <p className="mt-2 text-sm text-slate-400">
              Preview the most recent video output.
            </p>
            <div className="mt-4">
              <VideoPreview videoUrl={videoUrl} />
            </div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-lg font-semibold">Pipeline Status</h2>
            <div className="mt-4 space-y-3 text-sm">
              {jobStatus?.steps?.length ? (
                jobStatus.steps.map((step, index) => (
                  <div
                    key={step.label}
                    className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-4 py-3"
                  >
                    <span className="text-slate-200">
                      {index + 1}. {step.label}
                    </span>
                    <span
                      className={`rounded-full px-3 py-1 text-xs ${
                        step.state === "completed"
                          ? "bg-emerald-400/15 text-emerald-300"
                          : step.state === "active"
                            ? "bg-sky-400/15 text-sky-300"
                            : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {step.state === "completed"
                        ? "Complete"
                        : step.state === "active"
                          ? "In progress"
                          : "Waiting"}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-slate-400">No completed render found yet.</p>
              )}
            </div>
            <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">
                Tip
              </p>
              <p className="mt-2 text-sm text-slate-300">
                The dashboard refreshes automatically and follows the latest finished render.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
