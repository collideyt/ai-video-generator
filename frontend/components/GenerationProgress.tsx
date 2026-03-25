"use client";

interface GenerationProgressProps {
  steps: string[];
  activeStepIndex: number;
  activeStepProgress: number;
}

export default function GenerationProgress({ steps, activeStepIndex, activeStepProgress }: GenerationProgressProps) {
  return (
    <section className="glass-panel rounded-3xl p-8">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-slate-100">Generating your video...</h2>
        <p className="mt-1 text-sm text-slate-400">Please do not close this page.</p>
      </div>
      <div className="space-y-4">
        {steps.map((step, index) => {
          const isCompleted = index < activeStepIndex;
          const isActive = index === activeStepIndex;
          return (
            <div key={step} className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className={`text-sm ${isCompleted || isActive ? "text-slate-200" : "text-slate-500"}`}>
                  {step}
                </span>
                <span className="text-xs text-slate-400">
                  {isCompleted ? "100%" : isActive ? `${Math.round(activeStepProgress)}%` : "0%"}
                </span>
              </div>
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
                <div
                  className={`h-full transition-all duration-300 ${isCompleted ? "bg-emerald-400" : "bg-indigo-500"} ${isActive ? "bg-indigo-400" : ""}`}
                  style={{ width: isCompleted ? "100%" : isActive ? `${activeStepProgress}%` : "0%" }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
