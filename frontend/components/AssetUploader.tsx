"use client";

interface AssetUploaderProps {
  assets: File[];
  logo: File | null;
  music: File | null;
  onAssetsChange: (files: File[]) => void;
  onLogoChange: (file: File | null) => void;
  onMusicChange: (file: File | null) => void;
}

export default function AssetUploader({
  assets,
  logo,
  music,
  onAssetsChange,
  onLogoChange,
  onMusicChange,
}: AssetUploaderProps) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-sm font-semibold">Assets</p>
        <p className="text-xs text-slate-400">
          Upload images and video clips used in the edit.
        </p>
        <input
          type="file"
          multiple
          accept="image/*,video/*"
          onChange={(event) =>
            onAssetsChange(event.target.files ? Array.from(event.target.files) : [])
          }
          className="mt-3 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm"
        />
        {assets.length > 0 && (
          <p className="mt-2 text-xs text-slate-400">
            {assets.length} asset(s) selected
          </p>
        )}
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <p className="text-sm font-semibold">Logo</p>
          <input
            type="file"
            accept="image/*"
            onChange={(event) =>
              onLogoChange(event.target.files ? event.target.files[0] : null)
            }
            className="mt-3 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm"
          />
          {logo && (
            <p className="mt-2 text-xs text-slate-400">{logo.name}</p>
          )}
        </div>
        <div>
          <p className="text-sm font-semibold">Background music</p>
          <input
            type="file"
            accept="audio/*"
            onChange={(event) =>
              onMusicChange(event.target.files ? event.target.files[0] : null)
            }
            className="mt-3 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm"
          />
          {music && (
            <p className="mt-2 text-xs text-slate-400">{music.name}</p>
          )}
        </div>
      </div>
    </div>
  );
}
