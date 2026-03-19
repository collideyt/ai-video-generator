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
  const selectedFiles = [
    ...assets.map((asset) => ({ name: asset.name, type: "Asset" })),
    ...(logo ? [{ name: logo.name, type: "Logo" }] : []),
    ...(music ? [{ name: music.name, type: "Music" }] : []),
  ];

  return (
    <div className="space-y-6">
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
          className="mt-3 w-full rounded-[20px] border border-dashed border-slate-700 bg-slate-950/60 px-4 py-4 text-sm file:mr-4 file:rounded-full file:border-0 file:bg-slate-800 file:px-4 file:py-2 file:text-slate-100"
        />
        {assets.length > 0 && (
          <p className="mt-2 text-xs text-slate-400">{assets.length} asset(s) selected</p>
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
            className="mt-3 w-full rounded-[20px] border border-slate-700 bg-slate-950/60 px-4 py-3 text-sm file:mr-4 file:rounded-full file:border-0 file:bg-slate-800 file:px-4 file:py-2 file:text-slate-100"
          />
          {logo && <p className="mt-2 text-xs text-slate-400">{logo.name}</p>}
        </div>
        <div>
          <p className="text-sm font-semibold">Background music</p>
          <input
            type="file"
            accept="audio/*"
            onChange={(event) =>
              onMusicChange(event.target.files ? event.target.files[0] : null)
            }
            className="mt-3 w-full rounded-[20px] border border-slate-700 bg-slate-950/60 px-4 py-3 text-sm file:mr-4 file:rounded-full file:border-0 file:bg-slate-800 file:px-4 file:py-2 file:text-slate-100"
          />
          {music && <p className="mt-2 text-xs text-slate-400">{music.name}</p>}
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        {selectedFiles.length > 0 ? (
          selectedFiles.map((file) => (
            <div
              key={`${file.type}-${file.name}`}
              className="glass-chip rounded-2xl px-4 py-3 text-sm text-slate-200"
            >
              <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                {file.type}
              </p>
              <p className="mt-1 truncate">{file.name}</p>
            </div>
          ))
        ) : (
          <div className="glass-chip col-span-full rounded-2xl px-4 py-5 text-sm text-slate-400">
            Upload clips, stills, brand assets, or audio to help the planner match scenes.
          </div>
        )}
      </div>
    </div>
  );
}
