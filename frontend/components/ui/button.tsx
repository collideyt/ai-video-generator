import * as React from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function Button({
  variant = "primary",
  className = "",
  ...props
}: ButtonProps) {
  const base =
    "rounded-full px-6 py-3 text-sm font-semibold transition duration-300 disabled:cursor-not-allowed";
  const styles =
    variant === "primary"
      ? "shadow-glow bg-gradient-to-r from-sky-300 via-emerald-300 to-lime-200 text-slate-950 hover:-translate-y-0.5 hover:scale-[1.01] hover:shadow-[0_18px_50px_rgba(34,197,94,0.24)] disabled:transform-none disabled:bg-slate-600"
      : "glass-chip border border-slate-700/70 text-slate-100 hover:-translate-y-0.5 hover:border-slate-500 hover:bg-slate-800/70";

  return <button className={`${base} ${styles} ${className}`} {...props} />;
}
