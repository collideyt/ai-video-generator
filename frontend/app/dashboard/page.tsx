import Link from "next/link";
import VideoPreview from "@/components/VideoPreview";

export default function DashboardPage() {
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
              <VideoPreview videoUrl="http://localhost:8000/outputs/final_video.mp4" />
            </div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6">
            <h2 className="text-lg font-semibold">Pipeline Status</h2>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>1. Script Analyzer: Ready</li>
              <li>2. Scene Planner: Ready</li>
              <li>3. Asset Matcher: Awaiting assets</li>
              <li>4. Voiceover: Optional</li>
              <li>5. Captions: Optional</li>
              <li>6. Timeline Builder: Ready</li>
              <li>7. Renderer: Ready</li>
            </ul>
            <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950/60 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">
                Tip
              </p>
              <p className="mt-2 text-sm text-slate-300">
                Use the upload studio to stage assets and kick off a new render.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
