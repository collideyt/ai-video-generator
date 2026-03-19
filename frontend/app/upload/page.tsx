"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

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
  const [aspectRatio, setAspectRatio] = useState<"16:9" | "9:16" | "1:1">("9:16");
  const [scenes, setScenes] = useState<SceneItem[]>([]);
  const [timelineOpen, setTimelineOpen] = useState(false);

  useEffect(() => {
    const originalOverflow = document.body.style.overflow;
    if (timelineOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = originalOverflow || "";
    }

    return () => {
      document.body.style.overflow = originalOverflow || "";
    };
  }, [timelineOpen]);

  return (
    <main className="min-h-screen bg-grid">
      <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col px-4 py-4 lg:px-6">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.28em] text-sky-300/80">
              Collide AI Video Editor
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-50 md:text-4xl">
              AI video workspace
            </h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-400">
              Build, preview, and refine short-form edits inside a production-style studio.
            </p>
          </div>
          <div className="glass-chip rounded-full px-4 py-2 text-sm text-slate-300">
            Editor mode
          </div>
        </div>

        <div className="flex flex-1 flex-col gap-4 xl:min-h-0 xl:flex-row">
          <Card className="xl:h-[calc(100vh-150px)] xl:w-[380px] xl:flex-none p-4">
            <div className="xl:h-full xl:overflow-y-auto xl:pr-1">
              <UploadForm
                onVideoReady={setVideoUrl}
                onAspectRatioChange={setAspectRatio}
                onScenesChange={setScenes}
              />
            </div>
          </Card>

          <div className="flex min-h-0 flex-1 flex-col gap-4">
            <div className="xl:sticky xl:top-6">
              <Card className="flex min-h-[520px] flex-1 flex-col justify-center p-6 xl:h-[calc(100vh-150px)]">
              <div className="mb-5 flex items-center justify-between gap-4">
                <div>
                  <h2 className="text-lg font-semibold text-slate-100">Preview Monitor</h2>
                  <p className="mt-1 text-sm text-slate-400">
                    Main render view with reel-safe framing and playback controls.
                  </p>
                </div>
                <div className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300">
                  {aspectRatio} output
                </div>
              </div>

              <VideoPreview videoUrl={videoUrl ?? ""} aspectRatio={aspectRatio} scenes={scenes} />
              </Card>
            </div>
          </div>
        </div>
      </div>

      {!timelineOpen && (
        <button
          type="button"
          onClick={() => setTimelineOpen(true)}
          className="fixed bottom-6 left-1/2 z-40 -translate-x-1/2 rounded-full bg-gradient-to-r from-sky-300 via-emerald-300 to-lime-200 px-5 py-3 text-sm font-semibold text-slate-950 shadow-[0_18px_50px_rgba(34,197,94,0.28)]"
        >
          Open Timeline
        </button>
      )}

      <AnimatePresence>
        {timelineOpen && (
          <>
            <motion.button
              type="button"
              aria-label="Close timeline"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setTimelineOpen(false)}
              className="fixed inset-0 z-40 bg-slate-950/45 backdrop-blur-sm"
            />

            <motion.div
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ duration: 0.32, ease: "easeOut" }}
              className="fixed bottom-0 left-0 right-0 z-50 h-[38vh] min-h-[280px]"
            >
              <div className="mx-auto h-full max-w-[1600px] px-4 pb-4 lg:px-6">
                <Card className="flex h-full flex-col rounded-t-[32px] rounded-b-[22px] p-5">
                  <div className="mb-4 flex items-center justify-between gap-4">
                    <div>
                      <p className="text-sm font-semibold text-slate-100">Scene Timeline</p>
                      <p className="text-xs text-slate-400">
                        Horizontal scene cards designed for editing review.
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300">
                        {scenes.length} scenes
                      </div>
                      <button
                        type="button"
                        onClick={() => setTimelineOpen(false)}
                        className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300"
                      >
                        Close
                      </button>
                    </div>
                  </div>

                  <div className="flex-1 overflow-x-auto overflow-y-hidden pb-2">
                    {scenes.length > 0 ? (
                      <div className="flex min-w-max gap-4">
                        {scenes.map((scene) => (
                          <div
                            key={scene.id}
                            className="w-[280px] flex-none rounded-[24px] border border-slate-800 bg-slate-950/70 p-4"
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div>
                                <p className="text-[11px] uppercase tracking-[0.26em] text-slate-500">
                                  Scene {scene.id}
                                </p>
                                <p className="mt-2 text-lg font-semibold text-slate-100">
                                  {scene.label}
                                </p>
                              </div>
                              <span className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300">
                                {scene.duration}s
                              </span>
                            </div>
                            <p className="mt-4 text-sm leading-6 text-slate-300">{scene.text}</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="rounded-[22px] border border-dashed border-slate-700 px-4 py-10 text-center text-sm text-slate-500">
                        Build a script to populate the timeline drawer.
                      </div>
                    )}
                  </div>
                </Card>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </main>
  );
}
