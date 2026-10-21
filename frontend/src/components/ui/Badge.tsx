// frontend/src/components/ui/Badge.tsx
import React from "react";
import { RiskTier } from "@/lib/types";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  children: React.ReactNode;
  variant?: "low" | "moderate" | "elevated" | "neutral" | "info";
  tier?: RiskTier;
  size?: "sm" | "md";
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  className = "",
  variant = "neutral",
  tier,
  size = "md",
  ...props
}) => {
  const effectiveVariant = tier || variant;

  const variantStyles = {
    low: "bg-[#ECFDF5] text-[#065F46] border-[#A7F3D0]",
    moderate: "bg-[#FFFBEB] text-[#92400E] border-[#FDE68A]",
    elevated: "bg-[#FEF2F2] text-[#991B1B] border-[#FECACA]",
    neutral: "bg-[#F5F0E8] text-[#1F2937] border-[#E9E4D8]",
    info: "bg-[#EFF6FF] text-[#1E40AF] border-[#BFDBFE]",
  };

  const sizeStyles = {
    sm: "px-2 py-0.5 text-xs font-medium",
    md: "px-3 py-1 text-xs font-semibold",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border tracking-wide uppercase ${sizeStyles[size]} ${variantStyles[effectiveVariant] || variantStyles.neutral} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};
