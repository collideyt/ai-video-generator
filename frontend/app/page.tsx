import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function Home() {
  return (
    <main className="min-h-screen bg-grid">
      <div className="mx-auto max-w-6xl px-6 py-16">
        <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-10 shadow-2xl">
          <div className="flex flex-col gap-6">
            <p className="text-sm uppercase tracking-[0.3em] text-emerald-400">
              Collide AI Video Editor
            </p>
            <h1 className="text-4xl font-semibold leading-tight md:text-5xl">
              Auto-edit studio-quality videos from a script and your media assets.
            </h1>
            <p className="max-w-2xl text-lg text-slate-300">
              Upload a script, visuals, logo, and music. Collide splits scenes,
              generates voiceover and captions, builds a timeline, and renders a
              final video with FFmpeg.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link href="/dashboard">
                <Button>Go to Dashboard</Button>
              </Link>
              <Link href="/upload">
                <Button variant="secondary">Start a Project</Button>
              </Link>
            </div>
          </div>
        </div>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            {
              title: "Scene Intelligence",
              body: "Script-aware scene splitting and asset matching so every beat lands on time.",
            },
            {
              title: "Studio Automation",
              body: "Voiceover, captions, and motion graphics layered automatically in the render pipeline.",
            },
            {
              title: "Production Ready",
              body: "Export an MP4 with watermark, music, transitions, and captions in one click.",
            },
          ].map((card) => (
            <Card key={card.title} className="p-6">
              <h3 className="text-lg font-semibold">{card.title}</h3>
              <p className="mt-2 text-sm text-slate-300">{card.body}</p>
            </Card>
          ))}
        </div>
      </div>
    </main>
  );
}
