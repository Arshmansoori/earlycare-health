// frontend/src/components/analytics/RiskGauge.tsx
"use client";

import React from "react";
import { RiskTier } from "@/lib/types";

interface RiskGaugeProps {
  score: number; // 0 to 100
  tier: RiskTier;
  title: string;
  subtitle?: string;
  className?: string;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({
  score,
  tier,
  title,
  subtitle,
  className = "",
}) => {
  const radius = 75;
  const strokeWidth = 14;
  const arcLength = Math.PI * radius; // ~235.62
  const clampedScore = Math.min(Math.max(score, 0), 100);
  const progressOffset = arcLength * (1 - clampedScore / 100);

  const tierColors = {
    low: {
      stroke: "#10B981",
      bg: "#ECFDF5",
      text: "#065F46",
      border: "#A7F3D0",
      label: "Low / Optimal",
    },
    moderate: {
      stroke: "#F59E0B",
      bg: "#FFFBEB",
      text: "#92400E",
      border: "#FDE68A",
      label: "Moderate Risk",
    },
    elevated: {
      stroke: "#EF4444",
      bg: "#FEF2F2",
      text: "#991B1B",
      border: "#FECACA",
      label: "Elevated Risk",
    },
  };

  const currentTheme = tierColors[tier] || tierColors.low;
  // Needle angle: -90deg at 0% to +90deg at 100%
  const needleAngle = -90 + (clampedScore / 100) * 180;

  return (
    <div
      className={`flex flex-col items-center bg-white rounded-3xl p-6 border border-[#E9E4D8] shadow-warm ${className}`}
    >
      <div className="text-center mb-3">
        <h3 className="text-base font-bold text-[#1F2937] tracking-tight">{title}</h3>
        {subtitle && <p className="text-xs text-[#6B7280] mt-0.5">{subtitle}</p>}
      </div>

      <div className="relative w-52 h-32 flex items-center justify-center">
        <svg viewBox="0 0 200 120" className="w-full h-full overflow-visible">
          {/* Background Track Arc */}
          <path
            d="M 25 100 A 75 75 0 0 1 175 100"
            fill="none"
            stroke="#E9E4D8"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />

          {/* Active Progress Arc */}
          <path
            d="M 25 100 A 75 75 0 0 1 175 100"
            fill="none"
            stroke={currentTheme.stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={arcLength}
            strokeDashoffset={progressOffset}
            className="transition-all duration-1000 ease-out"
          />

          {/* Pivot Center Pin */}
          <circle cx="100" cy="100" r="5" fill="#1F2937" />

          {/* Animated Needle Pointer */}
          <line
            x1="100"
            y1="100"
            x2="100"
            y2="32"
            stroke="#1F2937"
            strokeWidth="3"
            strokeLinecap="round"
            style={{
              transformOrigin: "100px 100px",
              transform: `rotate(${needleAngle}deg)`,
              transition: "transform 1s cubic-bezier(0.34, 1.56, 0.64, 1)",
            }}
          />
        </svg>

        {/* Center Numerical Score */}
        <div className="absolute bottom-0 flex flex-col items-center">
          <span className="text-3xl font-extrabold tracking-tight text-[#1F2937]">
            {clampedScore.toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Semantic Tier Badge */}
      <div
        className="mt-4 px-3.5 py-1 rounded-full text-xs font-bold tracking-wide uppercase border shadow-sm"
        style={{
          backgroundColor: currentTheme.bg,
          color: currentTheme.text,
          borderColor: currentTheme.border,
        }}
      >
        {currentTheme.label}
      </div>
    </div>
  );
};
