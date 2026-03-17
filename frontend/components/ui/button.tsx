import * as React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  const base =
    "rounded-full px-6 py-3 text-sm font-semibold transition disabled:cursor-not-allowed";
  const styles =
    variant === "primary"
      ? "bg-emerald-500 text-slate-950 hover:bg-emerald-400 disabled:bg-slate-600"
      : "border border-slate-700 text-slate-100 hover:border-slate-500";

  return <button className={`${base} ${styles} ${className}`} {...props} />;
}
