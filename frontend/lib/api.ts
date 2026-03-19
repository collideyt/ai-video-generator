import type { VideoSpecs } from "@/components/SettingsPanel";

interface GenerateVideoRequest {
  script: string;
  assets: File[];
  logo: File | null;
  music: File | null;
  specs: VideoSpecs;
}

export interface GenerateVideoResponse {
  job_id: string;
  status_url: string;
  video_url: string | null;
}

export interface JobStatusResponse {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  current_step: string;
  steps: Array<{
    label: string;
    state: "pending" | "active" | "completed";
  }>;
  video_url: string | null;
  error: string | null;
  updated_at: string;
}

export interface LatestRenderResponse {
  job_id?: string;
  video_url: string | null;
  updated_at?: string;
  job_status?: JobStatusResponse | null;
}

export async function generateVideo({
  script,
  assets,
  logo,
  music,
  specs,
}: GenerateVideoRequest): Promise<GenerateVideoResponse> {
  const formData = new FormData();
  formData.append("script", script);
  formData.append("specs", JSON.stringify(specs));
  assets.forEach((asset) => formData.append("assets", asset));
  if (logo) {
    formData.append("logo", logo);
  }
  if (music) {
    formData.append("music", music);
  }

  const response = await fetch("http://localhost:8000/generate-video", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to start video generation");
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`http://localhost:8000/job-status/${jobId}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch job status");
  }

  return response.json();
}

export async function getLatestRender(): Promise<LatestRenderResponse> {
  const response = await fetch("http://localhost:8000/latest-render", {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch latest render");
  }

  return response.json();
}
