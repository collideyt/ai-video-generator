# Collide AI Video Editor

A full-stack AI video editor that turns a script and uploaded media into a finished MP4.

## Setup

### Backend

1. Install FFmpeg and make sure `ffmpeg` is on your PATH.
2. Create a virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
.venv\Scriptsctivate
pip install -r requirements.txt
```

3. (Optional) Set your OpenAI key for voiceover:

```bash
setx OPENAI_API_KEY "your-key"
```

4. Run the API:

```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

## Example Test Request

```bash
curl -X POST "http://localhost:8000/generate-video"   -F "script=Tired of slow workflows? Meet Collide."   -F "specs={"duration":30,"aspect_ratio":"9:16","captions":true,"voiceover":true}"   -F "assets=@C:\path\to\image1.jpg"   -F "assets=@C:\path\to\clip1.mp4"   -F "logo=@C:\path\to\logo.png"   -F "music=@C:\path\to\track.mp3"
```

Response:

```json
{
  "video_url": "/outputs/<job_id>/final_video.mp4"
}
```

## FFmpeg Command Examples

Trim clip:

```bash
ffmpeg -y -i input.mp4 -t 3 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" output.mp4
```

Concatenate scenes:

```bash
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy stitched.mp4
```

Overlay logo:

```bash
ffmpeg -y -i stitched.mp4 -i logo.png -filter_complex "overlay=W-w-40:H-h-40" final.mp4
```

Add captions:

```bash
ffmpeg -y -i stitched.mp4 -vf "subtitles=captions.srt" final.mp4
```

## Setup Instructions

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

FFmpeg will download automatically on first run.

### Frontend

```bash
cd frontend
npm install
npm run dev
```
