import type { VideoSpecs } from "@/components/SettingsPanel";

interface GenerateVideoRequest {
  script: string;
  assets: File[];
  logo: File | null;
  music: File | null;
  specs: VideoSpecs;
}

interface GenerateVideoResponse {
  video_url: string;
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
    throw new Error("Failed to generate video");
  }

  return response.json();
}
