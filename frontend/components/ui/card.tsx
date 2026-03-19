import * as React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Card({ className = "", ...props }: CardProps) {
  return <div className={`glass-panel rounded-[28px] ${className}`} {...props} />;
}
