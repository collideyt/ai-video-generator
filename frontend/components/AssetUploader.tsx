"use client";

import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

interface AssetUploaderProps {
  assets: File[];
  logo: File | null;
  music: File | null;
  onAssetsChange: (files: File[]) => void;
  onLogoChange: (file: File | null) => void;
  onMusicChange: (file: File | null) => void;
}

interface PreviewItem {
  name: string;
  type: string;
  url: string;
  kind: "image" | "video" | "audio" | "file";
}

function getPreviewKind(file: File): PreviewItem["kind"] {
  if (file.type.startsWith("image/")) {
    return "image";
  }
  if (file.type.startsWith("video/")) {
    return "video";
  }
  if (file.type.startsWith("audio/")) {
    return "audio";
  }
  return "file";
}

function PreviewModal({
  item,
  onClose,
}: {
  item: PreviewItem | null;
  onClose: () => void;
}) {
  return (
    <AnimatePresence>
      {item && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-6 backdrop-blur-md"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 16 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="glass-panel w-full max-w-3xl rounded-[28px] p-4"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="mb-4 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-slate-100">{item.name}</p>
                <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{item.type}</p>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="glass-chip rounded-full px-3 py-1 text-xs text-slate-300"
              >
                Close
              </button>
            </div>

            <div className="overflow-hidden rounded-[24px] border border-slate-800 bg-slate-950">
              {item.kind === "image" && (
                <img src={item.url} alt={item.name} className="max-h-[70vh] w-full object-contain" />
              )}
              {item.kind === "video" && (
                <video src={item.url} controls className="max-h-[70vh] w-full object-contain" />
              )}
              {item.kind === "audio" && (
                <div className="flex min-h-[220px] items-center justify-center p-8">
                  <audio src={item.url} controls className="w-full max-w-xl" />
                </div>
              )}
              {item.kind === "file" && (
                <div className="flex min-h-[220px] items-center justify-center p-8 text-sm text-slate-400">
                  Preview unavailable for this file type.
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function AssetCard({
  file,
  onPreview,
  onDelete,
}: {
  file: File;
  onPreview: (item: PreviewItem) => void;
  onDelete: () => void;
}) {
  const url = useMemo(() => URL.createObjectURL(file), [file]);
  const kind = getPreviewKind(file);

  useEffect(() => () => URL.revokeObjectURL(url), [url]);

  return (
    <div className="group relative overflow-hidden rounded-[18px] border border-slate-800 bg-slate-950/70">
      <div className="aspect-square bg-slate-900">
        {kind === "image" && (
          <img src={url} alt={file.name} className="h-full w-full object-cover transition duration-300 group-hover:scale-105" />
        )}
        {kind === "video" && (
          <video src={url} muted className="h-full w-full object-cover transition duration-300 group-hover:scale-105" />
        )}
        {kind !== "image" && kind !== "video" && (
          <div className="flex h-full items-center justify-center text-[11px] uppercase tracking-[0.24em] text-slate-500">
            {kind}
          </div>
        )}
      </div>

      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950 via-slate-950/75 to-transparent p-2.5">
        <p className="truncate text-xs font-medium text-slate-100">{file.name}</p>
      </div>

      <div className="absolute inset-0 flex items-start justify-between p-2 opacity-0 transition group-hover:opacity-100">
        <button
          type="button"
          onClick={() => onPreview({ name: file.name, type: kind, url, kind })}
          className="glass-chip rounded-full px-2.5 py-1 text-[11px] text-slate-100"
        >
          Preview
        </button>
        <button
          type="button"
          onClick={onDelete}
          className="rounded-full bg-rose-500/90 px-2.5 py-1 text-[11px] text-white"
        >
          Delete
        </button>
      </div>
    </div>
  );
}

function SmallFileButton({
  label,
  accept,
  file,
  onChange,
}: {
  label: string;
  accept: string;
  file: File | null;
  onChange: (file: File | null) => void;
}) {
  return (
    <label className="glass-chip cursor-pointer rounded-full px-3 py-2 text-xs text-slate-200">
      {file ? `${label}: ${file.name}` : label}
      <input
        type="file"
        accept={accept}
        onChange={(event) => onChange(event.target.files ? event.target.files[0] : null)}
        className="hidden"
      />
    </label>
  );
}

export default function AssetUploader({
  assets,
  logo,
  music,
  onAssetsChange,
  onLogoChange,
  onMusicChange,
}: AssetUploaderProps) {
  const [previewItem, setPreviewItem] = useState<PreviewItem | null>(null);

  return (
    <>
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-2.5">
          <label className="cursor-pointer rounded-full bg-gradient-to-r from-sky-300 via-emerald-300 to-lime-200 px-4 py-2 text-sm font-semibold text-slate-950">
            + Upload
            <input
              type="file"
              multiple
              accept="image/*,video/*"
              onChange={(event) =>
                onAssetsChange(event.target.files ? Array.from(event.target.files) : [])
              }
              className="hidden"
            />
          </label>

          <SmallFileButton
            label="Logo"
            accept="image/*"
            file={logo}
            onChange={onLogoChange}
          />

          <SmallFileButton
            label="Music"
            accept="audio/*"
            file={music}
            onChange={onMusicChange}
          />
        </div>

        {assets.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-4">
            {assets.map((asset, index) => (
              <AssetCard
                key={`${asset.name}-${index}`}
                file={asset}
                onPreview={setPreviewItem}
                onDelete={() =>
                  onAssetsChange(assets.filter((_, assetIndex) => assetIndex !== index))
                }
              />
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No assets yet — upload to start</p>
        )}
      </div>

      <PreviewModal item={previewItem} onClose={() => setPreviewItem(null)} />
    </>
  );
}
